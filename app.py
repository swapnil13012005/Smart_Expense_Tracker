from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import datetime
import csv
import io
import os
import re
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CSV_FILE = os.environ.get("EXPENSES_CSV", "expenses.csv")
CATEGORIES = ["food", "clothing", "travel", "books", "entertainment", "utilities", "other"]

class Expense:
    def __init__(self, amount, category, description, date=None):
        self.amount = float(amount)
        self.category = category
        self.description = description
        self.date = date or datetime.date.today()

class ExpenseTracker:
    def __init__(self):
        self.allowed_categories = CATEGORIES
        self.expenses = self.load_expenses()

    def load_expenses(self):
        items = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, newline="", encoding="utf-8") as file:
                for row in csv.DictReader(file):
                    try:
                        items.append(Expense(
                            row["amount"], row["category"].lower(),
                            row["description"], datetime.date.fromisoformat(row["date"])
                        ))
                    except (ValueError, KeyError):
                        continue
        return items

    def save_expenses(self):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["date", "amount", "category", "description"])
            writer.writeheader()
            for item in self.expenses:
                writer.writerow({
                    "date": item.date.isoformat(), "amount": item.amount,
                    "category": item.category, "description": item.description
                })

    def add_expense(self, amount, category, description, date=None):
        try:
            amount = float(amount)
            category = (category or "").lower()
            description = (description or "").strip()
            expense_date = datetime.date.fromisoformat(date) if date else datetime.date.today()
        except (ValueError, TypeError):
            return "Enter a valid amount and date."
        if amount <= 0:
            return "Amount must be greater than zero."
        if category not in self.allowed_categories:
            return "Choose a valid category."
        if not description:
            return "Description cannot be empty."
        self.expenses.append(Expense(amount, category, description, expense_date))
        self.save_expenses()
        return None

    def analytics(self):
        today = datetime.date.today()
        this_month = [e for e in self.expenses if e.date.year == today.year and e.date.month == today.month]
        previous_month_date = (today.replace(day=1) - datetime.timedelta(days=1))
        previous_month = [e for e in self.expenses if e.date.year == previous_month_date.year and e.date.month == previous_month_date.month]
        category_totals = defaultdict(float)
        monthly_totals = defaultdict(float)
        for e in self.expenses:
            category_totals[e.category] += e.amount
            monthly_totals[e.date.strftime("%Y-%m")] += e.amount
        month_total = sum(e.amount for e in this_month)
        previous_total = sum(e.amount for e in previous_month)
        change = ((month_total - previous_total) / previous_total * 100) if previous_total else None
        return {
            "total": round(sum(e.amount for e in self.expenses), 2),
            "month_total": round(month_total, 2),
            "previous_month_total": round(previous_total, 2),
            "month_change_percent": round(change, 1) if change is not None else None,
            "transaction_count": len(self.expenses),
            "average": round(sum(e.amount for e in self.expenses) / len(self.expenses), 2) if self.expenses else 0,
            "category_totals": {k: round(v, 2) for k, v in sorted(category_totals.items())},
            "monthly_totals": {k: round(v, 2) for k, v in sorted(monthly_totals.items())[-6:]},
            "recent": [self.to_dict(e, i) for i, e in reversed(list(enumerate(self.expenses[-8:], start=max(0, len(self.expenses)-8))))],
        }

    @staticmethod
    def to_dict(e, index):
        return {"id": index, "date": e.date.isoformat(), "amount": round(e.amount, 2),
                "category": e.category, "description": e.description}

tracker = ExpenseTracker()

@app.route("/")
def index():
    return render_template("index.html", categories=tracker.allowed_categories)

@app.route("/add", methods=["POST"])
def add():
    error = tracker.add_expense(request.form.get("amount"), request.form.get("category"),
                                request.form.get("description"), request.form.get("date"))
    if error:
        return error, 400
    return redirect(url_for("index"))

@app.route("/report")
def report():
    category_summary = tracker.analytics()["category_totals"]
    return render_template("report.html", report={
        "total_expenses": tracker.analytics()["total"],
        "category_summary": category_summary,
        "all_expenses": tracker.expenses
    })

