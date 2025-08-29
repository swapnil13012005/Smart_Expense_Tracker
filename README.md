Smart Expense Tracker 💰

A simple and intuitive web-based expense tracker built with Python Flask. Track daily expenses, visualize spending by category, and download detailed financial reports effortlessly.

✨ Features

Add Expenses: Record new expenses with predefined categories: Food, Clothing, Travel, Books, Entertainment, Utilities, Other. Include descriptive notes for clarity.

View Expenses: Display all recorded expenses in a clear, sortable table.

Interactive Reporting: Generate dynamic pie charts (via Chart.js) showing spending distribution by category.

Persistent Storage: All data is saved to a CSV file, ensuring records persist across sessions.

Download Reports: Export your expenses as a CSV file for offline analysis.

Responsive UI: Clean and modern interface with CSS animations for enhanced usability.

🚀 Setup Instructions

1. Clone the Repository

git clone <your-repo-url> # Replace with your repository URL
cd Smart-Expense-Tracker

2. Install Dependencies

Use a virtual environment (recommended):

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

3. Run the Application

python app.py

Open http://localhost:5000 in your browser.

📂 Project Structure

Smart-Expense-Tracker/
│
├── app.py                 # Flask application
├── expenses.csv           # Stores expense data
├── requirements.txt       # Python dependencies
├── static/                # Static assets
│   └── style.css          # Custom CSS
└── templates/             # HTML templates
    ├── index.html         # Home page (add/view expenses)
    └── report.html        # Report page (charts & summaries)

📖 Usage

Add Expenses: Fill in Amount, Category, and Description on the home page, then click Add Expense.

View Expenses: All entries appear in a table on the home page.

Generate Report: Navigate to /report to view summaries, charts, and all recorded expenses.

Download Report: Click Download Report (CSV) on the report page.

🌐 API Endpoint

/api/category_summary

Method: GET

Description: Returns total spending per category as JSON (used for charts).

Example Response:

{
  "food": 1000.0,
  "travel": 250.0,
  "clothing": 750.0,
  "books": 300.0,
  "entertainment": 500.0,
  "utilities": 120.0,
  "other": 1000.0
}

📊 Sample expenses.csv

date,amount,category,description
2025-08-28,150.0,food,Lunch at cafe
2025-08-28,50.0,travel,Bus fare
2025-08-27,450.0,clothing,New t-shirt
2025-08-27,20.0,travel,Rickshaw to market
2025-08-26,300.0,books,Python textbook
2025-08-26,75.0,food,Groceries
2025-08-25,500.0,entertainment,Movie ticket
2025-08-25,120.0,utilities,Mobile recharge

💡 Future Enhancements

User Authentication: Multiple users with private expense tracking.

Database Support: Move from CSV to SQLite/PostgreSQL for scalability.

Advanced Visualizations: Bar charts, line charts, and trend analysis.

Filtering & Search: Filter by date, category, amount, or search keywords.

CRUD Operations: Edit or delete existing expenses.

