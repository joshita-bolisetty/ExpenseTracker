import csv
import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import Calendar
import calendar
import datetime as dt

class FutureDateException(Exception):
    pass

class Expense:

    def __init__(self):
        self.conn = sqlite3.connect("expense_tracker.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
                            create table if not exists User(
                                userid integer primary key autoincrement,
                                username text not null,
                                password text not null)
                            """
        )
        self.cursor.execute("""                            
                            CREATE TABLE IF NOT EXISTS expenses (
                                user TEXT NOT NULL,
                                id INTEGER PRIMARY KEY autoincrement,
                                category TEXT NOT NULL,
                                name TEXT not null,
                                amount REAL NOT NULL,
                                date DATE NOT NULL)
                            """
        )
        self.conn.commit()

    def add_user(self, name):
        self.cursor.execute(
            "INSERT INTO User (username,password) VALUES (?,?)", (name, "123")
        )
        self.conn.commit()

    def get_all_users(self):
        self.cursor.execute("SELECT username,userid FROM User")
        return self.cursor.fetchall()

    def add_expense(self, user: str, category: str, name: str, amount: int, date: str):
        month, date, year = date.split("/")
        year = f"20{year}"
        date = f"{year}-{month}-{date}"
        if not amount.isdigit():
            raise ValueError("Amount must be a number")
        self.cursor.execute(
            "INSERT INTO expenses (user, category,name ,amount, date) VALUES (?,?, ?, ?, ?)",
            (user, category, name, amount, date),
        )
        self.conn.commit()

    def view_expenses(self, user: str, start_date: str, end_date: str):
        self.cursor.execute(
            "SELECT * FROM expenses WHERE user = ? AND date BETWEEN ? AND ?",
            (user, start_date, end_date),
        )
        return self.cursor.fetchall()

    def view_expenses_category(self, user: str, category: str):
        self.cursor.execute(
            "SELECT date,name,amount,category  FROM expenses WHERE user = ? AND category = ? order by date desc",
            (user, category),
        )
        return self.cursor.fetchall()

    def view_expenses_date(self, user: str, start_date: str, end_date: str):
        self.cursor.execute(
            "SELECT date, SUM(amount) FROM expenses WHERE user = ? AND date BETWEEN ? AND ? GROUP BY date",
            (user, start_date, end_date),
        )
        return self.cursor.fetchall()

    def view_expenses_month(self, user: str, year: str):
        self.cursor.execute(
            "SELECT substr(date, instr(date, '-')+1, 2) as month, SUM(amount) FROM expenses WHERE user = ? AND substr(date, 1, 4) = ? GROUP BY month",
            (user, year),
        )
        return self.cursor.fetchall()

    def view_expenses_year(self, user: str, start_date: str, end_date: str):
        self.cursor.execute(
            "SELECT strftime('%Y', date) AS year, SUM(amount) FROM expenses WHERE user = ? AND date BETWEEN ? AND ? GROUP BY year",
            (user, start_date, end_date),
        )
        return self.cursor.fetchall()

    def view_expenses_all(self, user: str):
        self.cursor.execute(
            "SELECT date,name,amount,category FROM expenses WHERE user = ? order by date desc", (user,)
        )
        return self.cursor.fetchall()

    def view_expenses_category_all(self, user: str):
        self.cursor.execute(
            "SELECT category, SUM(amount) FROM expenses WHERE user = ? GROUP BY category",
            (user,),
        )
        return self.cursor.fetchall()

    def view_expenses_category_month(self, user: str, month: str):
        self.cursor.execute(
            """
            SELECT category, SUM(amount) 
            FROM expenses 
            WHERE user = ? AND substr(date, instr(date, '-')+1, 2) = ? 
            GROUP BY category
            """,
            (user, month),
        )
        return self.cursor.fetchall()

    def view_expenses_category_month_year(self, user: str, month: str, year: str):
        self.cursor.execute(
            """
            SELECT category, SUM(amount) 
            FROM expenses 
            WHERE user = ? AND substr(date, 1, 4) = ? AND substr(date, instr(date, '-')+1, 2) = ? 
            GROUP BY category
            """,
            (user, year, month),
        )
        return self.cursor.fetchall()

    def view_expenses_category_year(self, user: str, year: str):
        self.cursor.execute(
            """
            SELECT category, SUM(amount) 
            FROM expenses 
            WHERE user = ? AND substr(date, 1, 4) = ? 
            GROUP BY category
            """,
            (user, year),
        )
        return self.cursor.fetchall()

class ExpenseTracker:
    
    def __init__(self) -> None:
        self.db = Expense()
        self.root = tk.Tk()
        self.root.withdraw()
        self.select_user()

    def user_menu(self, top):
        self.user_clicked = tk.StringVar()
        options = [x[0] for x in self.db.get_all_users()]
        self.user_clicked.set("--Select User--")
        tk.Label(top, text="User : ").grid(row=3, column=0)
        self.users = tk.OptionMenu(top, self.user_clicked, *options)
        self.users.grid(row=3, column=1)

    def select_user(self):
        top = tk.Toplevel(self.root)
        top.title("Select User")
        top.geometry("250x150")
        self.user_menu(top)
        submit_button = tk.Button(top, text="Submit", command=self.create_main_window)
        submit_button.grid(row=4, column=1, columnspan=2)
        tk.Button(top, text="Create User", command=self.create_user).grid(
            row=5,
            column=1,
            columnspan=2,
        )
        self.root.mainloop()

    def create_main_window(self):
        self.root.destroy()
        self.root = tk.Tk()
        self.root.title("Expense Tracker")
        self.root.geometry("350x300")

        tk.Label(self.root, text="Category : ").grid(row=1, column=0)
        self.category_clicked = tk.StringVar()
        self.category_clicked.set("--Select Category--")
        options = [
            "--Select Category--",
            "Food",
            "Rent",
            "Study",
            "Bill",
            "Groceries",
            "Personal",
            "Luxury",
            "Others",
        ]
        self.category_entry = tk.OptionMenu(self.root, self.category_clicked, *options)
        self.category_entry.grid(row=1, column=1, pady=(10, 0))

        tk.Label(self.root, text="Date : ").grid(row=4, column=0, pady=(10, 0))
        style = tk.ttk.Style()
        style.theme_use("clam") 
        style.configure(
            "TButton", background="lightblue", foreground="black", font=("Arial", 12)
        )

        style.configure(
            "TButton.Calendar",
            fieldbackground="white",
            selectbackground="blue",
            selectforeground="white",
        )
        style.configure("Treeview", border=1, borderwidth=1, relief="solid")
        self.date_picker = Calendar(self.root)
        self.date_picker.grid(row=4, column=1, pady=(10, 0))
        self.date_picker.bind("<<CalendarSelected>>", self.on_date_select)
        self.create_menu()
        tk.Button(self.root, text="Add Expense", command=self.add_expense).grid(
            row=5, column=1, pady=(10, 0)
        )
        self.root.mainloop()

    def create_user(self):
        top = tk.Toplevel(self.root)
        top.title("Create User")
        tk.Label(top, text="User Name:").grid(row=0, column=0)
        user_entry = tk.Entry(top)
        user_entry.grid(row=0, column=1)
        submit_button = tk.Button(
            top, text="Submit", command=lambda: self.add_user(user_entry.get(), top)
        )
        submit_button.grid(row=1, column=0, columnspan=2)

    def add_user(self, user_name, top):
        self.db.add_user(user_name)
        messagebox.showinfo("Success", "User added successfully!")
        self.users["menu"].delete(0, "end")
        new_choices = [x[0] for x in self.db.get_all_users()]
        for choice in new_choices:
            self.users["menu"].add_command(
                label=choice, command=tk._setit(self.user_clicked, choice)
            )
        top.destroy()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        expense_menu = tk.Menu(menubar, tearoff=0)
        expense_menu.add_command(label="View Expenses List", command=self.view_expense)
        expense_menu.add_command(
            label="View Expenses according to category", command=self.open_expense_viewer
        )
        expense_menu.add_command(
            label="View Monthly Expense Comparision",
            command=self.draw_monthly_expense_graph,
        )
        expense_menu.add_command(label="Export Expenses to File", command=self.export_expenses)
        menubar.add_cascade(label="Tools ", menu=expense_menu)
        self.root.config(menu=menubar)

    def on_date_select(self, event):
        selected_date = self.date_picker.get_date()
        today = dt.datetime.today().date()

        try:
            selected_date_obj = dt.datetime.strptime(selected_date, "%m/%d/%y")
            if selected_date_obj.date() > today:
                raise FutureDateException
        except FutureDateException:
            self.handle_future_date_exception()

    def handle_future_date_exception(self):
        messagebox.showerror(
            "Invalid Date",
            "Future date selection is not allowed!\nResetting date to current date!",
        )
        self.date_picker.selection_set(dt.datetime.today().date())

    def validate(self):
        user = self.user_clicked.get()
        category = self.category_clicked.get()
        date = self.date_picker.get_date()
        if user == "" or user == "--Select User--":
            raise ValueError("User field is empty")
        if category == "--Select Category--":
            raise ValueError("Category field is empty")
        if date == "":
            raise ValueError("Date field is empty")

    def add_expense(self):
        try:
            self.validate()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        def submit():
            user = self.user_clicked.get()
            category = self.category_clicked.get()
            name = self.expense_name_entry.get()
            amount = self.amount_entry.get()
            date = self.date_picker.get_date()
            try:
                self.db.add_expense(user, category, name, amount, date)
                messagebox.showinfo("Success", "Expense Added")
                top.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return

        top = tk.Toplevel(self.root)
        tk.Label(top, text="Name : ").grid(row=2, column=0)
        self.expense_name_entry = tk.Entry(top)
        self.expense_name_entry.grid(row=2, column=1)
        tk.Label(top, text="Amount : ").grid(row=3, column=0)
        self.amount_entry = tk.Entry(top)
        self.amount_entry.grid(row=3, column=1)
        tk.Button(top, text="Submit", command=submit).grid(row=4, column=0)
   
    def view_expense(self):
        user = self.user_clicked.get()
        if user is None or user == "" or user == "--Select User--":
            messagebox.showerror("Error", "Select User ")
            return
        top = tk.Toplevel(self.root)
        category = self.category_clicked.get()
        if category != "--Select Category--":
            data = self.db.view_expenses_category(user, category)
        else:
            data = self.db.view_expenses_all(user)
        headings = [["Date", "Name", "Amount", "Category"]]
        table = tk.ttk.Treeview(
            top,
            columns=(1, 2, 3, 4),
            show="headings",
            height=len(data),
            style="Treeview",
        )
        table.grid(row=len(data) + 1, column=0, columnspan=4)
        table.heading(1, text="Date")
        table.heading(2, text="Name")
        table.heading(3, text="Amount")
        table.heading(4, text="Category")
        for row in data:
            table.insert("", "end", values=row)

    def draw_monthly_expense_graph(self):
        top = tk.Toplevel(self.root)
        top.title("Monthly Expense Graph")
        top.geometry("600x600")
        self.selected_year = tk.StringVar(top)
        self.selected_year.set("--Select Year--")
        cur_year = dt.datetime.today().year
        year_option = tk.OptionMenu(top, self.selected_year, *range(cur_year, 1989, -1))
        year_option.grid(row=0, column=1)

        def generate_graph():
            year = self.selected_year.get()
            if year != "--Select Year--":
                data = self.db.view_expenses_month(self.user_clicked.get(), year)
                months_data = dict(data)
                all_months = [calendar.month_abbr[i] for i in range(1, 13)]
                month_dict = {
                    "Jan": "1-",
                    "Feb": "2-",
                    "Mar": "3-",
                    "Apr": "4-",
                    "May": "5-",
                    "Jun": "6-",
                    "Jul": "7-",
                    "Aug": "8-",
                    "Sep": "9-",
                    "Oct": "10",
                    "Nov": "11",
                    "Dec": "12",
                }
                amounts = [
                    months_data.get(month_dict[month], 0) for month in all_months
                ]
                fig, ax = plt.subplots()
                ax.bar(all_months, amounts)
                ax.bar(all_months, amounts)
                ax.set_title(f"Monthly Expenses for {year}")
                ax.set_xlabel("Month")
                ax.set_ylabel("Amount")
                canvas = FigureCanvasTkAgg(fig, master=top)
                canvas.get_tk_widget().grid(row=1, column=0, columnspan=2)

        generate_button = tk.Button(top, text="Generate Graph", command=generate_graph)
        generate_button.grid(row=2, column=0, columnspan=2)
        top.mainloop()

    def open_expense_viewer(self):
        top = tk.Toplevel(self.root)
        top.title("View Expenses")
        top.geometry("250x150")
        self.selected_month = tk.StringVar(top)
        self.selected_month.set("--Select Month--")
        self.selected_year = tk.StringVar(top)
        self.selected_year.set("--Select Year--")
        self.month_dict = {
            "Jan": "1-",
            "Feb": "2-",
            "Mar": "3-",
            "Apr": "4-",
            "May": "5-",
            "Jun": "6-",
            "Jul": "7-",
            "Aug": "8-",
            "Sep": "9-",
            "Oct": "10",
            "Nov": "11",
            "Dec": "12",
        }
        months_with_initial_option = ["--Select Month--"] + list(self.month_dict.keys())
        month_option = tk.OptionMenu(
            top, self.selected_month, *months_with_initial_option
        )
        month_option.grid(row=1, column=1)
        cur_year = dt.datetime.today().year
        years_with_initial_option = ["--Select Year--"] + [
            str(year) for year in range(cur_year, 1989, -1)
        ]
        year_option = tk.OptionMenu(top, self.selected_year, *years_with_initial_option)
        year_option.grid(row=2, column=1)
        button = tk.Button(
            top, text="View Expenses", command=self.view_selected_expenses
        )
        button.grid(row=3, column=0, columnspan=2)

    def view_selected_expenses(self):
        month = self.selected_month.get()
        year = self.selected_year.get()
        if month != "--Select Month--" and year != "--Select Year--":
            data = self.db.view_expenses_category_month_year(
                self.user_clicked.get(), self.month_dict[month], year
            )
        elif month != "--Select Month--":
            data = self.db.view_expenses_category_month(
                self.user_clicked.get(), self.month_dict[month]
            )
        elif year != "--Select Year--":
            data = self.db.view_expenses_category_year(self.user_clicked.get(), year)
        else:
            data = self.db.view_expenses_category_all(self.user_clicked.get())
        self.draw_category_expense_pie_chart(data)

    def draw_category_expense_pie_chart(self, data):
        top = tk.Toplevel(self.root)
        top.title("Category Expense Pie Chart")
        if not data or len(data) == 0:
            tk.Label(top, text="No data to display").pack()
            return
        categories, amounts = zip(*data)
        fig, ax = plt.subplots()
        labels = [
            f"{category}: {amount}" for category, amount in zip(categories, amounts)
        ]
        ax.pie(amounts, labels=labels, autopct="%1.1f%%")
        ax.set_title("Expenses by Category")
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def export_expenses(self):
        data = self.db.view_expenses_all(self.user_clicked.get())
        with open(
            f"expenses_{self.user_clicked.get().replace(' ','_')}.csv", "w", newline=""
        ) as file:
            writer = csv.writer(file)
            writer.writerow(
                ["Date", "Expense", "Amount", "Category"]
            )
            writer.writerows(data)
        messagebox.showinfo("Success", "Expenses exported successfully!")

if __name__ == "__main__":
    ExpenseTracker()
