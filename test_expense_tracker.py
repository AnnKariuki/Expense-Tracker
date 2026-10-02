# Business logic layer -  constructor immediately creates both database objects and loads expenses/budgets, so for unit tests we want to mock those persistence dependencies rather than touch CSV files.
import unittest
from unittest.mock import patch
import argparse
import datetime

from expense import Expense
from expense_tracker import ExpenseTracker

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
 
# FakeDateTime inherits the behavior of the real datetime.datetime. an instance of FakeDateTime is also considered an instance of datetime.datetime.
# we are overriding now() instead of returnong current time, now() always returns October 1 2026 at 10 pm cause we need to freeze time toeeffectively text that the correct expenses are added
# Other datetime functionality remains inherited, including methods like strptime() and strftime().
class FakeDate(datetime.datetime):
    @classmethod
    def now(cls):
        return cls(2026, 10, 1, 22, 0, 0)

class TestExpenseTracker(unittest.TestCase):

    def setUp(self):
        # before we call the ExpenseTracker class we need to patch ExpenseDatabase and BudgetDatabase cause we don't want to interact with the prod csv files
        # need patch here but we will do it manually instead of as a decorator or context manager
        self.expense_db_patch = patch("expense_tracker.ExpenseDatabase", autospec=True) # Patch the name in the module where the code under test looks it up, not necessarily where the class was originally defined.
        self.autospeced_expense_bd_class_mock = self.expense_db_patch.start() # mocked class
        # shold be stop not stop() When Python evaluates the line, it immediately executes stop(), removing your patch before ExpenseTracker is instantiated.
        # Then it passes the return value of stop() to addCleanup(), rather than passing the cleanup function itself.
        # we should be passing the function without executing it. unittest will call it during cleanup.
        self.addCleanup(self.expense_db_patch.stop) # multiple add clean ups  are executed in Last-In, First-Out (LIFO) order
        # self.expense_db = ExpenseDatabase()
        self.expense_db = self.autospeced_expense_bd_class_mock.return_value # instance of mocked class
        self.expenses = [
            Expense(id=1, date=datetime.datetime.strptime("2026-09-27 14:50:23", DATE_FORMAT), description="Chipotle", amount=20.0, category="groceries"),
            Expense(id=2, date=datetime.datetime.strptime("2026-09-27 15:19:49", DATE_FORMAT), description="Movie", amount=20.123, category="entertainment")
        ]
        self.expense_db.load_database.return_value = self.expenses

        self.budget_db_patch = patch('expense_tracker.BudgetDatabase', autospec=True)
        self.autospeced_budget_bd_class_mock = self.budget_db_patch.start()
        self.addCleanup(self.budget_db_patch.stop)
        self.budget_db = self.autospeced_budget_bd_class_mock.return_value # what is the return value when we call a class? an instance of the class
        self.budgets = {(3, 2026): 100.0, (4, 2026): 100.0, (9, 2026): 30.0}
        self.budget_db.load_database.return_value = self.budgets

        # now we can initialize the ExpenseTracker class cause we have mocked all the dependecies it calls to interact with our csv files which hold prod data
        # if we didn't ExpenseTracker() would call __init-_ which would load all prod data and that is not what you want in tests. test and prod data must be isolated
        self.exp_tracker = ExpenseTracker() 

        # now in the tests we will be usung exp_tracker public interface
    #----------------------------------------------------------------------------------------------------
    #__init__
    #----------------------------------------------------------------------------------------------------
    def test_init_loads_expenses(self):
        # assert that the mock method was called
        self.exp_tracker.expense_db.load_database.assert_called_once()
        self.assertEqual(self.exp_tracker.expenses, self.expenses)

    def test_init_loads_budgets(self):
        # assert that the mock method was called
        self.exp_tracker.budget_db.load_database.assert_called_once()
        self.assertEqual(self.exp_tracker.budgets, self.budgets)

    #----------------------------------------------------------------------------------------------------
    # highest_id
    #----------------------------------------------------------------------------------------------------
    # boundary
    def test_highest_id_returns_zero_when_expenses_empty(self):
        self.exp_tracker.expenses = []
        self.assertEqual(self.exp_tracker.highest_id(), 0)

    def test_highest_id_returns_highest_expense_id(self):
        self.assertEqual(self.exp_tracker.highest_id(), 2) 

    #----------------------------------------------------------------------------------------------------
    # add_expense
    #----------------------------------------------------------------------------------------------------
    # replacing datetime.datetime with a subclass of datetime.datetime, rather than a MagicMock. this is because when creating an expense we validate that the data is a datitime object but having it as a magic mock isn't great cause creating an expense will always fail
    @patch("expense_tracker.datetime.datetime", FakeDate)
    def test_add_expense_creates_expense_with_next_id(self):
        date = FakeDate.now()
        args = argparse.Namespace(description = "buy a car", amount = 100000.0, category = "luxury")
        self.exp_tracker.add_expense(args)
        # this also confirms that we assigned the highest id if the 2 expenses match
        expected_expense = Expense(id=3, description = "buy a car", amount = 100000.0, category = "luxury", date=date)
        self.assertEqual(expected_expense, self.exp_tracker.expenses[-1])
        #  confirms saves updated expenses
        # self.exp_tracker.expense_db.save_database.assert_called_once_with(self.exp_tracker.expenses)
        # self.exp_tracker.check_over_budget.assert_called_once_with(date.month, date.year)

    @patch("expense_tracker.datetime.datetime", FakeDate)
    def test_add_expense_saves_updated_expenses(self):
        args = argparse.Namespace(description = "buy a car", amount = 100000.0, category = "luxury")
        self.exp_tracker.add_expense(args)
        #  confirms saves updated expenses
        self.exp_tracker.expense_db.save_database.assert_called_once_with(self.exp_tracker.expenses)

    @patch("expense_tracker.datetime.datetime", FakeDate)
    # @patch("expense_tracker.check_over_budget") # we can't do this because check_over_budget() is a method of the ExpenseTracker class, not a function defined directly in the expense_tracker module.
    @patch("expense_tracker.ExpenseTracker.check_over_budget")
    def test_add_expense_checks_budget_for_expense_month_and_year(self, mocked_over_budget_check):
        args = argparse.Namespace(description = "buy a car", amount = 100000.0, category = "luxury")
        self.exp_tracker.add_expense(args)
        date = FakeDate.now()
        mocked_over_budget_check.assert_called_once_with(date.month, date.year)


    # you could stop the patches in teardown but that is not good practice since we started them in setup()
    # The difference is when cleanup gets registered and executed.
    # - tearDown() runs after setUp() completes successfully and the test method runs, even if the test fails. if set up fails teardown does not run which can cause resource leaks to other tests. remember tests need to be isolated
    # - addCleanup() registers cleanup immediately. The registered cleanup still runs even if setUp() raises an exception partway through.
    # def tearDown(self):
    #     self.expense_db_patch.stop()
