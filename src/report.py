
"""Generate CSV and Excel financial reports from the expense database."""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("db/expenses.db")
OUTPUT_DIR = Path("outputs")


def load_report_data():
    if not DB_PATH.is_file():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            """
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
            """,
            conn,
        )

    if df.empty:
        raise ValueError("No transactions available for reporting.")

    df["tx_date"] = pd.to_datetime(df["tx_date"])
    df["month"] = df["tx_date"].dt.strftime("%Y-%m")
    df["income"] = df["amount"].clip(lower=0)
    df["expenses"] = -df["amount"].clip(upper=0)

    return df


def generate_monthly_report():
    df = load_report_data()

    report = (
        df.groupby("month", as_index=False)[["income", "expenses"]]
        .sum()
        .sort_values("month")
    )

    report["savings"] = report["income"] - report["expenses"]

    report["savings_rate"] = (
        report["savings"]
        .div(report["income"].replace(0, float("nan")))
        .mul(100)
        .fillna(0)
        .round(2)
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_path = OUTPUT_DIR / "financial_report.csv"
    excel_path = OUTPUT_DIR / "financial_report.xlsx"

    report.to_csv(csv_path, index=False)

    expenses_df = df[df["amount"] < 0].copy()

    category_summary = (
        expenses_df.groupby(
            ["month", "category"], as_index=False
        )["expenses"]
        .sum()
        .sort_values(["month", "category"])
    )

    transactions_export = df[
        ["tx_date", "description", "category", "account", "amount"]
    ].copy()

    with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
        report.to_excel(
            writer, sheet_name="Monthly Summary", index=False
        )

        transactions_export.to_excel(
            writer, sheet_name="Transactions", index=False
        )

        category_summary.to_excel(
            writer, sheet_name="Category Summary", index=False
        )

        workbook = writer.book

        header_format = workbook.add_format({
            "bold": True,
            "bg_color": "#17365D",
            "font_color": "white",
            "border": 1,
        })

        money_format = workbook.add_format({
            "num_format": '#,##0.00',
        })

        date_format = workbook.add_format({
            "num_format": "yyyy-mm-dd",
        })

        for sheet_name, dataframe in [
            ("Monthly Summary", report),
            ("Transactions", transactions_export),
            ("Category Summary", category_summary),
        ]:
            worksheet = writer.sheets[sheet_name]
            worksheet.freeze_panes(1, 0)

            for col_num, column_name in enumerate(dataframe.columns):
                worksheet.write(
                    0, col_num, column_name, header_format
                )

                width = min(
                    max(
                        16,
                        len(column_name) + 3,
                        dataframe[column_name]
                        .astype(str)
                        .str.len()
                        .max() + 2
                        if not dataframe.empty else 16,
                    ),
                    45,
                )

                worksheet.set_column(col_num, col_num, width)

            worksheet.autofilter(
                0, 0, len(dataframe), len(dataframe.columns) - 1
            )

        monthly_sheet = writer.sheets["Monthly Summary"]
        monthly_sheet.set_column("B:D", 18, money_format)

        transactions_sheet = writer.sheets["Transactions"]
        transactions_sheet.set_column("A:A", 16, date_format)
        transactions_sheet.set_column("E:E", 18, money_format)

        category_sheet = writer.sheets["Category Summary"]
        category_sheet.set_column("C:C", 18, money_format)

    print("\nMONTHLY FINANCIAL REPORT")
    print("=" * 50)
    print(report.to_string(index=False))

    print(f"\nCSV REPORT SAVED: {csv_path}")
    print(f"EXCEL REPORT SAVED: {excel_path}")
    print("FINANCIAL REPORTS GENERATED SUCCESSFULLY")

    return report


if __name__ == "__main__":
    generate_monthly_report()

def export_month(month):
    """Export transactions and category spending for one month."""
    import sqlite3
    from pathlib import Path
    import pandas as pd

    db_path = Path("db/expenses.db")
    output_dir = Path("outputs")

    if not db_path.is_file():
        raise FileNotFoundError(f"Database not found: {db_path}")

    month = str(month)

    if not pd.Series([month]).str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])").all():
        raise ValueError("Month must use YYYY-MM format.")

    with sqlite3.connect(db_path) as conn:
        transactions = pd.read_sql_query(
            """
            SELECT
                t.tx_date,
                t.description,
                COALESCE(c.name, 'Uncategorized') AS category,
                t.account,
                t.amount
            FROM transactions AS t
            LEFT JOIN categories AS c
                ON t.category_id = c.id
            WHERE substr(t.tx_date, 1, 7) = ?
            ORDER BY t.tx_date
            """,
            conn,
            params=(month,),
        )

    if transactions.empty:
        raise ValueError(f"No transactions found for {month}")

    expenses = transactions[transactions["amount"] < 0].copy()
    expenses["expenses"] = -expenses["amount"]

    category_summary = (
        expenses.groupby("category", as_index=False)["expenses"]
        .sum()
        .sort_values("expenses", ascending=False)
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"financial_report_{month}.xlsx"

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        transactions.to_excel(
            writer, sheet_name="Transactions", index=False
        )
        category_summary.to_excel(
            writer, sheet_name="Category Summary", index=False
        )

        for sheet in writer.sheets.values():
            sheet.set_column("A:A", 20)
            sheet.set_column("B:E", 25)

    print(f"MONTHLY EXPORT SAVED: {output_file}")
    return output_file
