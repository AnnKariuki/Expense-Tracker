import unittest
import tempfile
from unittest.mock import patch, mock_open
from expense import Expense
from expense_database import ExpenseDatabase
import csv
from pathlib import Path
import os
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
import datetime
class TestLoadDatabase(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data = "id,date,description,amount,category\n1,2026-09-27 14:50:23,Chipotle,20.0,groceries\n2,2026-09-27 15:19:49,Chipotle,20.123,groceries")
    def test_load_database_success(self, mocked_file):
        expected_result = [Expense(id=1, date=datetime.datetime.strptime('2026-09-27 14:50:23', DATE_FORMAT), description="Chipotle", amount=20.0, category ="groceries"),
                           Expense(id=2, date=datetime.datetime.strptime('2026-09-27 15:19:49', DATE_FORMAT), description="Chipotle", amount=20.123, category ="groceries")]

        result = ExpenseDatabase().load_database()
        self.assertEqual(expected_result, result)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_database_file_not_found_returns_empty_list(self, mocked_file):
        result = ExpenseDatabase().load_database()

        self.assertEqual(result, [])

    @patch("builtins.open", side_effect=PermissionError)
    def test_load_database_generic_exception_is_reraised(self, mocked_file):
        with self.assertRaises(PermissionError):
            ExpenseDatabase().load_database()

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=""
    )
    def test_load_database_on_empty_database(self, mocked_file):
        result = ExpenseDatabase().load_database()

        self.assertEqual(result, [])

class TestSaveDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = self.enterContext(tempfile.TemporaryDirectory())
        self.temp_dir_path = Path(self.temp_dir)
        self.temp_database_path = self.temp_dir_path / "expenses.csv"

        self.db = ExpenseDatabase()
        self.db.db_path = self.temp_database_path

    def test_save_database_success(self):
        expenses = [Expense(id=1,date=datetime.datetime.strptime("2026-09-27 14:50:23",DATE_FORMAT),description="Chipotle",amount=20.0,category="groceries"),
                    Expense(id=2,date=datetime.datetime.strptime("2026-09-27 15:19:49",DATE_FORMAT),description="Chipotle",amount=20.123,category="groceries")]

        self.db.save_database(expenses)
        result = []

        with open(self.db.db_path, newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for line in reader:
                result.append(Expense(id=int(line["id"]),date=datetime.datetime.strptime(line["date"],DATE_FORMAT),description=line["description"],amount=float(line["amount"]),category=line["category"]))
        self.assertEqual(expenses, result)

    @patch("os.replace")
    def test_save_database_cleans_up_temp_file_and_reraises_exception(self, mocked_replace):
        mocked_replace.side_effect = OSError
        with self.assertRaises(OSError):
            self.db.save_database([])
        self.assertEqual(os.listdir(self.temp_dir), [])


class TestIntegrationSaveAndLoadDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = self.enterContext(tempfile.TemporaryDirectory())
        self.db = ExpenseDatabase()
        self.db.db_path = Path(self.temp_dir) / "expenses.csv"

    def test_save_and_load_database_success(self):
        expenses = [Expense(id=1,date=datetime.datetime.strptime("2026-09-27 14:50:23",DATE_FORMAT),description="Chipotle",amount=20.0,category="groceries"),
                    Expense(id=2,date=datetime.datetime.strptime("2026-09-27 15:19:49",DATE_FORMAT),description="Chipotle",amount=20.123,category="groceries")]

        self.db.save_database(expenses)
        result = self.db.load_database()
        self.assertEqual(expenses, result)

class TestExportDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = self.enterContext(tempfile.TemporaryDirectory())
        self.temp_dir_path = Path(self.temp_dir)
        self.output_path = self.temp_dir_path / "export.csv"

        self.db = ExpenseDatabase()

        self.expenses = [
            Expense(id=1,date=datetime.datetime.strptime("2026-09-27 14:50:23",DATE_FORMAT),description="Chipotle",amount=20.0,category="groceries"),
            Expense(id=2,date=datetime.datetime.strptime("2026-09-27 15:19:49",DATE_FORMAT),description="Chipotle",amount=20.123,category="groceries")
        ]

    def test_export_database_success(self):
        self.db.export_database(self.output_path, self.expenses)

        result = []

        with open(self.output_path, newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for line in reader:
                result.append(Expense(id=int(line["id"]),date=datetime.datetime.strptime(line["date"],DATE_FORMAT),description=line["description"],amount=float(line["amount"]),category=line["category"]))

        self.assertTrue(self.output_path.exists())
        self.assertEqual(self.expenses, result)

    def test_export_database_does_not_overwrite_existing_file(self):
        # write_text -> Open the file in text mode, write to it, and close the file.
        self.output_path.write_text("existing data")

        with self.assertRaises(FileExistsError):
            self.db.export_database(self.output_path, self.expenses)

        self.assertEqual(self.output_path.read_text(), "existing data")

    def test_export_database_with_empty_expenses(self):
        self.db.export_database(self.output_path, [])

        with open(self.output_path, newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            result = list(reader)

            self.assertEqual(reader.fieldnames, ["id", "date", "description", "amount", "category"])

        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()