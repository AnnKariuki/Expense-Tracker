# CSV representation:
# month, year, budget

#             ↕ serialization/deserialization

# ExpenseTracker representation:
# {(month, year): budget}

from pathlib import Path
import csv
import datetime
import tempfile
import os
class BudgetDatabase:
    budget_db_path = Path.cwd() / "budgets.csv"

    def load_database(self) -> dict[tuple[int,int], float]:
        budgets = {}
        try: 
            with open(self.budget_db_path, newline="") as csv_file:
                reader = csv.DictReader(csv_file)
                for line in reader:
                    month = int(line["month"])
                    year = int(line["year"])
                    budget = float(line["budget"])
                    budgets[(month, year)] = budget
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"problem when loading budget database, {e}")
            raise
        # made sure python and the editor are looking at thr same file
        # print("READING FROM:", self.budget_db_path) # here we got this from path.cwd meaning the directory python is currently running from
        # print("RESOLVED PATH:", self.budget_db_path.resolve()) # produce the absolute, resolved path to that file. so python is looking at the correct file
        # print(f"are we loading the correct thing {budgets}")
        return budgets

    def save_database(self, budgets: dict[tuple[int,int], float]) -> None:
        # atomic updates to csv file to prevent data loss or currupted/incomplete file due to the program crashing. store in fake file until write is successful then replace temp file with real file
        temp = tempfile.NamedTemporaryFile(newline="", suffix=".csv", delete=False, mode="w", dir=self.budget_db_path.parent)

        try: 
            with temp:
                fieldnames = ["month", "year", "budget"]
                writer = csv.DictWriter(temp, fieldnames=fieldnames)
                writer.writeheader()
                for (month, year), budget in budgets.items(): #for key, value in budgets.items(): python let's you unpack the values directly no need for index accessing
                    budget_row = {"month":str(month), "year":str(year), "budget": budget}
                    writer.writerow(budget_row)
            # do this when we have exited the temp context manager meaning temp is closed and now replace with real
            os.replace(temp.name, self.budget_db_path)
        except:
            os.unlink(temp.name) # cleanup temp file if os.replace fails
            raise




# month | year | budget.
# def write_db():
#     DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
#     budget_db_path = Path.cwd() / "budgets.csv"
#     with open(budget_db_path, "w", newline="") as csv_file:
#         fieldnames = ["month", "year", "budget"]
#         writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerow({"month": int(3), "year":str(datetime.datetime.now().year), "budget": str(100)})
#         writer.writerow({"month": int(4), "year":str(datetime.datetime.now().year), "budget": str(100)})

# write_db()

# should we give them the chance to input which month they want to place the budget on or just stick to datetime.now where we do it by ourselves. 
# instruction was "Allow users to set a budget for each month and show a warning when the user exceeds the budget." so maybe yes --month

# decided on having them give a month cause using .now() effectively becomes budget for current month always

# user will provide month and year of the budget they want to set
# budget is a float
# internally we will use ints to represent the month but wehn dispaying to user we will use month strings

# BudgetDatabase().save_database({(3, 2026): float('100'), (4, 2026): float('100')})
