# 💰 FinTrack — Smart Personal Finance Tracker

A full-stack web application to track income, expenses and savings with AI-powered financial insights built for Indian users with INR support.

🔗 **Live Demo:** [finance-tracker-fw9c.onrender.com](https://finance-tracker-fw9c.onrender.com)

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-black)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🔐 **User Authentication** — secure signup/login, each users data stays private
- 💸 **Income & Expense Tracking** — categorized entries (Food, Rent, Shopping, Medical, etc.)
- 🎯 **Monthly Budget Goals** — set budgets and track progress per category
- 📊 **Visual Analytics** — spending breakdown charts and category-wise insights
- 🤖 **AI-Powered Insights** — personalized financial tips using Google Gemini
- 📂 **CSV Import** — bulk import transactions from bank statements
- 🌗 **Dark/Light Theme** — toggle between themes
- 🇮🇳 **INR-first design** — built around Indian spending categories and currency

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite |
| Authentication | Flask-Login, Werkzeug (password hashing) |
| AI | Google Gemini API |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Deployment | Render |

---

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.11+
- A free [Gemini API key](https://aistudio.google.com/)

### Installation

```bash
# Clone the repo
git clone https://github.com/kavleen29/Smart-Finance-Tracker.git
cd Smart-Finance-Tracker

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo "GEMINI_API_KEY=your_key_here" > .env

# Run the app
python3 app.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## 📁 Project Structure
---

## 🔮 Future Improvements

- [ ] Bank/UPI integration via Account Aggregator APIs
- [ ] SMS-based transaction auto-detection
- [ ] Multi-currency support
- [ ] Export reports as PDF

---

## 👤 Author

**Kavleen Kaur**
B.Sc. Applied Statistics & Data Science 

---

## 📄 License

This project is licensed under the MIT License.
