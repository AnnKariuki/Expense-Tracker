import argparse
from expense_tracker import ExpenseTracker

def main() -> None:
    parser = argparse.ArgumentParser(prog="Expense Tracker", description="Simple expense tracker application to manage your finances")
    subparsers = parser.add_subparsers(required=True)
    # we will use one expensetracker instance to handle all subcommands
    tracker = ExpenseTracker()
    add_subparser = subparsers.add_parser('add', help="To add an expense run: <expense-tracker> <description> <amount>")
    add_subparser.add_argument("description")
    add_subparser.add_argument("amount", type=float)
    add_subparser.set_defaults(func=tracker.add_expense)

    update_subparser = subparsers.add_parser('update', help="To update an expense run: <expense-tracker> <id> --description=<description> and/or --amount=<amount>")
    update_subparser.add_argument("id", type=int)
    update_subparser.add_argument("--description")
    update_subparser.add_argument("--amount", type=float)
    update_subparser.set_defaults(func=tracker.update_expense)

    delete_subparser = subparsers.add_parser('delete', help="To delete an expense run: <expense-tracker> <id>")
    delete_subparser.add_argument("id", type=int)
    delete_subparser.set_defaults(func=tracker.delete_expense)

    args = parser.parse_args()
    args.func(args)
    

if __name__ == "__main__":
    main()
