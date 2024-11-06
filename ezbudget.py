import sqlite3
from getpass import getpass
import datetime
from tabulate import tabulate

# ASCII Welcome Message
def show_welcome():
    print("""

 /$$$$$$$$           /$$$$$$$                  /$$                       /$$    
| $$_____/          | $$__  $$                | $$                      | $$    
| $$       /$$$$$$$$| $$  \\ $$ /$$   /$$  /$$$$$$$  /$$$$$$   /$$$$$$  /$$$$$$  
| $$$$$   |____ /$$/| $$$$$$$ | $$  | $$ /$$__  $$ /$$__  $$ /$$__  $$|_  $$_/  
| $$__/      /$$$$/ | $$__  $$| $$  | $$| $$  | $$| $$  \\ $$| $$$$$$$$  | $$    
| $$        /$$__/  | $$  \\ $$| $$  | $$| $$  | $$| $$  | $$| $$_____/  | $$ /$$
| $$$$$$$$ /$$$$$$$$| $$$$$$$/|  $$$$$$/|  $$$$$$$|  $$$$$$$|  $$$$$$$  |  $$$$/
|________/|________/|_______/  \\______/  \\_______/ \\____  $$ \\_______/   \\___/  
                                                   /$$  \\ $$                    
                                                  |  $$$$$$/                    
                                                   \\______/                     
                                                                 

Welcome to EzBudget! Let's make budgeting easy and accessible. EzBudget helps you effortlessly track your income and expenses to manage your finances better.

Begin by registering and creating an account. It will take less than 2 minutes!
""")

