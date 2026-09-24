# persistence
# load_database()
# save_database()
# populate_database()
# is_database_empty()
# expense tracker should not know the database is a csv file so we need to return something that hides this implementation
from pathlib import Path
import csv
from expense import Expense
import datetime
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
class ExpenseDatabase:

    db_path = Path.cwd() / "expenses.csv"

    def load_database(self) -> list[Expense]:
        expenses = []
        with open(self.db_path, newline='') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for line in csv_reader:
                row = {
                    "id": int(line['id']),
                    "date": datetime.datetime.strptime(line['date'], DATE_FORMAT),
                    "description": line['description'],
                    "amount": int(line['amount']) if line['amount'].isdigit() else float(line['amount']),
                }
                expense = Expense(**row)
                expenses.append(expense)
        return expenses
        


# for testing purposes
def write_database():
    db_path = Path.cwd() / "expenses.csv"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    with open(db_path, 'w', newline='') as csvfile:
        fieldnames = ['id', 'date', 'description', 'amount']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerow({'id':'1', "date": datetime.datetime.now().strftime(DATE_FORMAT), 'description': 'get rich', 'amount': 100})
        writer.writerow({'id':'2', "date": datetime.datetime.now().strftime(DATE_FORMAT), 'description': 'get really rich', 'amount': 10000000})


write_database()

result = ExpenseDatabase().load_database()
print(result[0].id)

