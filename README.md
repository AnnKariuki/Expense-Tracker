# Expense Tracker

A command-line expense tracker built with Python to manage personal expenses.

This project is part of the [roadmap.sh Backend Projects](https://roadmap.sh/projects/expense-tracker).

## Features

- Add expenses with a description, amount, and category.
- Update existing expenses.
- Delete expenses by ID.
- View all expenses.
- Filter expenses by category.
- View a summary of total expenses.
- View expenses for a specific month of the current year.
- Set and update monthly budgets.
- Receive warnings when expenses exceed the monthly budget.
- Export expenses to a CSV file.
- Persist expenses and budgets using CSV files.

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install tabulate
```

## Usage

### Add an expense

```bash
python3 main.py add --description "Lunch" --amount 20 --category food
```

Output:

```text
Task added successfully (ID: 1)
```

### Update an expense

Update an expense by specifying its ID and the fields to modify.

```bash
python3 main.py update 1 --amount 25
```

You can also update the description or category.

```bash
python3 main.py update 1 --description "Dinner" --category food
```

### Delete an expense

```bash
python3 main.py delete 1
```

### List all expenses

```bash
python3 main.py list
```

Filter expenses by category:

```bash
python3 main.py list --category food
```

### View expense summary

View the total of all expenses:

```bash
python3 main.py summary
```

Output:

```text
Total expenses: $150.00
```

View the summary for a specific month of the current year:

```bash
python3 main.py summary --month 9
```

Output:

```text
Total expenses for September: $100.00
```

Months are represented by integers from `1` (January) to `12` (December).

### Set a monthly budget

Set a budget for a specific month and year:

```bash
python3 main.py budget --month 9 --year 2026 --budget 500
```

To update an existing budget, run the same command with a different amount.

When an expense is added or its amount is updated, the application checks whether the total monthly spending exceeds the configured budget.

Example warning:

```text
warning September 2026 expenses 550.0 exceed your 500.0 budget.
```

### Export expenses

Export expenses to a CSV file:

```bash
python3 main.py export --output ./export.csv
```

You can also specify an absolute path or a path relative to your home directory.

```bash
python3 main.py export --output ~/Downloads/expenses.csv
```

Example CSV output:

```csv
id,date,description,amount,category
1,2026-09-27 14:50:23,Lunch,20.0,food
2,2026-09-27 15:19:49,Movie,15.0,entertainment
```

The export operation does not overwrite an existing file.

### Components

- **main.py**: Defines CLI commands, parses arguments, and dispatches operations.
- **expense.py**: Defines the `Expense` model and validates its attributes.
- **expense_tracker.py**: Implements business logic for managing expenses and budgets.
- **expense_database.py**: Handles CSV serialization and persistence of expenses.
- **budget_database.py**: Handles CSV serialization and persistence of budgets.
