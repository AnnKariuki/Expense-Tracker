# expenses business logic to manage expenses / expense behavior
# add expense
# update expense
# delete expense
# list expenses
# calculate summary
# load expenses
# save expenses

# validare non-existent expense ids
from expense import Expense
from expense_database import ExpenseDatabase

class ExpenseTracker:
    def __init__(self):
        # composition. this class does not manage database operations hence we call the class that does
        self.expense_database = ExpenseDatabase()

    def add_expense(self):
        pass