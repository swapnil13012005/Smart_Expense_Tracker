# SpendWise — Smart Expense Tracker

A Flask-based personal finance dashboard for recording expenses, understanding spending patterns, and getting AI-assisted suggestions.

## Features

- Responsive finance dashboard with monthly totals, all-time spending, average transaction value, and transaction count
- Monthly spending trend and category breakdown charts
- Add, search, filter, edit, and delete transactions
- CSV report export
- AI finance assistant powered by Gemini for natural-language questions and suggestions
- Basic spending insight fallback when a Gemini key is not configured

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Configure Gemini AI:

   **Windows PowerShell**
   ```powershell
   $env:GEMINI_API_KEY="your_api_key"
   ```

   **macOS/Linux**
   ```bash
   export GEMINI_API_KEY="your_api_key"
   ```

   Get an API key from [Google AI Studio](https://aistudio.google.com/apikey). Keep the key private and never commit it to Git.

4. Run the application:

   ```bash
   python app.py
   ```

5. Open http://127.0.0.1:5000.

## Data storage

Expenses are stored in `expenses.csv` to preserve compatibility with the original project. Set `EXPENSES_CSV` to use a different file path. Do not commit personal transaction data to a public repository.

## API

- `GET /api/analytics` — dashboard metrics, charts, and transactions
- `GET /api/category_summary` — totals grouped by category
- `POST /api/assistant` — AI-assisted spending question; JSON body: `{"message":"..." }`

## Notes

The app calculates all totals and category metrics in Python before sending summarized transaction context to Gemini. AI responses are explanatory suggestions, not professional financial advice.
