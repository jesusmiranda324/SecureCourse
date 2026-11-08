import sqlite3
from pathlib import Path
from getpass import getpass
from werkzeug.security import generate_password_hash

DATABASE = Path(__file__).parent / "instance" / "securecourse.db"

# Create the database folder if it does not exist
DATABASE.parent.mkdir(exist_ok=True)

# Connect to the database
connection = sqlite3.connect(DATABASE)

# Create the users table
connection.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
""")

connection.commit()

# Get account information
username = input("Enter username: ").strip()
password = getpass("Enter password: ")
role = input("Enter role (faculty, student, other): ").strip().lower()

if role not in ("faculty", "student", "other"):
    print("Invalid role.")
else:
    password_hash = generate_password_hash(password)

    try:
        connection.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )

        connection.commit()
        print("User created successfully!")

    except sqlite3.IntegrityError:
        print("That username already exists.")

connection.close()