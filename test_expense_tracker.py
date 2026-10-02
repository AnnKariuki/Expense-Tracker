# Business logic layer -  constructor immediately creates both database objects and loads expenses/budgets, so for unit tests we want to mock those persistence dependencies rather than touch CSV files.
import unittest
from unittest.mock import patch
import argparse
import datetime

from expense import Expense
from expense_tracker import ExpenseTracker
from pathlib import Path
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
        # shold be stop not stop() When Python evaluates the line, it immediately executes stop(), removing our patch before ExpenseTracker is instantiated.
        # Then it passes the return value of stop() to addCleanup(), rather than passing the cleanup function itself.
        # we should be passing the function without executing it. unittest will call it during cleanup.
        self.addCleanup(self.expense_db_patch.stop) # multiple add clean ups  are executed in Last-In, First-Out (LIFO) order
        # self.expense_db = ExpenseDatabase()
        self.expense_db = self.autospeced_expense_bd_class_mock.return_value # instance of mocked class
        self.expenses = [
            Expense(id=1, date=datetime.datetime.strptime("2026-09-27 14:50:23", DATE_FORMAT), description="Chipotle", amount=20.0, category="groceries"),
            Expense(id=2, date=datetime.datetime.strptime("2026-09-27 15:19:49", DATE_FORMAT), description="Movie", amount=20.123, category="entertainment"),
            Expense(id=3, date=datetime.datetime.strptime("2026-11-27 15:19:49", DATE_FORMAT), description="Movie", amount=1000.0, category="entertainment")
        ]
        self.expense_db.load_database.return_value = self.expenses

        self.budget_db_patch = patch('expense_tracker.BudgetDatabase', autospec=True)
        self.autospeced_budget_bd_class_mock = self.budget_db_patch.start()
        self.addCleanup(self.budget_db_patch.stop)
        self.budget_db = self.autospeced_budget_bd_class_mock.return_value # what is the return value when we call a class? an instance of the class
        self.budgets = {(3, 2026): 100.0, (4, 2026): 100.0, (9, 2026): 50.0, (11,2026):15.0}
        self.budget_db.load_database.return_value = self.budgets

        # now we can initialize the ExpenseTracker class cause we have mocked all the dependecies it calls to interact with our csv files which hold prod data
        # if we didn't ExpenseTracker() would call __init-_ which would load all prod data and that is not what we want in tests. test and prod data must be isolated
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
    # check_over_budget
    #----------------------------------------------------------------------------------------------------
    @patch("builtins.print")
    def test_check_over_budget_when_no_budget_is_set(self, mock_print):
        # budget is definitely missing cause a present budget that is not over budget displays same symptoms
        self.assertNotIn((10, 2026), self.exp_tracker.budgets)
        result = self.exp_tracker.check_over_budget(10, 2026)
        self.assertIsNone(result)
        # warning not printed
        mock_print.assert_not_called()

    @patch("builtins.print")
    def test_check_over_budget_below_budget_does_not_warn(self, mock_print):
        # budget not missing
        self.assertIn((9, 2026), self.exp_tracker.budgets)
        result = self.exp_tracker.check_over_budget(9, 2026)
        self.assertIsNone(result)
        # warning not printed
        mock_print.assert_not_called()

    @patch("builtins.print")
    def test_check_over_budget_equal_to_budget_does_not_warn(self, mock_print):
        self.exp_tracker.expenses = [Expense(id=1,date=datetime.datetime.strptime("2026-09-27 14:50:23",DATE_FORMAT),description="Chipotle",amount=30.0,category="groceries")]
        self.exp_tracker.budgets = {(9, 2026): 30.0}
        self.exp_tracker.check_over_budget(9, 2026)
        mock_print.assert_not_called()

    @patch("builtins.print")
    def test_check_over_budget_above_budget_warns(self, mock_print):
        self.assertIn((11, 2026), self.exp_tracker.budgets)
        result = self.exp_tracker.check_over_budget(11, 2026)
        self.assertIsNone(result)
        # warning not printed
        mock_print.assert_called_once_with("warning November 2026 expenses 1000.0 exceed your 15.0 budget.")


    #----------------------------------------------------------------------------------------------------
    # highest_id
    #----------------------------------------------------------------------------------------------------
    # boundary
    def test_highest_id_returns_zero_when_expenses_empty(self):
        self.exp_tracker.expenses = []
        self.assertEqual(self.exp_tracker.highest_id(), 0)

    def test_highest_id_returns_highest_expense_id(self):
        self.assertEqual(self.exp_tracker.highest_id(), 3) 

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
        expected_expense = Expense(id=4, description = "buy a car", amount = 100000.0, category = "luxury", date=date)
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

    #----------------------------------------------------------------------------------------------------
    # update_expense
    #----------------------------------------------------------------------------------------------------
    def test_update_expense_without_fields_raises_value_error(self):
        args = argparse.Namespace(id=1, amount=None, description=None, category=None)
        with self.assertRaises(ValueError):
            self.exp_tracker.update_expense(args)

    def test_update_expense_updates_amount(self):
        amount_before = self.exp_tracker.expenses[0].amount
        args = argparse.Namespace(id=1, amount=100.0, description=None, category=None)
        self.exp_tracker.update_expense(args)
        self.assertEqual(self.exp_tracker.expenses[0].amount, 100.0)
        self.assertNotEqual(self.exp_tracker.expenses[0].amount, amount_before)

    def test_update_expense_updates_description(self):
        description_before = self.exp_tracker.expenses[0].description
        args = argparse.Namespace(id=1, amount=None, description="Concert", category=None)
        self.exp_tracker.update_expense(args)
        self.assertEqual(self.exp_tracker.expenses[0].description, "Concert")
        self.assertNotEqual(self.exp_tracker.expenses[0].description, description_before)

    def test_update_expense_updates_category(self):
        category_before = self.exp_tracker.expenses[0].category
        args = argparse.Namespace(id=1, amount=None, description=None, category="Fun")
        self.exp_tracker.update_expense(args)
        self.assertEqual(self.exp_tracker.expenses[0].category, "fun")
        self.assertNotEqual(self.exp_tracker.expenses[0].category, category_before)

    @patch("expense_tracker.datetime.datetime", FakeDate)
    def test_update_expense_preserves_unspecified_fields(self):
        date_before = self.exp_tracker.expenses[0].date
        amount_before = self.exp_tracker.expenses[0].amount
        description_before = self.exp_tracker.expenses[0].description
        args = argparse.Namespace(id=1, amount=None, description=None, category="Fun")
        self.exp_tracker.update_expense(args)
        self.assertEqual(self.exp_tracker.expenses[0].date, date_before)
        self.assertEqual(self.exp_tracker.expenses[0].amount, amount_before)
        self.assertEqual(self.exp_tracker.expenses[0].description, description_before)

    def test_update_existing_expense_saves_database(self):
        args = argparse.Namespace(id=1, amount=100.0, description=None, category=None)
        self.exp_tracker.update_expense(args)
        # this works because we mocked the expense_tracker module's expensedatabase
        # so self.exp_tracker.expense_db is a mock instance therefore we can use assert_called_once_with() on it.
        self.exp_tracker.expense_db.save_database.assert_called_once_with(self.exp_tracker.expenses)

    @patch("expense_tracker.print")
    def test_update_nonexistent_expense_does_not_save_database(self, mocked_print):
        args = argparse.Namespace(id=5, amount=100.0, description=None, category=None)
        self.exp_tracker.update_expense(args)
        self.exp_tracker.expense_db.save_database.assert_not_called()
        mocked_print.assert_called_once_with("There is no expense with id: 5")

    @patch("expense_tracker.ExpenseTracker.check_over_budget")
    def test_update_amount_checks_budget(self, mocked_check_over_budget):
        args = argparse.Namespace(id=1, amount=100.0, description=None, category=None)
        self.exp_tracker.update_expense(args)
        mocked_check_over_budget.assert_called_once_with(self.exp_tracker.expenses[0].date.month, self.exp_tracker.expenses[0].date.year)

    #----------------------------------------------------------------------------------------------------
    # delete_expense
    #----------------------------------------------------------------------------------------------------
 
    def test_delete_existing_expense_removes_expense_and_saves(self):
        expected_expenses = [Expense(id=2, date=datetime.datetime.strptime( "2026-09-27 15:19:49", DATE_FORMAT), description="Movie", amount=20.123, category="entertainment"), 
                             Expense(id=3, date=datetime.datetime.strptime("2026-11-27 15:19:49", DATE_FORMAT), description="Movie", amount=1000.0, category="entertainment")]
        args = argparse.Namespace(id=1)
        self.exp_tracker.delete_expense(args)
        self.assertEqual(self.exp_tracker.expenses, expected_expenses)
        self.exp_tracker.expense_db.save_database.assert_called_once_with(self.exp_tracker.expenses)
        # the tests below are not necessary. the way we did it about is correct
        self.assertEqual(len(self.exp_tracker.expenses), 2)
        self.assertNotEqual(self.exp_tracker.expenses[0].id, 1)

    @patch("expense_tracker.print")
    def test_delete_nonexistent_expense_does_not_save(self, mocked_print):
        args = argparse.Namespace(id=5)
        self.exp_tracker.delete_expense(args)
        self.exp_tracker.expense_db.save_database.assert_not_called()
        mocked_print.assert_called_once_with("There is no expense with id: 5")

    #----------------------------------------------------------------------------------------------------
    # set_monthly_budget
    #----------------------------------------------------------------------------------------------------
    def test_set_new_monthly_budget_stores_and_saves_budget(self):
        args = argparse.Namespace(month=10,year=2026,budget=500.0)
        self.exp_tracker.set_monthly_budget(args)
        self.assertEqual(self.exp_tracker.budgets[(10, 2026)],500.0)
        self.budget_db.save_database.assert_called_once_with(self.exp_tracker.budgets)

    @patch("builtins.print")
    def test_set_existing_monthly_budget_replaces_and_saves_budget(self, mocked_print):
        args = argparse.Namespace(month=9,year=2026,budget=500.0)
        self.exp_tracker.set_monthly_budget(args)
        self.assertEqual(self.exp_tracker.budgets[(9, 2026)],500.0)
        self.budget_db.save_database.assert_called_once_with(self.exp_tracker.budgets)
        mocked_print.assert_called_once_with("you updated the budget of the month:September, year, 2026 to 500.0")

    #----------------------------------------------------------------------------------------------------
    # list_expenses
    #----------------------------------------------------------------------------------------------------
    
    @patch("expense_tracker.tabulate")
    @patch("builtins.print")
    def test_list_all_expenses(self, mock_print, mock_tabulate):
        args = argparse.Namespace(category=None)
        self.exp_tracker.list_expenses(args)

        expected_rows = [
            {"id": expense.id, "description": expense.description, "amount": expense.amount, "date": expense.date, "category": expense.category}
            for expense in self.expenses
        ]

        mock_tabulate.assert_called_once_with(expected_rows, headers="keys", tablefmt="grid")
        mock_print.assert_called_once_with(mock_tabulate.return_value)


    @patch("expense_tracker.tabulate")
    @patch("builtins.print")
    def test_list_expenses_filters_by_category(self, mock_print, mock_tabulate):
        args = argparse.Namespace(category="GROCERIES")
        self.exp_tracker.list_expenses(args)
        # list_expenses does not call datetime.datetime.now() so patching with FakeData here will not work
        # Expected: tabulate([{'id': 1, 'description': 'Chipotle', 'amount': 20.0, 'date': FakeDate(2026, 10, 1, 22, 0), 'category': 'groceries'}], headers='keys', tablefmt='grid')
        # Actual: tabulate([{'id': 1, 'description': 'Chipotle', 'amount': 20.0, 'date': datetime.datetime(2026, 9, 27, 14, 50, 23), 'category': 'groceries'}], headers='keys', tablefmt='grid')
        # patching datetime.datetime does not change the dates of expenses that were already created in setUp().
        # General rule: Freeze time when the code our testing depends on the current time, not simply because it works with dates.
        # use the existing expense's date
        expected_rows = [
            {"id": 1, "description": "Chipotle", "amount": 20.0, "date": self.expenses[0].date, "category": "groceries"}
        ]

        mock_tabulate.assert_called_once_with(expected_rows, headers="keys", tablefmt="grid")
        mock_print.assert_called_once_with(mock_tabulate.return_value)


    @patch("expense_tracker.tabulate")
    @patch("builtins.print")
    def test_list_expenses_when_no_category_matches(self, mock_print, mock_tabulate):
        args = argparse.Namespace(category="travel")
        self.exp_tracker.list_expenses(args)

        mock_tabulate.assert_called_once_with([], headers="keys", tablefmt="grid")
        mock_print.assert_called_once_with(mock_tabulate.return_value)


    #----------------------------------------------------------------------------------------------------
    # summary_expenses
    #----------------------------------------------------------------------------------------------------

    @patch("builtins.print")
    def test_summary_all_expenses(self, mock_print):
        args = argparse.Namespace(month=None)
        self.exp_tracker.summary_expenses(args)

        mock_print.assert_called_once_with("Total expenses: $1040.12")


    @patch("expense_tracker.datetime.datetime", FakeDate)
    @patch("builtins.print")
    def test_summary_expenses_for_month(self, mock_print):
        args = argparse.Namespace(month=9)
        self.exp_tracker.summary_expenses(args)

        mock_print.assert_called_once_with("Total expenses for September: $40.12")


    @patch("expense_tracker.datetime.datetime", FakeDate)
    @patch("builtins.print")
    def test_summary_month_with_no_expenses(self, mock_print):
        args = argparse.Namespace(month=10)
        self.exp_tracker.summary_expenses(args)

        mock_print.assert_called_once_with(" October has no expenses")


    @patch("expense_tracker.datetime.datetime", FakeDate)
    @patch("builtins.print")
    def test_summary_excludes_expenses_from_other_years(self, mock_print):
        self.exp_tracker.expenses.append(Expense(id=4, date=datetime.datetime(2025, 9, 27), description="Old expense", amount=500.0, category="groceries"))

        args = argparse.Namespace(month=9)
        self.exp_tracker.summary_expenses(args)

        mock_print.assert_called_once_with("Total expenses for September: $40.12")

   #----------------------------------------------------------------------------------------------------
    # export_expenses
    #----------------------------------------------------------------------------------------------------
    @patch("builtins.print")
    def test_export_expenses_successfully(self, mock_print):
        args = argparse.Namespace(output="./export.csv")
        expected_path = Path("./export.csv").expanduser().resolve()

        self.exp_tracker.export_expenses(args)

        self.expense_db.export_database.assert_called_once_with(expected_path, self.exp_tracker.expenses)
        mock_print.assert_called_once_with(f"Expenses exported successfully to {expected_path}")

    @patch("builtins.print")
    def test_export_expenses_when_database_fails(self, mock_print):
        args = argparse.Namespace(output="./export.csv")
        self.expense_db.export_database.side_effect = FileExistsError("File already exists")

        with self.assertRaises(FileExistsError):
            self.exp_tracker.export_expenses(args)

        self.expense_db.export_database.assert_called_once_with(Path("./export.csv").expanduser().resolve(), self.exp_tracker.expenses)
        mock_print.assert_called_once_with("Failed to export expenses")

    # we could stop the patches in teardown but that is not great since we started them in setup(). self.add_cleanup is more robust way of doing this
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

# Python provides us with three ways to call patch():

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

# when we write self.autospeced_expense_bd_class_mock.return_value we're accessing the mock instance that will be returned when our production code calls ExpenseDatabase()
# 3. Why can't we omit the first .return_value?
# Suppose we write:
# self.autospeced_expense_bd_class_mock.load_database.return_value = self.expenses

# we're trying to configure load_database() directly on the mocked class.
# But production code doesn't call:
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