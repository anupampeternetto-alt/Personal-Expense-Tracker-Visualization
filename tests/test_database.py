
import sqlite3
import pytest


@pytest.fixture
def db():
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")

    connection.executescript("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            parent TEXT
        );

        CREATE TABLE transactions (
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
            FOREIGN KEY(category_id) REFERENCES categories(id)
        );

        CREATE TABLE budgets (
            id INTEGER PRIMARY KEY,
            month TEXT NOT NULL,
            category_name TEXT NOT NULL,
            limit_amount REAL NOT NULL CHECK(limit_amount >= 0),
            UNIQUE(month, category_name)
        );
    """)

    yield connection
    connection.close()


def test_duplicate_category(db):
    db.execute("INSERT INTO categories(name) VALUES ('Food')")

    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO categories(name) VALUES ('Food')")


def test_invalid_foreign_key(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("""
            INSERT INTO transactions
            (tx_date, description, amount, account, category_id)
            VALUES ('2026-11-23', 'Lunch', -200, 'UPI', 999)
        """)


def test_duplicate_transaction(db):
    sql = """
        INSERT INTO transactions
        (tx_date, description, amount, account)
        VALUES ('2026-11-23', 'Lunch', -200, 'UPI')
    """

    db.execute(sql)

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(sql)


def test_negative_budget(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("""
            INSERT INTO budgets
            (month, category_name, limit_amount)
            VALUES ('2026-11', 'Food', -100)
        """)


def test_database_integrity(db):
    result = db.execute("PRAGMA integrity_check").fetchone()[0]
    assert result == "ok"
