# Smart Expense Tracker

A simple, modern expense tracker built with Flask. Track your daily spending, view summaries, and download detailed reports.

## Features

- Add new expenses with category and description
- View all expenses in a sortable table
- Generate detailed reports with category summaries and charts
- Download reports as CSV
- Responsive design

## Setup

1. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Run the app**
   ```
   python app.py
   ```
   Visit [http://localhost:5000](http://localhost:5000) in your browser.

## Structure

```
Smart Expense Tracker/
│
├── app.py
├── expenses.csv
├── requirements.txt
├── static/
│   └── style.css
└── templates/
    ├── index.html
    └── report.html
```

## Usage

- Add expenses from the home page.
- View all expenses and generate a report.
- Download the report as CSV.

## API

- `GET /api/category_summary`  
  Returns a JSON summary of expenses by category.

## Contributing

Pull requests welcome. For major changes, open an issue first.

