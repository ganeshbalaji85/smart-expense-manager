import mysql.connector
from functools import reduce
from abc import ABC, abstractmethod
from datetime import datetime

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="expense_db"
)

cursor = conn.cursor()


class BaseUser(ABC):

    @abstractmethod
    def display(self):
        pass


class User(BaseUser):

    def __init__(self, name):
        self.__name = name   

    def create_user(self):
        query = "INSERT INTO users (name) VALUES (%s)"
        cursor.execute(query, (self.__name,))
        conn.commit()
        print("User Added Successfully!")

    def display(self):
        print(f"User: {self.__name}")


class Expense(User):

    def __init__(self, name):
        super().__init__(name)

    def add_expense(self, user_id, amount, category, description, date):
        query = """
        INSERT INTO expenses (user_id, amount, category, description, date)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, amount, category, description, date))
        conn.commit()
        print("Expense Added!")

    def view_expenses(self, user_id):
        query = """
        SELECT u.name, e.amount, e.category, e.description, e.date
        FROM users u
        JOIN expenses e ON u.user_id = e.user_id
        WHERE u.user_id = %s
        """
        cursor.execute(query, (user_id,))
        data = cursor.fetchall()

        for row in data:
            print(row)

        return data

    def filter_expenses(self, expenses, category=None, date=None):
        filtered = [
            exp for exp in expenses
            if (category is None or exp[2] == category) and
               (date is None or str(exp[4]) == date)
        ]
        return filtered

    def total_expense(self, expenses):
        amounts = list(map(lambda x: x[1], expenses))
        total = reduce(lambda a, b: a + b, amounts, 0)
        return total

    def category_summary(self, expenses):
        categories = set(map(lambda x: x[2], expenses))

        summary = {
            cat: sum([e[1] for e in expenses if e[2] == cat])
            for cat in categories
        }
        return summary

    
    def update_expense(self, exp_id, amount):
        query = "UPDATE expenses SET amount = %s WHERE exp_id = %s"
        cursor.execute(query, (amount, exp_id))
        conn.commit()
        print("Updated!")


    def delete_expense(self, exp_id):
        query = "DELETE FROM expenses WHERE exp_id = %s"
        cursor.execute(query, (exp_id,))
        conn.commit()
        print("Deleted!")

    
    def monthly_report(self, expenses):
        report = {}

        for e in expenses:
            month = e[4].strftime("%Y-%m")
            report[month] = report.get(month, 0) + e[1]

        return report

    def highest_expense(self, expenses):
        return reduce(lambda a, b: a if a[1] > b[1] else b, expenses)

    
    def display(self):
        print("Expense Manager User")


def smart_insight(summary):
    if not summary:
        return "No data available"

    max_category = max(summary, key=summary.get)
    return f"You are spending too much on {max_category}!"


if __name__ == "__main__":

    exp = Expense("Arun")

    

    data = exp.view_expenses(1)

    print("\n--- FILTERED (Food) ---")
    print(exp.filter_expenses(data, category="Food"))

    print("\n--- TOTAL ---")
    print(exp.total_expense(data))

    print("\n--- CATEGORY SUMMARY ---")
    summary = exp.category_summary(data)
    print(summary)

    print("\n--- MONTHLY REPORT ---")
    print(exp.monthly_report(data))

    print("\n--- HIGHEST EXPENSE ---")
    print(exp.highest_expense(data))

    print("\n--- SMART INSIGHT ---")
    print(smart_insight(summary))