import sqlite3
import re
import hashlib
import random

from getpass import getpass

USERS_DB = "users.db"

with sqlite3.connect(USERS_DB) as conn:
    cursor = conn.cursor()
    cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL CHECK (full_name <> ''),
    username TEXT NOT NULL UNIQUE CHECK (username <> ''),
    email TEXT NOT NULL UNIQUE CHECK (email <> ''),
    password TEXT NOT NULL CHECK (password <> ''),
    initial_deposit INTEGER NOT NULL CHECK (initial_deposit >= 2000),
    account_number TEXT NOT NULL UNIQUE
);
""")

def account_number_generator(cursor):
    while True:
        account_number = str(random.randint(10_000_000, 99_999_999))
        with sqlite3.connect(USERS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE account_number = ?", (account_number,))
            if cursor.fetchone() is None:
                return account_number
            
            conn.commit()


def sign_up():
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
        username_pattern = r"^(?=.{6,20}$)[A-Za-z][A-Za-z0-9]*$"
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


    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        account_number = account_number_generator(cursor)
        try:
            cursor.execute("INSERT INTO users (full_name, username, email, password, initial_deposit, account_number) VALUES (?, ?, ?, ?, ?, ?)", (full_name, username, email, hashed_password, initial_deposit, account_number))
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
            # log_in()


def log_in():
    pass

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
        sign_up()

    elif choice == "2":
        log_in()
    
    elif choice == "3":
        print("Exiting...")
        break
