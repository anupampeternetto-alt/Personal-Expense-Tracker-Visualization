
"""Generate additional synthetic expense CSV records."""

import csv
import random
from datetime import date
from pathlib import Path

OUTPUT = Path("data/multimonth_expenses.csv")

EXPENSES = [
    ("Swiggy Lunch", -350, "UPI"),
    ("Uber Ride", -220, "UPI"),
    ("DMart Groceries", -1200, "Card"),
    ("Netflix Subscription", -199, "UPI"),
    ("Amazon Shopping", -1800, "Card"),
    ("Electricity Bill", -950, "Bank"),
    ("Zomato Dinner", -450, "UPI"),
    ("Metro Travel", -100, "Cash"),
    ("College Books", -750, "Card"),
]


def generate_data():
    random.seed(42)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    records = []

    for month in [9, 10]:
        records.append([
            date(2026, month, 4).isoformat(),
            "Monthly Allowance",
            15000,
            "Bank",
        ])

        for day, (description, amount, account) in enumerate(
            EXPENSES, start=1
        ):
            multiplier = random.uniform(0.75, 1.25)
            adjusted_amount = -round(abs(amount) * multiplier)

            records.append([
                date(2026, month, day).isoformat(),
                description,
                adjusted_amount,
                account,
            ])

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Date", "Description", "Amount", "Account"
        ])
        writer.writerows(records)

    print(f"SYNTHETIC RECORDS GENERATED: {len(records)}")
    print(f"CSV FILE: {OUTPUT}")
    print("MULTI-MONTH DATA GENERATION SUCCESSFUL")


if __name__ == "__main__":
    generate_data()
