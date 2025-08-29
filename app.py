from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import datetime
import csv
import io
import os

app = Flask(__name__)

# File to store expenses
CSV_FILE = 'expenses.csv'

class Expense:
    """A single expense entry."""
    def __init__(self, amount, category, description, date=None):
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date if date else datetime.date.today()

class ExpenseTracker:
    """Manages expense records and reporting."""
    def __init__(self):
        self.expenses = self.load_expenses()
        self.allowed_categories = ['food', 'clothing', 'travel', 'books', 'entertainment', 'utilities', 'other']

    def load_expenses(self):
        """Load expenses from CSV file."""
        expenses = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        expenses.append(Expense(
                            amount=float(row['amount']),
                            category=row['category'],
                            description=row['description'],
                            date=datetime.date.fromisoformat(row['date'])
                        ))
                    except (ValueError, KeyError) as e:
                        print(f"Error loading row from CSV: {row}. Error: {e}")
        return expenses

    def save_expenses(self):
        """Save expenses to CSV file."""
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['date', 'amount', 'category', 'description']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for expense in self.expenses:
                writer.writerow({
                    'date': expense.date.isoformat(),
                    'amount': expense.amount,
                    'category': expense.category,
                    'description': expense.description
                })

    def add_expense(self, amount, category, description):
        """Add a new expense."""
        try:
            amount = float(amount)
            category = category.lower()

            if amount <= 0:
                return "Invalid amount. Please enter a positive number."
            if not description:
                return "Description cannot be empty."
            if category not in self.allowed_categories:
                return f"Invalid category. Please select from: {', '.join(self.allowed_categories)}"

            expense = Expense(amount, category, description)
            self.expenses.append(expense)
            self.save_expenses()  # Save to CSV after adding
            return "Expense added successfully."
        except ValueError:
            return "Invalid amount. Please enter a valid number."

    def get_expenses_by_category(self, category):
        """Get expenses for a specific category."""
        return [expense for expense in self.expenses if expense.category == category.lower()]

    def get_total_expenses(self):
        """Calculate total expenses."""
        return sum(expense.amount for expense in self.expenses)

    def get_expenses_for_month(self, year, month):
        """Get expenses for a given month."""
        return [expense for expense in self.expenses if expense.date.year == int(year) and expense.date.month == int(month)]

    def generate_report(self):
        """Generate a report with totals and summaries."""
        total_expenses = self.get_total_expenses()
        category_summary = {}
        for expense in self.expenses:
            category_summary[expense.category] = category_summary.get(expense.category, 0) + expense.amount
        
        report = {
            'total_expenses': total_expenses,
            'category_summary': category_summary,
            'all_expenses': self.expenses
        }
        return report

tracker = ExpenseTracker()

@app.route('/')
def index():
    """Home page: add and view expenses."""
    return render_template('index.html', expenses=tracker.expenses, categories=tracker.allowed_categories)

@app.route('/add', methods=['POST'])
def add():
    """Add a new expense."""
    amount = request.form['amount']
    category = request.form['category']
    description = request.form['description']
    tracker.add_expense(amount, category, description)
    return redirect(url_for('index'))

@app.route('/report')
def report():
    """Show detailed expense report."""
    report_data = tracker.generate_report()
    return render_template('report.html', report=report_data)

@app.route('/download_report_csv')
def download_report_csv():
    """Download report as CSV."""
    report_data = tracker.generate_report()
    
    si = io.StringIO()
    cw = csv.writer(si)

    cw.writerow(['Date', 'Amount', 'Category', 'Description'])
    for expense in report_data['all_expenses']:
        cw.writerow([expense.date, expense.amount, expense.category, expense.description])
    
    cw.writerow([])
    cw.writerow(['Category Summary'])
    cw.writerow(['Category', 'Total Amount'])
    for category, total in report_data['category_summary'].items():
        cw.writerow([category, total])

    cw.writerow([])
    cw.writerow(['Total Expenses', report_data['total_expenses']])

    output = si.getvalue()
    
    response = Response(output, mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=expense_report.csv"
    return response

@app.route('/api/category_summary')
def get_category_summary_api():
    """API: category summary as JSON."""
    report_data = tracker.generate_report()
    return jsonify(report_data['category_summary'])

if __name__ == '__main__':
    app.run(debug=True)