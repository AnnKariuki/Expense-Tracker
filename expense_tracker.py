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

    def add_expense(self, args: argparse.Namespace) -> None:
        id = self.highest_id() + 1
        expense = {
           "id": id,
           "description": args.description,
           "amount": args.amount,
           "date": datetime.datetime.now()
        }
        # we do not need to have expensetracker reload it's expenses since we are updating self.expenses here
        self.expenses.append(Expense(**expense))
        self.database.save_database(self.expenses)
        print(f"Task added successfully (ID: {id})")

    def highest_id(self) -> int: # placed this method in expense tracker not in database class because 1, it needs access to all expenses and the db's class work should only be interacting with csv
        #file so that even if I chnaged my id method to UUIDS the db class would not have to be touched. separtion of concerns
        # in my implementation ids are not unique since if i delete id 3 and add a new expense it will take that id 3. this isn't great in real production systems where ids need to be unique for easy identification
        # maximum = 0 
        # for expense in self.expenses:
        #     maximum = max(maximum, expense.id)
        # return maximum

        # max here returns the expense object with the max id then we access it's id with .id and return that
        # remember an empty list or any empty Sequences and Collections are falsy
        return max(self.expenses, key= lambda x: x.id).id if self.expenses else 0

    def update_expense(self, args:argparse.Namespace) -> None:
        if args.amount is None and args.description is None:
            raise ValueError("At least one of --amount or --description must be provided")
        updated = False
        for expense in self.expenses:
            if expense.id == args.id:
                if args.amount is not None: # not if args.amount cause we want to assess actual value not truthiness for example 0.00 would fail even though it is legitimate
                    expense.amount = args.amount
                if args.description is not None: # same here with "" maybe client wanted to clear description but "" is falsy so description would not get the update
                    expense.description = args.description
                updated = True
                break
        if updated:
            self.database.save_database(self.expenses)
        else:
            print(f"There is no expense with id: {args.id}")

    def delete_expense(self, args:argparse.Namespace) -> None:
        deleted = False
        for expense in self.expenses:
            if expense.id == args.id:
                # swap and pop method to have O(1) deletion but looping with our for loop is o(n) and index() is also traversing the list o(index) so better to do in place deletion
                # cause remove is o(n) and looping is o(n) so no drawback both 0(2n)=o(n). the swap also messes up my csv file ordering whihc will be important when displaying a 
                # customer's expenses
                # i = self.expenses.index(expense)
                # self.expenses[i], self.expenses[-1] = self.expenses[-1], self.expenses[i]
                # self.expenses.pop()
                self.expenses.remove(expense)
                deleted = True
                break
        if deleted:
            self.database.save_database(self.expenses)
        else:
            print(f"There is no expense with id: {args.id}")
