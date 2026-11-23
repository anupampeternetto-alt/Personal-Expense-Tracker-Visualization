
"""Personal Expense Tracker - Interactive Dashboard."""

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = Path("db/expenses.db")

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="\U0001F4B0",
    layout="wide",
)

st.title("\U0001F4B0 Personal Expense Tracker")
st.caption("Interactive Financial Analytics Dashboard")


@st.cache_data(ttl=60)
def load_transactions():
    """Read transactions and categories from SQLite."""
    if not DB_PATH.exists():
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as conn:
        query = """
        SELECT
            t.tx_date,
            t.description,
            t.amount,
            t.account,
            COALESCE(c.name, 'Uncategorized') AS category
        FROM transactions AS t
        LEFT JOIN categories AS c
            ON t.category_id = c.id
        ORDER BY t.tx_date
        """
        return pd.read_sql_query(query, conn)


df = load_transactions()

if df.empty:
    st.warning("No transactions found. Import your CSV first.")
    st.stop()

df["tx_date"] = pd.to_datetime(df["tx_date"])
df["month"] = df["tx_date"].dt.strftime("%Y-%m")

# Sidebar filters
st.sidebar.header("Dashboard Filters")

months = sorted(df["month"].unique().tolist())

selected_months = st.sidebar.multiselect(
    "Select Months",
    options=months,
    default=months,
)

filtered = df[df["month"].isin(selected_months)].copy()

if filtered.empty:
    st.warning("Select at least one month to view the dashboard.")
    st.stop()

# Financial calculations
income = filtered.loc[
    filtered["amount"] > 0, "amount"
].sum()

expenses = -filtered.loc[
    filtered["amount"] < 0, "amount"
].sum()

savings = income - expenses

savings_rate = (
    savings / income * 100 if income > 0 else 0
)

# Financial KPI cards
st.subheader("Financial Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Income", f"\u20B9{income:,.2f}")
col2.metric("Total Expenses", f"\u20B9{expenses:,.2f}")
col3.metric("Net Savings", f"\u20B9{savings:,.2f}")
col4.metric("Savings Rate", f"{savings_rate:.2f}%")

expense_df = filtered[filtered["amount"] < 0].copy()
expense_df["spending"] = -expense_df["amount"]

if expense_df.empty:
    st.info("No expenses found for the selected period.")
else:
    category = (
        expense_df.groupby("category", as_index=False)
        ["spending"].sum()
        .sort_values("spending", ascending=False)
    )

    monthly = (
        expense_df.groupby("month", as_index=False)
        ["spending"].sum()
        .sort_values("month")
    )

    payment = (
        expense_df.groupby("account", as_index=False)
        ["spending"].sum()
    )

    daily = (
        expense_df.groupby("tx_date", as_index=False)
        ["spending"].sum()
        .sort_values("tx_date")
    )

    st.subheader("Expense Visualizations")

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            category,
            x="spending",
            y="category",
            orientation="h",
            title="Category-wise Spending",
            labels={
                "spending": "Spending (INR)",
                "category": "Category",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.line(
            monthly,
            x="month",
            y="spending",
            markers=True,
            title="Monthly Spending Trend",
            labels={
                "month": "Month",
                "spending": "Spending (INR)",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    left2, right2 = st.columns(2)

    with left2:
        fig = px.pie(
            payment,
            names="account",
            values="spending",
            title="Payment Method Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    with right2:
        fig = px.line(
            daily,
            x="tx_date",
            y="spending",
            markers=True,
            title="Daily Spending Trend",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Spending Insights")

    highest = category.iloc[0]

    st.info(
        f"Highest spending category: "
        f"{highest['category']} "
        f"(\u20B9{highest['spending']:,.2f})"
    )

# Budget analysis
st.subheader("Budget Alerts")

try:
    with sqlite3.connect(DB_PATH) as conn:
        budgets = pd.read_sql_query(
            """
            SELECT
                b.month, b.category_name AS category, b.limit_amount AS budget FROM budgets b
            """,
            conn,
        )

    if budgets.empty:
        st.info("No budgets configured.")
    else:
        spending_by_month = (
            expense_df.groupby(
                ["month", "category"], as_index=False
            )["spending"].sum()
        )

        budget_view = budgets[
            budgets["month"].isin(selected_months)
        ].copy()

        budget_view = budget_view.merge(
            spending_by_month,
            on=["month", "category"],
            how="left",
        )

        budget_view["spending"] = (
            budget_view["spending"].fillna(0)
        )

        budget_view["remaining"] = (
            budget_view["budget"]
            - budget_view["spending"]
        )

        budget_view["status"] = budget_view.apply(
            lambda row: (
                "OVER BUDGET"
                if row["remaining"] < 0
                else "WARNING"
                if row["budget"] > 0
                and row["spending"] >= row["budget"] * 0.8
                else "WITHIN BUDGET"
            ),
            axis=1,
        )

        st.dataframe(
            budget_view,
            use_container_width=True,
            hide_index=True,
        )

        alerts = budget_view[
            budget_view["status"] == "OVER BUDGET"
        ]

        if not alerts.empty:
            st.error(
                f"{len(alerts)} category budget(s) exceeded."
            )

except (sqlite3.Error, KeyError) as error:
    st.warning(f"Budget data unavailable: {error}")

# Transaction history
st.subheader("Transaction History")

st.dataframe(
    filtered.sort_values(
        "tx_date", ascending=False
    ),
    use_container_width=True,
    hide_index=True,
)

# Download CSV
csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Transactions CSV",
    data=csv_data,
    file_name="expense_transactions.csv",
    mime="text/csv",
)

st.success("Dashboard loaded successfully!")
