
import re
import sqlite3

DB_PATH = "db/expenses.db"

RULES = {
    "Groceries": [
        r"dmart|d-mart|grocery|groceries|supermarket"
    ],
    "Food & Dining": [
        r"swiggy|zomato|restaurant|cafe|lunch|dinner"
    ],
    "Transport": [
        r"uber|ola|metro|fuel|petrol|diesel|taxi"
    ],
    "Bills & Utilities": [
        r"electricity|water bill|wifi|recharge|broadband"
    ],
    "Shopping": [
        r"amazon|flipkart|myntra|shopping"
    ],
    "Entertainment": [
        r"netflix|spotify|cinema|movie|bookmyshow"
    ],
    "Education": [
        r"college|books|tuition|course|education"
    ],
    "Income": [
        r"salary|allowance|payout|income"
    ]
}


def classify(description, amount):
    """Assign a category using amount and keyword rules."""

    if amount > 0:
        return "Income"

    text = description.lower()

    for category, patterns in RULES.items():
        if category == "Income":
            continue

        for pattern in patterns:
            if re.search(pattern, text):
                return category

    return "Uncategorized"


def categorize_transactions(db_path=DB_PATH):
    """Categorize transactions without overriding existing labels."""

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        category_names = list(RULES) + ["Uncategorized"]

        for name in category_names:
            connection.execute(
                "INSERT OR IGNORE INTO categories(name) VALUES (?)",
                (name,)
            )

        categories = dict(
            connection.execute(
                "SELECT name, id FROM categories"
            ).fetchall()
        )

        transactions = connection.execute("""
            SELECT id, description, amount
            FROM transactions
            WHERE category_id IS NULL
        """).fetchall()

        for transaction_id, description, amount in transactions:
            category = classify(description, amount)

            connection.execute(
                """
                UPDATE transactions
                SET category_id = ?
                WHERE id = ?
                """,
                (categories[category], transaction_id)
            )

        connection.commit()

    print(f"TRANSACTIONS CATEGORIZED: {len(transactions)}")
    print("CATEGORIZATION COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    categorize_transactions()
