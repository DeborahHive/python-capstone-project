import sqlite3
import re
import hashlib
import random
import time
import datetime
# from colorama import Fore, Style

from getpass import getpass

class BankSystem:
    def __init__(self, USERS_DB = "users.db"):
        self.USERS_DB = USERS_DB
        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.USERS_DB)
    
    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL CHECK (full_name <> ''),
            username TEXT NOT NULL UNIQUE CHECK (username <> ''),
            email TEXT NOT NULL UNIQUE CHECK (email <> ''),
            password TEXT NOT NULL CHECK (password <> ''),
            initial_deposit INTEGER NOT NULL CHECK (initial_deposit >= 2000),
            account_number TEXT NOT NULL UNIQUE,
            balance REAL NOT NULL DEFAULT 0
        );
        """)

            cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            recipient_name TEXT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL CHECK (amount > 0),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
            
            cursor.execute("UPDATE users SET balance = initial_deposit WHERE balance = 0")
            conn.commit()


    def _account_number_generator(self):
        while True:
            account_number = str(random.randint(10_000_000, 99_999_999))
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM users WHERE account_number = ?", (account_number,))
                if cursor.fetchone() is None:
                    return account_number


    def sign_up(self):
        while True:
            first_name = input("Enter your first name: ").strip()

            if not first_name:
                print("This field cannot be blank.")
                continue
            break

        while True:
            last_name = input("Enter your last name: ").strip()

            if not last_name:
                print("This field cannot be blank.")
                continue
            break

        full_name = f"{first_name} {last_name}"
        full_name_pattern = r"^(?=.{4,255}$)[A-Za-z]+(?:[-'][A-Za-z]+)*(?: [A-Za-z]+(?:[-'][A-Za-z]+)*)*$"
        if re.fullmatch(full_name_pattern, full_name, re.IGNORECASE):
            full_name = full_name.title()

        while True:
            username_pattern = r"^(?=.{3,20}$)[A-Za-z][A-Za-z0-9]*$"
            username = input("Enter your username: ").strip()

            if not username:
                print("This field cannot be blank.")
                continue
            if not re.fullmatch(username_pattern, username):
                print("Invalid username. Must start with a letter and be 6-20 letters/numbers only.")
                continue
            break

        while True:
            email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
            email = input("Enter your email: ").strip()

            if not email:
                print("This field cannot be blank.")
                continue
            if not re.fullmatch(email_pattern, email):
                print("Invalid email")
                continue
            break

        while True:
            password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$"
            password1 = getpass("Enter a password: ").strip()
            if not password1:
                print("This field cannot be blank.")
                continue
            if not re.fullmatch(password_pattern, password1):
                print("Invalid password. Must include upper, lower, number, symbol, and be 8-32 chars long.")
                continue

            password2 = getpass("Confirm your password: ").strip()
            if not password2:
                print("Confirm password field cannot be blank.")
                continue
            if not re.fullmatch(password_pattern, password2):
                print("Invalid password. Must include upper, lower, number, symbol, and be 8-32 chars long.")
                continue

            if password1 != password2:
                print("Password do not match!")
                continue
            break
        hashed_password = hashlib.sha256(password1.encode()).hexdigest()

        while True:
            try:
                initial_deposit = int(input("Enter initial deposit (minimum of ₦2000 required): "))
            except ValueError:
                print("Initial deposit must be integers.")
            else:
                if initial_deposit < 2000:
                    print("Initial deposit must be a minimum of ₦2000.")
                    continue
                break


        with self.connect() as conn:
            account_number = self._account_number_generator()
            cursor = conn.cursor()
            balance = initial_deposit
            try:
                cursor.execute("INSERT INTO users (full_name, username, email, password, initial_deposit, account_number, balance) VALUES (?, ?, ?, ?, ?, ?, ?)", (full_name, username, email, hashed_password, initial_deposit, account_number, balance))
            except sqlite3.IntegrityError as exc:
                exc = str(exc)
                if exc == "UNIQUE constraint failed: users.email":
                    print("Email already exists.")
                elif exc == "UNIQUE constraint failed: users.username":
                    print("Username already exists.")
                else:
                    print(exc)
            else:
                conn.commit()
                print(f"Account created successfully! Your account number is {account_number}.")
                self.log_in()


    def log_in(self):
        attempts = 3
        with self.connect() as conn:
            cursor = conn.cursor()
            while True:
                while attempts > 0:
                    username_pattern = r"^(?=.{6,20}$)[A-Za-z][A-Za-z0-9]*$"
                    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

                    username_or_email = input("\nEnter your username or email: ").strip()

                    if not username_or_email:
                        print("This field cannot be blank.")
                        continue

                    if not (re.fullmatch(username_pattern, username_or_email)) and not (re.fullmatch(email_pattern, username_or_email)):
                        print("Invalid username or email")
                        continue

                    password1 = getpass("Enter your password: ").strip()

                    if not password1:
                        print("This field cannot be blank.")
                        continue
                    
                    hashed_password = hashlib.sha256(password1.encode()).hexdigest()

                    cursor.execute("SELECT * FROM users WHERE (username=? OR email=?) AND password=?", (username_or_email, username_or_email, hashed_password))
                    user = cursor.fetchone()

                    if user:
                        print("Log in successful")
                        self.dashboard(user[0])
                        return True
                    
                    else: 
                        attempts -= 1
                        print(f"Invalid credentials")
                
                print("Too many failed attempts. Please wait two minutes before trying again.")
                time.sleep(120)
                attempts = 3


    def dashboard(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()

            while True:
                cursor.execute("SELECT full_name, account_number, balance FROM users where user_id = ?", (user_id,))
                user = cursor.fetchone()

                if not user:
                    print("Error: User not found.")
                    return
                
                full_name, account_number, balance = user

                menu = f"""
