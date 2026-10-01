import unittest
#Using Python's tempfile module in tests ensures that mock files or sandbox directories are secure, isolated, and automatically cleaned up after the test completes
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from budget_database import BudgetDatabase
import csv
import os
class TestLoadBudgetDatabase(unittest.TestCase):
    # new_callable allows you to specify a different class, or callable object, that will be called to create the new object. By default AsyncMock is used for async functions and MagicMock for the rest.
    @patch('builtins.open', new_callable=mock_open, 
           read_data="month,year,budget\n3,2026,100.0\n4,2026,100.0\n9,2026,30.0")
    def test_load_database_loads_data(self, mock_file):
        # here we are mocking the open function to return the csv data above
        expected_result = {
            (3,2026):100.0,
            (4,2026):100.0,
            (9,2026):30.0,
        }

        result = BudgetDatabase().load_database()
        self.assertEqual(expected_result, result)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_file_not_found_load_database(self, mock_file):
        result = BudgetDatabase().load_database()
        self.assertEqual(result, {})

    @patch("builtins.open", side_effect=PermissionError)
    def test_generic_exception_is_reraised(self, mock_file):
        with self.assertRaises(PermissionError):
            BudgetDatabase().load_database()    

    @patch('builtins.open', new_callable=mock_open, 
           read_data="")
    def test_load_database_on_empty_database(self, mock_file):
        # here we are mocking the open function to return the csv data above
        result = BudgetDatabase().load_database()
        self.assertEqual(result, {})

class TestSaveBudgetDatabase(unittest.TestCase):
    def setUp(self):
        # unittest uses this to enter the supplied context manager. If successful, also add its __exit__() method as a cleanup function by addCleanup() and 
        # return the result of the __enter__() method. in our case __enter__ returns object.name which is the pathname of the directory.
        self.temp_dir = self.enterContext(tempfile.TemporaryDirectory()) # /var/folders/mc/r9_6bly179l01kr9fyjbrv1h0000gn/T/tmpxufs4ivb
        self.temp_dir_path = Path(self.temp_dir) # turn the path name into a path object
        self.temp_database_path = self.temp_dir_path / "budgets.csv"
        self.db = BudgetDatabase()
        self.db.budget_db_path = self.temp_database_path

    def test_save_database_success(self):
        budgets = {
            (3,2026):100.0,
            (4,2026):100.0,
            (9,2026):30.0,
        }
        self.db.save_database(budgets)
        result = {}     
        with open(self.db.budget_db_path, newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for line in reader:
                month = int(line["month"])
                year = int(line["year"])
                budget = float(line["budget"])
                result[(month, year)] = budget
        self.assertEqual(budgets, result)

    # @patch("os.replace")
    # def test_save_database_handles_exception(self, mocked_replace):
    #     mocked_replace.side_effect = OSError
    #     with self.assertRaises(OSError):
    #         self.db.save_database({})

    @patch("os.replace")
    def test_save_database_cleans_up_temp_file_and_reraises_exception(self, mocked_replace):
        mocked_replace.side_effect = OSError
        with self.assertRaises(OSError):
            self.db.save_database({})
        # remember when os.replace fails budges.csv(self.db.budget_db_path) is never created so the test below will always pass
        # self.assertFalse(os.path.exists(self.db.budget_db_path))

        # check if temp dir is empty 
        self.assertEqual(os.listdir(self.temp_dir), [])

class TestIntegrationSaveAndLoadDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = self.enterContext(tempfile.TemporaryDirectory())
        self.db = BudgetDatabase()
        self.db.budget_db_path = Path(self.temp_dir) / "budgets.csv"

    def test_save_and_load_database_success(self):
        budgets = {
            (3,2026):100.0,
            (4,2026):100.0,
            (9,2026):30.0,
        }
        self.db.save_database(budgets)
        results = self.db.load_database()
        # I can compare this 2 dicts because they have value based equality
        self.assertEqual(results,budgets)

    

if __name__ == '__main__':
    unittest.main()



# 1. Why PermissionError works but UnicodeDecodeError doesn't
# When you write side_effect=PermissionError, you're giving Mock an exception class.
# When the mocked open() gets called, Mock essentially tries to raise an instance of that exception.
# PermissionError can be constructed with no arguments, so that works.
# UnicodeDecodeError cannot. Python requires information about the failed decoding operation: the encoding, bytes being decoded, start position, end position, and reason.
# That's exactly what your error is telling you:
# TypeError: function takes exactly 5 arguments (0 given)

# So your load_database() isn't the problem. The mock tried to construct UnicodeDecodeError with no arguments and failed before it could raise one.
# If you want to simulate UnicodeDecodeError, you need to give side_effect an already-created UnicodeDecodeError instance with its required information, rather than just giving it the class.
# 2. Why adding new_callable=mock_open breaks
# These two concepts do different jobs.
# When you do:
# patch(..., side_effect=PermissionError)
# patch creates its normal MagicMock to replace open, and configures that mock's side_effect.
# But when you say:
# new_callable=mock_open
# you're telling patch:
# Don't create the normal mock. Call mock_open(...) to create my replacement.

# Then patch tries to pass your additional configuration into mock_open.
# In your case, it effectively tries to create the replacement using mock_open(side_effect=...).
# But mock_open doesn't accept a side_effect parameter. That's why you get:
# TypeError: mock_open() got an unexpected keyword argument 'side_effect'

# So for these exception tests, you don't need mock_open at all.
# You're testing:
# open()
#   ↓
# raises PermissionError
#   ↓
# load_database catches it in generic Exception
#   ↓
# re-raises it

# No fake file ever needs to exist because open() fails immediately.
# mock_open is useful for your other test where you want:
# open()
#   ↓
# succeeds
#   ↓
# returns a fake file
#   ↓
# fake file contains CSV data
#   ↓
# DictReader reads it

# So the distinction is:
# Need open() to fail? A normal patched mock with side_effect is enough.
# Need open() to succeed and behave like a file? That's where mock_open becomes useful.