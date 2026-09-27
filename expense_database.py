# persistence
# load_database()
# save_database()
# populate_database()
# is_database_empty()
# serialization/deserialization
# expense tracker should not know the database is a csv file so we need to return something that hides this implementation so we return a list of expenses.
# It doesn't care whether those objects originally came from CSV, JSON, SQLite, PostgreSQL, etc.
from pathlib import Path
import csv
from expense import Expense
import datetime
import tempfile
import os

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class ExpenseDatabase:

    db_path = Path.cwd() / "expenses.csv"

    def load_database(self) -> list[Expense]:
        expenses = []
        try: 
            with open(self.db_path, newline='') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                for line in csv_reader:
                    row = {
                        "id": int(line['id']),
                        "date": datetime.datetime.strptime(line['date'], DATE_FORMAT),
                        "description": line['description'],
                        "amount": float(line['amount']),
                        "category": line['category']
                    }
                    expense = Expense(**row)
                    expenses.append(expense)
        except FileNotFoundError:
            return [] # save_db uses mode=w which will create the file
        except Exception as e:
            print(f"An error occured when loading database {e}")
            # raise here re-raises the original exception with its traceback not the generic Exception so if it's valueerror that is what will be raised.
            raise
        return expenses

    def save_database(self, expenses: list[Expense]) -> None:
        # atomic replacement to help with transaction atomicity - write operations either comp]etely fail or succeed. os.replace After replacement, the source file no longer exists, 
        # and the destination contains the source file's content. write to a temporary file then atomically replace the target. This ensures the target is always in a consistent state.
        temp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="", dir=self.db_path.parent) # this creates and opens a new file so dont open() in the with block. 
        # mode here is w not w+b because csv writers expect strings not bytes
        # os.replace() is reliably atomic when the source and destination are on the same filesystem. 
        # Putting the temp file in the same directory ensures that. when using tempfile you use uses the operating system's default temporary directory
        try: 
            with temp: # temp files/dirs from tempfile module can be used as context managers
                fieldnames = ["id","date", "description", "amount", "category"]
                writer = csv.DictWriter(temp, fieldnames=fieldnames)
                writer.writeheader()
                for expense in expenses:
                    row = {
                        "id": str(expense.id),
                        "date": expense.date.strftime(DATE_FORMAT),
                        "description": expense.description,
                        "amount": str(expense.amount),
                        "category": expense.category
                    }
                    # have to pass in a dictionary to writerow
                    writer.writerow(row)
            # temp is closed at this point.
            # Replace the old database only after the entire new CSV
            # has been successfully written.
            os.replace(temp.name, self.db_path)
        except:
            # Clean up temp file if replace fails. we can access the file after we exited the context manager because we did delete=False so it was not immediately deleted
            os.unlink(temp.name) # used to permanently delete a file path from the file system
            raise