@app.route("/edit/<int:expense_id>", methods=["POST"])
def edit(expense_id):
    if expense_id < 0 or expense_id >= len(tracker.expenses):
        return "Expense not found.", 404
    old = tracker.expenses[expense_id]
    try:
        amount = float(request.form.get("amount"))
        date = datetime.date.fromisoformat(request.form.get("date"))
    except (ValueError, TypeError):
        return "Enter a valid amount and date.", 400
    category = (request.form.get("category") or "").lower()
    description = (request.form.get("description") or "").strip()
    if amount <= 0 or category not in CATEGORIES or not description:
        return "Please check the expense details.", 400
    tracker.expenses[expense_id] = Expense(amount, category, description, date)
    tracker.save_expenses()
    return redirect(url_for("index"))

@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    if expense_id < 0 or expense_id >= len(tracker.expenses):
        return "Expense not found.", 404
    tracker.expenses.pop(expense_id)
    tracker.save_expenses()
    return redirect(url_for("index"))

@app.route("/api/analytics")
def api_analytics():
    data = tracker.analytics()
    data["expenses"] = [tracker.to_dict(e, i) for i, e in reversed(list(enumerate(tracker.expenses)))]
    return jsonify(data)

@app.route("/api/category_summary")
def get_category_summary_api():
    return jsonify(tracker.analytics()["category_totals"])

@app.route("/api/assistant", methods=["POST"])
def assistant():
    question = (request.json or {}).get("message", "").strip()
    if not question:
        return jsonify({"answer": "Ask me something about your expenses."}), 400
    data = tracker.analytics()
    transactions = tracker.expenses[-100:]
    context = {
        "currency": "INR",
        "all_time_total": data["total"],
        "current_month_total": data["month_total"],
        "previous_month_total": data["previous_month_total"],
        "category_totals": data["category_totals"],
        "monthly_totals": data["monthly_totals"],
        "recent_transactions": [
            {"date": e.date.isoformat(), "amount": e.amount, "category": e.category, "description": e.description}
            for e in transactions
        ]
    }
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = (
                "You are a helpful personal expense assistant. Answer only using the supplied "
                "expense data. Never invent totals. Use INR, be concise, explain calculations "
                "when useful, and give practical non-judgmental suggestions. If data is insufficient, say so. "
                "Return clean plain text only. Do not use Markdown, bold markers, headings, tables, or code blocks. "
                "Use short paragraphs and simple hyphenated bullet lines when useful.\n\n"
                f"Expense data: {context}\n\nUser question: {question}"
            )
            models = ("gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.8-flash")
            last_error = None
            for model in models:
                try:
                    response = client.models.generate_content(model=model, contents=prompt)
                    if response.text:
                        return jsonify({"answer": plain_text_response(response.text)})
                except Exception as error:
                    last_error = error
                    app.logger.warning("Gemini model %s failed: %s", model, error)
            app.logger.error("All Gemini models failed. Last error: %s", last_error)
            return jsonify({"answer": fallback_answer(question, data, gemini_available=True)})
        except Exception:
            app.logger.exception("Gemini request failed")
            return jsonify({"answer": fallback_answer(question, data, gemini_available=True)})
    return jsonify({"answer": fallback_answer(question, data, gemini_available=False)})

def fallback_answer(question, data, gemini_available):
    category_totals = data["category_totals"]
    if not tracker.expenses:
        return "There are no expenses yet. Add a few transactions and I can help analyse your spending."
    if category_totals:
        top_category = max(category_totals, key=category_totals.get)
        share = category_totals[top_category] / data["total"] * 100 if data["total"] else 0
        insight = f"Your highest-spending category is {top_category.title()} at ₹{category_totals[top_category]:,.2f} ({share:.1f}% of recorded spending)."
    else:
        insight = "There is not enough category data yet."
    summary = (f"{insight} You have recorded ₹{data['month_total']:,.2f} this month and "
               f"₹{data['total']:,.2f} overall.")
    if gemini_available:
        return summary + " Gemini is temporarily unavailable. Please try your question again shortly."
    return summary + " A Gemini API key is not configured; set GEMINI_API_KEY to enable natural-language answers."

def plain_text_response(text):
    text = re.sub(r"```[^\n]*|```", "", text)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"(?m)^\s*[*+]\s+", "- ", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()

@app.route("/download_report_csv")
def download_report_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Amount", "Category", "Description"])
    for expense in tracker.expenses:
        writer.writerow([expense.date, expense.amount, expense.category, expense.description])
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=expense_report.csv"
    return response

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
