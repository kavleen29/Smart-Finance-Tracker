from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from database import (init_db, add_transaction, get_transactions,
                      delete_transaction, set_budget, get_budget,
                      get_summary, get_category_breakdown, import_from_csv,
                      create_user, get_user_by_username, get_user_by_id)
from ai_insights import get_ai_insights

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-this")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

CATEGORIES = [
    "Food & Dining", "Rent", "Shopping", "Entertainment",
    "Sports & Fitness", "Medical", "Electricity", "Cleaning",
    "Transport", "Education", "Subscriptions", "Miscellaneous"
]

class User(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict["id"]
        self.username = user_dict["username"]

@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(int(user_id))
    return User(user) if user else None

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        if len(username) < 3:
            flash("Username must be at least 3 characters")
            return redirect(url_for("signup"))
        if len(password) < 4:
            flash("Password must be at least 4 characters")
            return redirect(url_for("signup"))
        existing = get_user_by_username(username)
        if existing:
            flash("Username already taken")
            return redirect(url_for("signup"))
        password_hash = generate_password_hash(password)
        user_id = create_user(username, password_hash)
        user = get_user_by_id(user_id)
        login_user(User(user))
        return redirect(url_for("index"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            login_user(User(user))
            return redirect(url_for("index"))
        flash("Invalid username or password")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    transactions = get_transactions(current_user.id, month)
    summary = get_summary(current_user.id, month)
    budget = get_budget(current_user.id, month)
    category_breakdown = get_category_breakdown(current_user.id, month)
    total_income = summary.get("income", 0)
    total_expense = summary.get("expense", 0)
    saved = total_income - total_expense
    savings_rate = round((saved / total_income * 100), 1) if total_income > 0 else 0
    budget_used = round((total_expense / budget * 100), 1) if budget > 0 else 0
    return render_template("index.html",
        month=month,
        username=current_user.username,
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
@login_required
def add():
    data = request.form
    add_transaction(
        user_id=current_user.id,
        type=data["type"],
        amount=float(data["amount"]),
        category=data["category"],
        description=data["description"],
        date=data["date"]
    )
    return redirect(url_for("index", month=data["date"][:7]))

@app.route("/delete/<int:id>")
@login_required
def delete(id):
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    delete_transaction(current_user.id, id)
    return redirect(url_for("index", month=month))

@app.route("/set-budget", methods=["POST"])
@login_required
def update_budget():
    data = request.form
    set_budget(current_user.id, data["month"], float(data["budget"]))
    return redirect(url_for("index", month=data["month"]))

@app.route("/api/insights")
@login_required
def insights():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    summary = get_summary(current_user.id, month)
    budget = get_budget(current_user.id, month)
    category_breakdown = get_category_breakdown(current_user.id, month)
    if summary.get("income", 0) == 0 and summary.get("expense", 0) == 0:
        return jsonify({"error": "No data for this month yet"})
    try:
        result = get_ai_insights(summary, category_breakdown, budget, month)
        return jsonify({"insights": result})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/import", methods=["POST"])
@login_required
def import_csv():
    month = request.form.get("month", datetime.now().strftime("%Y-%m"))
    if "file" not in request.files:
        return redirect(url_for("index", month=month))
    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("index", month=month))
    filepath = f"temp_{current_user.id}_{file.filename}"
    file.save(filepath)
    success, message = import_from_csv(current_user.id, filepath)
    os.remove(filepath)
    return redirect(url_for("index", month=month))

@app.route("/api/chart-data")
@login_required
def chart_data():
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    breakdown = get_category_breakdown(current_user.id, month)
    labels = [item["category"] for item in breakdown]
    values = [item["total"] for item in breakdown]
    return jsonify({"labels": labels, "values": values})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
