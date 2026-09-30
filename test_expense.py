# we always want to test behavior and state not implementation details
# test the class creates instances correctly
# we pick one invalid argument to represent all invalid values you don't need to test the class
# rejects strings, ints. just pick one representative
import unittest
from expense import Expense
import datetime

class TestExpense(unittest.TestCase):
    def setUp(self):
        # I will create an Expense onject that will be used in the test cases to test
        # the class
        self.date = datetime.datetime.now()
        self.expense = Expense(
            id = 1,
            date = self.date,
            description = "visit New York",
            amount = 4000.0,
            category = "Travel"
        )

    def test_create_expense(self):
        self.assertEqual(self.expense.id, 1)
        self.assertEqual(self.expense.date, self.date)
        self.assertEqual(self.expense.description, "visit New York")
        self.assertEqual(self.expense.amount, 4000.0)
        self.assertEqual(self.expense.category, "travel")

    def test_id_is_read_only(self):
        with self.assertRaises(AttributeError):
            self.expense.id = 2
        
    def test_date_rejects_non_datetime(self):
        with self.assertRaises(ValueError):
            self.expense.date = "March 4 2026"

    def test_description_rejects_non_strings(self):
        with self.assertRaises(ValueError):
            self.expense.description = 4

    def test_amount_rejects_non_floats(self):
        with self.assertRaises(ValueError):
            self.expense.amount = 10

    def test_amount_must_be_non_negative(self):
        with self.assertRaises(ValueError):
            self.expense.amount = -1

    # test the boundary
    def test_amount_can_be_zero(self):
        self.expense.amount = 0.0

    def test_category_rejects_non_strings(self):
        with self.assertRaises(ValueError):
            self.expense.category = 4

    def test_category_is_normalized_to_lowercase(self):
        self.expense.category = "FOOD"
        self.assertEqual(self.expense.category, "food")


if __name__ == '__main__':
    unittest.main()