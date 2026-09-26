# expenses business logic to manage expenses / expense behavior
# add expense
# update expense
# delete expense
# list expenses
# calculate summary
# load expenses
# save expenses

# validate non-existent expense ids
from expense import Expense
import argparse
from expense_database import ExpenseDatabase
import datetime
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
class ExpenseTracker:
    def __init__(self):
        # composition. this class does not manage database operations hence we call the class that does
        self.database = ExpenseDatabase()
        # load all expenses and let the tracker class own the collection
        self.expenses = self.database.load_database()

    def add_expense(self, args: argparse.Namespace):
        expense = {
           "id": self.highest_id() + 1,
           "description": args.description,
           "amount": int(args.amount) if args.amount.isdigit() else float(args.amount),
           "date": datetime.datetime.now()
        }
        # we do not need to have expensetracker reload it's expenses since we are undating self.expenses here
        self.expenses.append(Expense(**expense))

    def highest_id(self):
        # maximum = 0 
        # for expense in self.expenses:
        #     maximum = max(maximum, expense.id)
        # return maximum

        # max here returns the expense object with the max id then we access it's id with .id and return that
        # remember an empty list or any empty Sequences and Collections are falsy
        return max(self.expenses, key= lambda x: x.id).id if self.expenses else 0

high = ExpenseTracker().highest_id()
print(high)
print(bool([]))