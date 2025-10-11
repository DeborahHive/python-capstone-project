import sqlite3
import re
import hashlib

from getpass import getpass

USERS_DB = "users.db"

with sqlite3.connect(USERS_DB) as conn:
    cursor = conn.cursor()
    cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL CHECK (full_name <> ''),
    username TEXT NOT NULL CHECK (username <> ''),
    password TEXT NOT NULL CHECK (password <> '')
);
""")
    
def sign_up():
    while True:
        full_name_pattern = r"^(?=.{4,255}$)[A-Za-z]+(?:[-'][A-Za-z]+)*(?: [A-Za-z]+(?:[-'][A-Za-z]+)*)*$"
        full_name = input("Enter your fullname: ").strip()

        if not full_name:
            print("Fullname cannot be blank.")
            continue
        if re.fullmatch(full_name_pattern, full_name, re.IGNORECASE):
            full_name = full_name.title()
        else:
            print("Invalid name. Please use only letters and spaces.")
        break

    while True:
        username_pattern = r"^(?=.{6,20}$)[A-Za-z][A-Za-z0-9]*$"
        username = input("Enter your username: ").strip()

        if not username:
            print("Username cannot be blank.")
            continue
        if not re.fullmatch(username_pattern, username):
            print("Invalid username. Must start with a letter and be 6-20 letters/numbers only.")
            continue
        break

    while True:
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,32}$"
        password1 = getpass("Enter a password: ").strip()
        if not password1:
            print("Password field cannot be blank.")
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

    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (full_name, username, password) VALUES (?, ?, ?)", (full_name, username, hashed_password))

        conn.commit()
        print("Account created successfully!")
        log_in()

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
