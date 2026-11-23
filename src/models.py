
import sqlite3
from pathlib import Path


DB_PATH = "db/expenses.db"


def init_db(path=DB_PATH):
    """Initialize the expense tracker SQLite database."""

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as con:
        con.execute("PRAGMA foreign_keys = ON")

        con.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            parent TEXT
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            tx_date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'INR',
            account TEXT NOT NULL,
            category_id INTEGER,
            raw_source TEXT,
            tags TEXT,

            UNIQUE(tx_date, description, amount, account),

            FOREIGN KEY(category_id)
                REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY,
            month TEXT NOT NULL,
            category_name TEXT NOT NULL,
            limit_amount REAL NOT NULL
                CHECK(limit_amount >= 0),

            UNIQUE(month, category_name)
        );
        """)

        con.commit()

    print("DATABASE INITIALIZED SUCCESSFULLY")
    print(f"Database location: {path}")


if __name__ == "__main__":
    init_db()