if __name__ == "__main__":
    unittest.main()

# MagicMock(...) directly
#     = "I created a fake object."

# patch(...)
#     = "Replace the object that MY CODE is going to use with a fake."

# Python provides you with three ways to call patch():

# Decorators for a function or a class.
# Context manager
# Manual start/stop


#autospec and mocking classes

# Mock expression  Represents
# self.autospeced_expense_bd_class_mock	ExpenseDatabase
# self.autospeced_expense_bd_class_mock.return_value	ExpenseDatabase()
# self.autospeced_expense_bd_class_mock.return_value.load_database	ExpenseDatabase().load_database
# self.autospeced_expense_bd_class_mock.return_value.load_database.return_value	Result of ExpenseDatabase().load_database()

# we are mocking a class not an instance of a class
# start() here returns a mock representing the ExpenseDatabase class itself.
# in prod code we instantiate an instance of the class:
# self.expense_db = ExpenseDatabase()
# self.expenses = self.expense_db.load_database()

# when we write self.autospeced_expense_bd_class_mock.return_value we're accessing the mock instance that will be returned when your production code calls ExpenseDatabase()
# 3. Why can't you omit the first .return_value?
# Suppose you write:
# self.autospeced_expense_bd_class_mock.load_database.return_value = self.expenses

# You're trying to configure load_database() directly on the mocked class.
# But your production code doesn't call:
# ExpenseDatabase.load_database()

# It calls:
# ExpenseDatabase().load_database()

# Those are different objects.
# With autospec=True, trying to configure the method directly on the class mock may be allowed because the method exists on the real class, but it still won't configure the method on the mock instance.
# 4. The correct configuration
# self.autospeced_expense_bd_class_mock.return_value.load_database.return_value = self.expenses

# This tells Python:
# - When ExpenseDatabase() is called, return the mock instance.
# - When .load_database() is called on that instance, return self.expenses.