# Initialize the database
conn = sqlite3.connect('ezbudget.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                  username TEXT PRIMARY KEY,
                  password TEXT NOT NULL,
                  currency TEXT DEFAULT '$',
                  security_question TEXT NOT NULL,
                  security_answer TEXT NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  type TEXT CHECK(type IN ('income', 'expense')),
                  amount REAL,
                  category TEXT,
                  description TEXT,
                  date TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
conn.commit()

# User Authentication (Login and Register)
def register():
    username = input("Enter a new username: ")
    password = getpass("Enter a new password: ")
    currency = input("Choose your currency symbol (default is $): ") or '$'
    security_question = input("Enter a security question for account recovery (e.g., 'What is your favorite color?'): ")
    security_answer = input("Enter the answer to your security question: ")

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        print("Username already exists. Try logging in.")
        return False
    
    cursor.execute("INSERT INTO users (username, password, currency, security_question, security_answer) VALUES (?, ?, ?, ?, ?)", 
                   (username, password, currency, security_question, security_answer))
    conn.commit()
    print("Registration successful! Welcome to EzBudget.")
    return True

def login():
    username = input("Enter username: ")
    password = getpass("Enter password: ")

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    if cursor.fetchone():
        print("Login successful! Welcome back.")
        return username
    else:
        print("Invalid credentials.")
        return None

# Account Recovery to Reset Password
def recover_account():
    username = input("Enter your username: ")
    
    cursor.execute("SELECT security_question, security_answer FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    
    if result:
        security_question, correct_answer = result
        print(f"Security Question: {security_question}")
        answer = input("Enter the answer to your security question: ")

        if answer == correct_answer:
            new_password = getpass("Enter a new password: ")
            cursor.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
            conn.commit()
            print("Password reset successful! You can now log in with your new password.")
        else:
            print("Incorrect answer. Password reset failed.")
    else:
        print("Username not found. Please register for an account.")

# Adding Income and Expenses
def add_transaction(username):
    cursor.execute("SELECT currency FROM users WHERE username=?", (username,))
    currency = cursor.fetchone()[0]

    print("\nAdding a new transaction. Leave fields blank or type 'cancel' to return to the menu.")
    
    # Prompt for transaction type with validation
    while True:
        trans_type = input("Enter type (income/expense): ").lower()
        if trans_type in ['income', 'expense']:
            break
        elif trans_type == 'cancel':
            print("Transaction canceled. Returning to previous menu.")
            return
        else:
            print("Invalid input. Please enter 'income' or 'expense', or type 'cancel' to go back.")

    # Prompt for amount with validation
    while True:
        amount_input = input(f"Enter amount in {currency}: ")
        if amount_input.lower() == 'cancel':
            print("Transaction canceled. Returning to previous menu.")
            return
        try:
            amount = float(amount_input)
            if amount > 0:
                break
            else:
                print("Amount must be positive. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid number or type 'cancel' to go back.")

    # Prompt for category with validation
    while True:
        category = input("Enter category (e.g., Salary, Groceries, etc.): ")
        if category:
            break
        elif category.lower() == 'cancel':
            print("Transaction canceled. Returning to previous menu.")
            return
        else:
            print("Invalid input. Category cannot be blank. Please try again or type 'cancel' to go back.")

    # Prompt for description with validation
    while True:
        description = input("Enter description: ")
        if description:
            break
        elif description.lower() == 'cancel':
            print("Transaction canceled. Returning to previous menu.")
            return
        else:
            print("Invalid input. Description cannot be blank. Please try again or type 'cancel' to go back.")

    # Prompt for date with validation
    while True:
        date_input = input("Enter date (YYYY-MM-DD) or leave blank for today: ") or str(datetime.date.today())
        if date_input.lower() == 'cancel':
            print("Transaction canceled. Returning to previous menu.")
            return
        try:
            datetime.datetime.strptime(date_input, "%Y-%m-%d")
            date = date_input
            break
        except ValueError:
            print("Invalid date format. Please enter a valid date in YYYY-MM-DD format, or type 'cancel' to go back.")

    # Insert the validated transaction into the database
    cursor.execute('''INSERT INTO transactions (username, type, amount, category, description, date)
                      VALUES (?, ?, ?, ?, ?, ?)''', (username, trans_type, amount, category, description, date))
    conn.commit()
    print(f"{trans_type.capitalize()} of {currency}{amount:.2f} added successfully to EzBudget.")

def view_transactions_menu(username):
    # Show the 5 most recent transactions when entering the menu
    print("\nYour 5 Most Recent Transactions:")
    cursor.execute("SELECT id, type, amount, category, description, date FROM transactions WHERE username=? ORDER BY date DESC LIMIT 5", (username,))
    recent_transactions = cursor.fetchall()
    
    if recent_transactions:
        headers = ["ID", "Type", "Amount", "Category", "Description", "Date"]
        table = [[trans[0], trans[1].capitalize(), f"${trans[2]:.2f}", trans[3], trans[4], trans[5]] for trans in recent_transactions]
        print(tabulate(table, headers, tablefmt="grid"))
    else:
        print("No recent transactions found.")

    # Provide options to view more details
    while True:
        print("\nView Transactions Menu:")
        print("1. View All Transactions")
        print("2. View Income Only")
        print("3. View Expenses Only")
        print("4. Go Back to Previous Menu")

        choice = input("Choose an option: ")

        if choice == '1':
            # Show all transactions
            view_transactions(username)
        elif choice == '2':
            # Show only income transactions
            view_transactions(username, filter_type="income")
        elif choice == '3':
            # Show only expense transactions
            view_transactions(username, filter_type="expense")
        elif choice == '4':
            # Exit to the main menu
            print("Returning to the previous menu...")
            break
        else:
            print("Invalid option. Please choose a valid option.")

# Updated view_transactions function to handle filters
def view_transactions(username, filter_type=None):
    # Determine the filter query based on the filter_type parameter
    if filter_type == "income":
        cursor.execute("SELECT id, type, amount, category, description, date FROM transactions WHERE username=? AND type='income'", (username,))
        print("\nIncome Transactions:")
    elif filter_type == "expense":
        cursor.execute("SELECT id, type, amount, category, description, date FROM transactions WHERE username=? AND type='expense'", (username,))
        print("\nExpense Transactions:")
    else:
        cursor.execute("SELECT id, type, amount, category, description, date FROM transactions WHERE username=?", (username,))
        print("\nAll Transactions:")

    # Fetch transactions and format them as a table
    transactions = cursor.fetchall()
    
    if transactions:
        headers = ["ID", "Type", "Amount", "Category", "Description", "Date"]
        table = [[trans[0], trans[1].capitalize(), f"${trans[2]:.2f}", trans[3], trans[4], trans[5]] for trans in transactions]
        print(tabulate(table, headers, tablefmt="grid"))
    else:
        print("No transactions found.")

# Editing and Deleting Transactions
def edit_transaction(username):
    # Display current transactions to the user
    view_transactions(username)
    trans_id = input("Enter the ID of the transaction to edit (or type 'cancel' to return to the menu): ")
    if trans_id.lower() == 'cancel':
        print("Edit canceled. Returning to previous menu.")
        return

    # Validate that trans_id is a valid integer and exists in the database
    try:
        trans_id = int(trans_id)
    except ValueError:
        print("Invalid ID. Returning to previous menu.")
        return
    
    # Fetch the existing transaction details
    cursor.execute("SELECT type, amount, category, description, date FROM transactions WHERE id=? AND username=?", (trans_id, username))
    result = cursor.fetchone()
    if result:
        current_type, current_amount, current_category, current_description, current_date = result
        print("\nLeave fields blank to keep the current value, or type 'cancel' to exit editing.")

        # Get new values from user input, use existing value if input is blank
        new_type = input(f"Enter new type (income/expense) [{current_type}]: ").lower()
        if new_type == 'cancel':
            print("Edit canceled. Returning to previous menu.")
            return
        new_type = new_type or current_type

        new_amount = input(f"Enter new amount [{current_amount}]: ")
        if new_amount.lower() == 'cancel':
            print("Edit canceled. Returning to previous menu.")
            return
        new_amount = float(new_amount) if new_amount else current_amount

        new_category = input(f"Enter new category [{current_category}]: ")
        if new_category.lower() == 'cancel':
            print("Edit canceled. Returning to previous menu.")
            return
        new_category = new_category or current_category

        new_description = input(f"Enter new description [{current_description}]: ")
        if new_description.lower() == 'cancel':
            print("Edit canceled. Returning to previous menu.")
            return
        new_description = new_description or current_description

        new_date = input(f"Enter new date (YYYY-MM-DD) [{current_date}]: ")
        if new_date.lower() == 'cancel':
            print("Edit canceled. Returning to previous menu.")
            return
        new_date = new_date or current_date

        # Update the transaction with the new or existing values
        cursor.execute('''UPDATE transactions 
                          SET type=?, amount=?, category=?, description=?, date=? 
                          WHERE id=? AND username=?''',
                       (new_type, new_amount, new_category, new_description, new_date, trans_id, username))
        conn.commit()
        print("Transaction updated successfully in EzBudget.")

        # Return to the transactions menu instead of the main menu
        view_transactions_menu(username)
    else:
        print("Transaction not found.")


def delete_transaction(username):
    view_transactions(username)
    trans_id = input("Enter the ID of the transaction to delete (or type 'cancel' to return to the menu): ")
    if trans_id.lower() == 'cancel':
        print("Delete canceled. Returning to previous menu.")
        return
    
    try:
        trans_id = int(trans_id)
    except ValueError:
        print("Invalid ID. Returning to previous menu.")
        return

    # Confirm deletion
    confirm = input("Are you sure you want to delete this transaction? (y/n): ").lower()
    if confirm == 'y':
        cursor.execute("DELETE FROM transactions WHERE id=? AND username=?", (trans_id, username))
        conn.commit()
        print("Transaction deleted successfully from EzBudget.")
    else:
        print("Deletion canceled.")


# Main Program Loop
def main():
    show_welcome()

    while True:
        choice = input("\nChoose an option:\n1. Register\n2. Login\n3. Recover Account\n4. Exit\n> ")
        if choice == '1':
            register()
        elif choice == '2':
            username = login()
            if username:
                while True:
                    action = input("\nChoose an action:\n1. Add Income/Expense\n2. View Transactions\n3. Edit Transaction\n4. Delete Transaction\n5. Logout\n> ")
                    if action == '1':
                        add_transaction(username)
                    elif action == '2':
                        view_transactions_menu(username)  # Updated to use the new submenu
                    elif action == '3':
                        edit_transaction(username)
                    elif action == '4':
                        delete_transaction(username)
                    elif action == '5':
                        confirm = input("Are you sure you want to logout? (y/n): ").lower()
                        if confirm == 'y':
                            print("Logging out of EzBudget...")
                            break
                        else:
                            print("Logout canceled.")
                    else:
                        print("Invalid option.")
        elif choice == '3':
            recover_account()
        elif choice == '4':
            print("Goodbye from EzBudget!")
            break
        else:
            print("Invalid option.")

main()
