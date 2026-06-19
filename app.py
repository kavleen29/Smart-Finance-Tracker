from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import os
from database import (init_db, add_transaction, get_transactions,
                      delete_transaction, set_budget, get_budget,
                      get_summary, get_category_breakdown, import_from_csv)
from ai_insights import get_ai_insights

app = Flask(__name__)

CATEGORIES = [
    "Food & Dining", "Rent", "Shopping", "Entertainment",
    "Sports & Fitness", "Medical", "Electricity", "Cleaning",
    "Transport", "Education", "Subscriptions", "Miscellaneous"
]

@app.route("/")
def index():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    transactions = get_transactions(month)
    summary = get_summary(month)
    budget = get_budget(month)
    category_breakdown = get_category_breakdown(month)
    total_income = summary.get("income", 0)
    total_expense = summary.get("expense", 0)
    saved = total_income - total_expense
    savings_rate = round((saved / total_income * 100), 1) if total_income > 0 else 0
    budget_used = round((total_expense / budget * 100), 1) if budget > 0 else 0
    return render_template("index.html",
        month=month,
        transactions=transactions,
        summary=summary,
        budget=budget,
        category_breakdown=category_breakdown,
        total_income=total_income,
        total_expense=total_expense,
        saved=saved,
        savings_rate=savings_rate,
        budget_used=budget_used,
        categories=CATEGORIES
    )

@app.route("/add", methods=["POST"])
def add():
    data = request.form
    add_transaction(
        type=data["type"],
        amount=float(data["amount"]),
        category=data["category"],
        description=data["description"],
        date=data["date"]
    )
    return redirect(url_for("index", month=data["date"][:7]))

@app.route("/delete/<int:id>")
def delete(id):
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    delete_transaction(id)
    return redirect(url_for("index", month=month))

@app.route("/set-budget", methods=["POST"])
def update_budget():
    data = request.form
    set_budget(data["month"], float(data["budget"]))
    return redirect(url_for("index", month=data["month"]))

@app.route("/api/insights")
def insights():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    summary = get_summary(month)
    budget = get_budget(month)
    category_breakdown = get_category_breakdown(month)
    if summary.get("income", 0) == 0 and summary.get("expense", 0) == 0:
        return jsonify({"error": "No data for this month yet"})
    try:
        result = get_ai_insights(summary, category_breakdown, budget, month)
        return jsonify({"insights": result})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/import", methods=["POST"])
def import_csv():
    month = request.form.get("month", datetime.now().strftime("%Y-%m"))
    if "file" not in request.files:
        return redirect(url_for("index", month=month))
    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("index", month=month))
    filepath = f"temp_{file.filename}"
    file.save(filepath)
    success, message = import_from_csv(filepath)
    os.remove(filepath)
    return redirect(url_for("index", month=month))

@app.route("/api/chart-data")
def chart_data():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    breakdown = get_category_breakdown(month)
    labels = [item["category"] for item in breakdown]
    values = [item["total"] for item in breakdown]
    return jsonify({"labels": labels, "values": values})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
