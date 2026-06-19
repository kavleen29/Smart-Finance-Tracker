from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_ai_insights(summary, category_breakdown, budget, month):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    total_income = summary.get("income", 0)
    total_expense = summary.get("expense", 0)
    saved = total_income - total_expense
    savings_rate = (saved / total_income * 100) if total_income > 0 else 0

    category_text = ""
    for item in category_breakdown:
        category_text += f"- {item['category']}: Rs.{item['total']:,.0f}\n"

    prompt = f"""
You are a personal finance advisor for an Indian student/young professional.
Analyze this monthly financial data and give smart, friendly, actionable insights.

Month: {month}
Total Budget Set: Rs.{budget:,.0f}
Total Income: Rs.{total_income:,.0f}
Total Spent: Rs.{total_expense:,.0f}
Total Saved: Rs.{saved:,.0f}
Savings Rate: {savings_rate:.1f}%

Spending by category:
{category_text}

Give exactly 4 insights in this JSON format and nothing else, no extra text:
{{
  "insights": [
    {{"type": "warning", "icon": "alert", "message": "..."}},
    {{"type": "success", "icon": "trending-up", "message": "..."}},
    {{"type": "tip", "icon": "bulb", "message": "..."}},
    {{"type": "prediction", "icon": "chart", "message": "..."}}
  ]
}}

Rules:
- Use Rs. for all amounts
- Be specific with numbers from the data
- Keep each message under 20 words
- Be encouraging and practical
- Think about Indian lifestyle and expenses
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    response_text = response.text.strip()
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    result = json.loads(response_text)
    return result["insights"]