------------------HOME🏡------------------------
\nWelcome back, {full_name}!
Account_number: {account_number}
Balance: ₦{balance:.2f}
\nChoose an action:
1. Deposit
2. Withdrawal
3. Transfer
4. Account Details
5. Transaction History
6. Logout
"""
            
                print(menu)
                choice = input("Choose an option: ").strip()

                if choice == "1":
                    self.deposit(user_id)

                elif choice == "2":
                    self.withdrawal(user_id)
                
                elif choice == "3":
                    self.transfer(user_id)
                
                elif choice == "4":
                    self.account_details(user_id)
                
                elif choice == "5":
                    self.transaction_history(user_id)

                elif choice == "6":
                    print("Logging out...")
                    break

                conn.commit()


    def deposit(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()

            while True:
                try:
                    deposit_amt = float(input("\nEnter deposit amount: ₦"))
                except ValueError:
                    print("Please, enter a valid number.")
                    continue
                if deposit_amt <= 0:
                    print("The amount must be greater than 0")
                    continue
                break

            cursor.execute("SELECT full_name FROM users where user_id = ?", (user_id,))
            full_name = cursor.fetchone()[0]

            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (deposit_amt, user_id))
            cursor.execute("INSERT INTO transactions (user_id, full_name, transaction_type, amount, timestamp) VALUES (?, ?, ?, ?, ?)", (user_id, full_name, "CR-Deposit", deposit_amt, datetime.datetime.now().isoformat()))

            conn.commit()
            print(f"₦{deposit_amt:.2f} deposited successfully!")


    def withdrawal(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()

            while True:
                try:
                    withdrawal_amt = float(input("\nEnter the amount you want to withdraw: ₦"))
                except ValueError:
                    print("Please, enter a valid number.")
                    continue
                if withdrawal_amt <= 0:
                    print("The amount must be greater than 0.")
                    continue

                cursor.execute("SELECT full_name, balance FROM users where user_id = ?", (user_id,))
                full_name, balance = cursor.fetchone()

                if withdrawal_amt > balance:
                    print(f"Insufficient funds. Your current balance is ₦{balance:.2f}")
                    continue

                updated_balance = balance - withdrawal_amt
                cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (updated_balance, user_id))
                cursor.execute("INSERT INTO transactions (user_id, full_name, transaction_type, amount, timestamp) VALUES (?, ?, ?, ?, ?)", (user_id, full_name, "DR-Withdrawal", withdrawal_amt, datetime.datetime.now().isoformat()))

                conn.commit()
                print(f"₦{withdrawal_amt:.2f} withdrawn successfully!\nBalance: ₦{updated_balance:.2f}")
                break


    def transfer(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT full_name, account_number, balance FROM users WHERE user_id = ?", (user_id,))
            sender = cursor.fetchone()
            if not sender:
                print("Error: user not found.")
                return
            
            sender_name, sender_account, sender_balance = sender

            while True:
                recipient_account = input("\nEnter the recipient's account number: ").strip()
                if not recipient_account:
                    print("This field cannot be blank.")
                    continue
                if recipient_account == sender_account:
                    print("You cannot transfer money to yourself.")
                    continue

                cursor.execute("SELECT user_id, full_name FROM users WHERE account_number = ?", (recipient_account,))
                recipient = cursor.fetchone()
                if not recipient:
                    print("Recipient cannot be found.")
                    continue
                recipient_id, recipient_name = recipient
                break

            while True:
                try:
                    transfer_amt = float(input("Enter amount to transfer: ₦"))
                except ValueError:
                    print("Please, enter a valid number.")
                    continue
                if transfer_amt <= 0:
                    print("Amount must be greater than 0.")
                    continue
                if transfer_amt > sender_balance:
                    print("Insufficient funds.")
                    continue
                break

            cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (transfer_amt, user_id))
            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (transfer_amt, recipient_id))

            cursor.execute("INSERT INTO transactions (user_id, full_name, recipient_name, transaction_type, amount, timestamp) VALUES (?, ?, ?, ?, ?, ?)", (user_id, sender_name, recipient_name, "DR-Transfer To", transfer_amt, datetime.datetime.now().isoformat()))
            cursor.execute("INSERT INTO transactions (user_id, recipient_name, full_name, transaction_type, amount, timestamp) VALUES (?, ?, ?, ?, ?, ?)", (recipient_id, recipient_name, sender_name, "CR-Transfer From", transfer_amt, datetime.datetime.now().isoformat()))

            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            updated_balance = cursor.fetchone()[0]
            conn.commit()
            print(f"{transfer_amt:.2f} Transfer successfull!👍")


    def account_details(self, user_id):
        with self.connect() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT full_name, account_number, email, balance FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()

            if not user:
                print("Account not found.")
                return
            full_name, account_number, email, balance = user
            print(f"""
