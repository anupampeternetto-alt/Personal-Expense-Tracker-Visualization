
"""Generate expense tracker visualizations."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.analyze import (
    load_transactions,
    category_analysis,
    monthly_analysis,
    payment_analysis,
    daily_analysis,
)

OUTPUT_DIR = Path("images")


def save_chart(filename):
    """Save chart and release its resources."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"CHART SAVED: {path}")


def category_chart(df):
    data = category_analysis(df)

    if data.empty:
        return

    plt.figure(figsize=(10, 6))
    sns.barplot(
        x=data.values,
        y=data.index,
        color="steelblue"
    )

    plt.title("Category-wise Expense Analysis")
    plt.xlabel("Spending (INR)")
    plt.ylabel("Expense Category")

    save_chart("category_spending.png")


def monthly_chart(df):
    data = monthly_analysis(df)

    if data.empty:
        return

    plt.figure(figsize=(10, 5))

    plt.plot(
        data.index,
        data["expenses"],
        marker="o",
        linewidth=2,
        label="Expenses"
    )

    plt.title("Monthly Spending Trend")
    plt.xlabel("Month")
    plt.ylabel("Expenses (INR)")
    plt.legend()
    plt.grid(alpha=0.3)

    save_chart("monthly_spending.png")


def payment_chart(df):
    data = payment_analysis(df)

    if data.empty or data.sum() <= 0:
        return

    plt.figure(figsize=(8, 8))

    plt.pie(
        data.values,
        labels=data.index,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Payment Method Distribution")

    save_chart("payment_methods.png")


def daily_chart(df):
    data = daily_analysis(df)

    if data.empty:
        return

    # Include days with zero expenses.
    all_days = pd.date_range(
        start=data.index.min(),
        end=data.index.max(),
        freq="D"
    )

    data = data.reindex(all_days, fill_value=0)

    plt.figure(figsize=(11, 5))

    plt.plot(
        data.index,
        data.values,
        marker="o",
        linewidth=2,
        color="teal"
    )

    plt.title("Daily Spending Trend")
    plt.xlabel("Date")
    plt.ylabel("Spending (INR)")
    plt.xticks(rotation=45)
    plt.grid(alpha=0.3)

    save_chart("daily_spending.png")


def generate_all_charts():
    sns.set_theme(style="whitegrid")

    df = load_transactions()

    print("\nGENERATING EXPENSE VISUALIZATIONS")
    print("=" * 45)

    category_chart(df)
    monthly_chart(df)
    payment_chart(df)
    daily_chart(df)

    print("\nALL VISUALIZATIONS GENERATED SUCCESSFULLY")

def cumulative_budget_chart():
    """Compare cumulative monthly spending against category budgets."""
    import sqlite3

    with sqlite3.connect("db/expenses.db") as conn:
        budgets = pd.read_sql_query(
            """
            SELECT month, category_name AS category,
                   limit_amount AS budget
            FROM budgets
            """,
            conn,
        )

    transactions = load_transactions()

    if budgets.empty or transactions.empty:
        print("No data available for cumulative budget chart.")
        return

    expenses = transactions[transactions["amount"] < 0].copy()
    expenses["month"] = pd.to_datetime(
        expenses["tx_date"]
    ).dt.strftime("%Y-%m")
    expenses["spending"] = -expenses["amount"]

    monthly_spending = (
        expenses.groupby(["month", "category"], as_index=False)
        ["spending"].sum()
    )

    comparison = budgets.merge(
        monthly_spending,
        on=["month", "category"],
        how="left",
    )
    comparison["spending"] = comparison["spending"].fillna(0)

    totals = (
        comparison.groupby("month", as_index=False)
        [["budget", "spending"]].sum()
        .sort_values("month")
    )

    totals["cumulative_budget"] = totals["budget"].cumsum()
    totals["cumulative_spending"] = totals["spending"].cumsum()

    plt.figure(figsize=(10, 5))
    plt.plot(
        totals["month"],
        totals["cumulative_budget"],
        marker="o",
        label="Cumulative Budget",
    )
    plt.plot(
        totals["month"],
        totals["cumulative_spending"],
        marker="o",
        label="Cumulative Spending",
    )

    plt.title("Cumulative Spending vs Budget")
    plt.xlabel("Month")
    plt.ylabel("Amount (INR)")
    plt.legend()
    plt.grid(alpha=0.3)

    save_chart("cumulative_budget.png")


if __name__ == "__main__":
    generate_all_charts()
