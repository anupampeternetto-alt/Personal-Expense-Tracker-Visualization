
"""Financial analysis for the Personal Expense Tracker."""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("db/expenses.db")


def load_transactions(db_path=DB_PATH):
    """Read transactions and their categories from SQLite."""
    with sqlite3.connect(db_path) as connection:
        df = pd.read_sql_query(
            """
            SELECT
                t.id,
                t.tx_date,
                t.description,
                t.amount,
                t.account,
                COALESCE(c.name, 'Uncategorized') AS category
            FROM transactions AS t
            LEFT JOIN categories AS c
                ON t.category_id = c.id
            ORDER BY t.tx_date
            """,
            connection,
        )

    if df.empty:
        raise ValueError("No transactions found in the database.")

    df["tx_date"] = pd.to_datetime(
        df["tx_date"], errors="raise"
    )
    df["amount"] = pd.to_numeric(
        df["amount"], errors="raise"
    )
    df["month"] = df["tx_date"].dt.strftime("%Y-%m")

    return df


def calculate_kpis(df):
    """Calculate the main financial indicators."""
    income = df.loc[df["amount"] > 0, "amount"].sum()
    expenses = -df.loc[df["amount"] < 0, "amount"].sum()

    savings = income - expenses
    savings_rate = (
        savings / income * 100 if income > 0 else 0.0
    )

    expense_df = df[df["amount"] < 0]

    if not expense_df.empty:
        first_day = expense_df["tx_date"].min()
        last_day = expense_df["tx_date"].max()
        days = (last_day - first_day).days + 1
        daily_average = expenses / days
    else:
        daily_average = 0.0

    return {
        "income": round(float(income), 2),
        "expenses": round(float(expenses), 2),
        "savings": round(float(savings), 2),
        "savings_rate": round(float(savings_rate), 2),
        "daily_average": round(float(daily_average), 2),
    }


def category_analysis(df):
    """Calculate category-wise expense totals."""
    expenses = df[df["amount"] < 0].copy()
    expenses["spending"] = -expenses["amount"]

    return (
        expenses.groupby("category")["spending"]
        .sum()
        .sort_values(ascending=False)
        .round(2)
    )


def monthly_analysis(df):
    """Calculate monthly income, spending and savings."""
    result = df.groupby("month").agg(
        income=("amount", lambda x: x[x > 0].sum()),
        expenses=("amount", lambda x: -x[x < 0].sum()),
    )

    result["savings"] = (
        result["income"] - result["expenses"]
    )

    return result.round(2)


def payment_analysis(df):
    """Calculate spending by payment method."""
    expenses = df[df["amount"] < 0].copy()
    expenses["spending"] = -expenses["amount"]

    return (
        expenses.groupby("account")["spending"]
        .sum()
        .sort_values(ascending=False)
        .round(2)
    )


def daily_analysis(df):
    """Calculate daily spending totals."""
    expenses = df[df["amount"] < 0].copy()
    expenses["spending"] = -expenses["amount"]

    return (
        expenses.groupby("tx_date")["spending"]
        .sum()
        .sort_index()
        .round(2)
    )


def run_analysis():
    df = load_transactions()
    kpis = calculate_kpis(df)
    categories = category_analysis(df)
    monthly = monthly_analysis(df)
    payments = payment_analysis(df)
    daily = daily_analysis(df)

    print("\nPERSONAL EXPENSE TRACKER - FINANCIAL ANALYSIS")
    print("=" * 50)

    print(f"Total Income: INR {kpis['income']:.2f}")
    print(f"Total Expenses: INR {kpis['expenses']:.2f}")
    print(f"Net Savings: INR {kpis['savings']:.2f}")
    print(f"Savings Rate: {kpis['savings_rate']:.2f}%")
    print(
        f"Average Daily Spending: "
        f"INR {kpis['daily_average']:.2f}"
    )

    print("\nCATEGORY-WISE SPENDING")
    print(categories.to_string())

    print("\nMONTHLY FINANCIAL SUMMARY")
    print(monthly.to_string())

    print("\nPAYMENT METHOD ANALYSIS")
    print(payments.to_string())

    print("\nDAILY SPENDING")
    print(daily.to_string())

    if not categories.empty:
        print(
            "\nHighest Spending Category:",
            categories.index[0],
        )

    output = Path("outputs")
    output.mkdir(parents=True, exist_ok=True)

    categories.to_csv(output / "category_analysis.csv")
    monthly.to_csv(output / "monthly_analysis.csv")
    payments.to_csv(output / "payment_analysis.csv")
    daily.to_csv(output / "daily_analysis.csv")

    print("\nANALYSIS COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run_analysis()
