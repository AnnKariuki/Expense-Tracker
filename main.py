import argparse
from expense_tracker import ExpenseTracker

def main() -> None:
    parser = argparse.ArgumentParser(prog="Expense Tracker", description="Simple expense tracker application to manage your finances")
    subparsers = parser.add_subparsers(required=True)
    # we will use one expensetracker instance to handle all subcommands
    tracker = ExpenseTracker()
    add_subparser = subparsers.add_parser('add', help="To add an expense run: <expense-tracker> --description=<description> --amount=<amount>")
    add_subparser.add_argument("--description")
    add_subparser.add_argument("--amount", type=float)
    add_subparser.set_defaults(func=tracker.add_expense)

    update_subparser = subparsers.add_parser('update', help="To update an expense run: <expense-tracker> <id> --amount=<amount> and/or --description=<description>")
    update_subparser.add_argument("id")
    update_subparser.add_argument("--amount")
    update_subparser.add_argument("--description")
    update_subparser.set_defaults(func=tracker.update_expense)

    # CLI error handling - make sure we are passing in correct types into Expense tracker incase some values slip in for example amount=-20 or name

    args = parser.parse_args()
    args.func(args)
    

if __name__ == "__main__":
    main()