import argparse
from expense_tracker import ExpenseTracker

def main():
    parser = argparse.ArgumentParser(prog="Expense Tracker", description="Simple expense tracker application to manage your finances")
    subparsers = parser.add_subparsers(required=True)
    add_subparser = subparsers.add_parser('add', help="To add an expense run: <expense-tracker> --description=<description> --amount=<amount>")
    add_subparser.add_argument("--description")
    add_subparser.add_argument("--amount")
    args = parser.parse_args()
    print(args)
    

if __name__ == "__main__":
    main()