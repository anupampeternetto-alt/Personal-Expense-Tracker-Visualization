
import sqlite3

import pytest

from src.categorize import classify, categorize_transactions


@pytest.mark.parametrize(
    "description, amount, expected",
    [
        ("DMart groceries", -500, "Groceries"),
        ("Swiggy dinner", -250, "Food & Dining"),
        ("Uber taxi", -300, "Transport"),
        ("Electricity bill", -900, "Bills & Utilities"),
        ("Amazon shopping", -1200, "Shopping"),
        ("Netflix subscription", -199, "Entertainment"),
        ("College books", -750, "Education"),
        ("Monthly salary", 15000, "Income"),
        ("Unknown purchase", -100, "Uncategorized"),
        ("SWIGGY DINNER", -250, "Food & Dining"),
    ],
)
def test_classification(description, amount, expected):
    assert classify(description, amount) == expected


def test_positive_amount_is_income():
    assert classify("Amazon refund", 500) == "Income"


def test_database_categorization(tmp_path):
    db_path = tmp_path / "test_expenses.db"

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category_id INTEGER,
                FOREIGN KEY (category_id)
                    REFERENCES categories(id)
            )
        """)

        conn.executemany(
            """
            INSERT INTO transactions
                (description, amount)
            VALUES (?, ?)
            """,
            [
                ("Swiggy dinner", -250),
                ("Uber taxi", -300),
                ("Monthly salary", 15000),
            ],
        )

    categorize_transactions(str(db_path))

    with sqlite3.connect(db_path) as conn:
        results = conn.execute("""
            SELECT c.name
            FROM transactions AS t
            JOIN categories AS c
                ON t.category_id = c.id
            ORDER BY t.id
        """).fetchall()

    assert results == [
        ("Food & Dining",),
        ("Transport",),
        ("Income",),
    ]


def test_existing_category_preserved(tmp_path):
    db_path = tmp_path / "test_existing.db"

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category_id INTEGER
            )
        """)

        conn.execute(
            "INSERT INTO categories (id, name) VALUES (1, 'Shopping')"
        )

        conn.execute("""
            INSERT INTO transactions
                (description, amount, category_id)
            VALUES ('Swiggy dinner', -250, 1)
        """)

    categorize_transactions(str(db_path))

    with sqlite3.connect(db_path) as conn:
        category_id = conn.execute(
            "SELECT category_id FROM transactions WHERE id = 1"
        ).fetchone()[0]

    assert category_id == 1


def test_repeat_categorization_is_safe(tmp_path):
    db_path = tmp_path / "test_repeat.db"

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category_id INTEGER
            )
        """)

        conn.execute("""
            INSERT INTO transactions
                (description, amount)
            VALUES ('Netflix subscription', -199)
        """)

    categorize_transactions(str(db_path))
    categorize_transactions(str(db_path))

    with sqlite3.connect(db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM categories WHERE name = 'Entertainment'"
        ).fetchone()[0]

        category = conn.execute("""
            SELECT c.name
            FROM transactions AS t
            JOIN categories AS c
                ON t.category_id = c.id
        """).fetchone()[0]

    assert count == 1
    assert category == "Entertainment"
