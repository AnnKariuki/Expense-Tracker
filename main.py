import argparse
from expense_tracker import ExpenseTracker

def main() -> None:
    parser = argparse.ArgumentParser(prog="Expense Tracker", description="Simple expense tracker application to manage your finances", formatter_class=argparse.RawTextHelpFormatter) 
    # RawTextHelpFormatter maintains whitespace for all sorts of help text
    subparsers = parser.add_subparsers(required=True)
    # we will use one expensetracker instance to handle all subcommands so one initialization
    tracker = ExpenseTracker()
    add_subparser = subparsers.add_parser('add', help="To add an expense run: <expense-tracker> --description <description> --amount <amount> --category <category>")
    add_subparser.add_argument("--description", required=True) # required optional flags
    add_subparser.add_argument("--amount", type=float, required=True)
    add_subparser.add_argument("--category", required=True)
    add_subparser.set_defaults(func=tracker.add_expense)

    update_subparser = subparsers.add_parser('update', help="To update an expense run: <expense-tracker> <id> --description <description> and/or --amount <amount>")
    update_subparser.add_argument("id", type=int)
    update_subparser.add_argument("--description")
    update_subparser.add_argument("--amount", type=float)
    update_subparser.add_argument("--category")
    update_subparser.set_defaults(func=tracker.update_expense)

    delete_subparser = subparsers.add_parser('delete', help="To delete an expense run: <expense-tracker> <id>")
    delete_subparser.add_argument("id", type=int)
    delete_subparser.set_defaults(func=tracker.delete_expense)

    list_subparser = subparsers.add_parser('list', help="To list all your expenses run: <expense-tracker> list \nTo view all your expenses by catogory run <expense-tracker> list --category <category>")
    list_subparser.add_argument("--category")
    list_subparser.set_defaults(func=tracker.list_expenses)

    summary_subparser = subparsers.add_parser('summary',help="""To view a summary of all your expenses run: <expense-tracker> summary\nTo view a summary for a specific month of current year run: <expense-tracker> summary --month <month>""")
    summary_subparser.add_argument("--month", type=int, choices=[1,2,3,4,5,6,7,8,9,10,11,12])
    summary_subparser.set_defaults(func=tracker.summary_expenses)

    args = parser.parse_args()
    args.func(args)
    

if __name__ == "__main__":
    main()
