
"""Monthly budget monitoring and overspending alerts."""

import sqlite3
from pathlib import Path

import pandas as pd

from src.analyze import load_transactions

DB_PATH = Path("db/expenses.db")

SAMPLE_BUDGETS = {
    "Food & Dining": 1000,
    "Groceries": 1500,
    "Transport": 500,
    "Shopping": 1500,
    "Entertainment": 500,
    "Bills & Utilities": 1200,
    "Education": 1000,
}


def create_budgets(month="2026-11", db_path=DB_PATH):
    """Create sample budgets without overwriting existing limits."""

    with sqlite3.connect(db_path) as connection:
        for category, limit in SAMPLE_BUDGETS.items():
            connection.execute(
                """
                INSERT OR IGNORE INTO budgets
                (month, category_name, limit_amount)
                VALUES (?, ?, ?)
                """,
                (month, category, limit),
            )

        connection.commit()

    print("MONTHLY BUDGETS INITIALIZED")


def analyze_budgets(month="2026-11", db_path=DB_PATH):
    """Compare monthly expenses against category budgets."""

    df = load_transactions(db_path)

    df = df[
        (df["month"] == month) &
        (df["amount"] < 0)
    ].copy()

    df["spent"] = -df["amount"]

    spending = (
        df.groupby("category")["spent"]
        .sum()
        .to_dict()
    )

    with sqlite3.connect(db_path) as connection:
        budgets = pd.read_sql_query(
            """
            SELECT category_name, limit_amount
            FROM budgets
            WHERE month = ?
            """,
            connection,
            params=(month,),
        )

    if budgets.empty:
        raise ValueError(
            f"No budgets configured for {month}"
        )

    results = []

    for row in budgets.itertuples(index=False):
        category = row.category_name
        limit = float(row.limit_amount)
        spent = float(spending.get(category, 0))

        remaining = limit - spent

        if spent > limit:
            status = "OVER BUDGET"
        elif limit > 0 and spent >= limit * 0.8:
            status = "WARNING"
        else:
            status = "WITHIN BUDGET"

        results.append({
            "category": category,
            "budget": limit,
            "spent": spent,
            "remaining": remaining,
            "status": status,
        })

    return pd.DataFrame(results)


def run_budget_analysis():
    month = "2026-11"

    create_budgets(month)
    result = analyze_budgets(month)

    print("\nMONTHLY BUDGET ANALYSIS")
    print("=" * 55)
    print(result.to_string(index=False))

    print("\nBUDGET ALERTS")

    alerts = result[
        result["status"] != "WITHIN BUDGET"
    ]

    if alerts.empty:
        print("No overspending alerts.")
    else:
        for row in alerts.itertuples(index=False):
            print(
                f"{row.category}: {row.status} "
                f"(INR {row.spent:.2f} spent / "
                f"INR {row.budget:.2f} budget)"
            )

    output = Path("outputs")
    output.mkdir(parents=True, exist_ok=True)

    result.to_csv(
        output / "budget_analysis.csv",
        index=False,
    )

    print("\nBUDGET ANALYSIS COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run_budget_analysis()
