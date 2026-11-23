
import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = "db/expenses.db"


def read_expense_csv(path):
    """Load and validate a manual or synthetic CSV."""

    df = pd.read_csv(path)

    required = ["Date", "Description", "Amount", "Account"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[required].copy()

    df["Date"] = pd.to_datetime(
        df["Date"], format="%Y-%m-%d", errors="coerce"
    )
    df["Amount"] = pd.to_numeric(
        df["Amount"], errors="coerce"
    )

    df["Description"] = df["Description"].astype(
        "string"
    ).str.strip()

    df["Account"] = df["Account"].astype(
        "string"
    ).str.strip()

    valid = (
        df["Date"].notna()
        & df["Amount"].notna()
        & (df["Amount"] != 0)
        & df["Description"].notna()
        & df["Description"].ne("")
        & df["Account"].notna()
        & df["Account"].ne("")
    )

    rejected = df.loc[~valid].copy()
    clean = df.loc[valid].copy()

    clean["Date"] = clean["Date"].dt.strftime("%Y-%m-%d")

    clean = clean.rename(columns={
        "Date": "tx_date",
        "Description": "description",
        "Amount": "amount",
        "Account": "account",
    })

    print(f"Valid records: {len(clean)}")
    print(f"Rejected records: {len(rejected)}")

    return clean, rejected


def save_to_database(df, db_path=DB_PATH):
    """Insert valid transactions without duplicating existing rows."""

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        before = connection.total_changes

        for row in df.itertuples(index=False):
            connection.execute(
                """
                INSERT OR IGNORE INTO transactions
                (tx_date, description, amount, account, raw_source)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    row.tx_date,
                    row.description,
                    float(row.amount),
                    row.account,
                    "sample_expenses.csv",
                ),
            )

        inserted = connection.total_changes - before
        connection.commit()

    print(f"New transactions inserted: {inserted}")


if __name__ == "__main__":
    from src.models import init_db

    init_db()
    clean, rejected = read_expense_csv(
        "data/sample_expenses.csv"
    )

    save_to_database(clean)
    print("CSV INGESTION COMPLETED SUCCESSFULLY")