_________DETAILS_________
Name: {full_name}
Account Number: {account_number}
Email: {email}
Balance: ₦{balance:.2f}
""")
            
    
    def transaction_history(self, user_id):
        GREEN = "\033[92m"
        RED = "\033[91m"
        RESET = "\033[0m"

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT full_name, recipient_name, transaction_type, amount, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
            
            transactions = cursor.fetchall()

            print("\n--------------------TRANSACTION HISTORY--------------------")

            if not transactions:
                print("No transactions found.")
                return
            
            for transaction in transactions:
                sender, recipient, trans_type, amount, timestamp = transaction
                date_time = datetime.datetime.fromisoformat(timestamp)
                formatted_date = date_time.strftime("%a %d %b %Y")
                formatted_time = date_time.strftime("%I:%M%p")

                if "CR" in trans_type:
                    color = GREEN
                    if "Deposit" in trans_type:
                        narration = f"Deposit by {sender}"
                    else:
                        narration = f"Transfer from {sender}"
                elif "DR" in trans_type:
                    color = RED
                    if "Withdrawal" in trans_type:
                        narration = f"Withdrawal by {sender}"
                    else:
                        narration = f"Transfer to {recipient}"
                else:
                    color = RESET

                print(f"""
Date: {formatted_date}
Time: {formatted_time}
Amount: {color}₦{amount:.2f}{RESET}
Narration: {narration}
----------------------------------------""")


    def run(self):
        menu = """
        1. Sign Up
        2. Log In
        3. Exit
        """
        print("Welcome to Calvary Bank")
        while True:
            print(menu)
            choice = input("Choose an Sign up or Log in to an existing account: ").strip()

            if choice == "1":
                self.sign_up()

            elif choice == "2":
                self.log_in()
            
            elif choice == "3":
                print("Exiting...")
                break

if __name__ == "__main__":
    app = BankSystem()
    app.run()