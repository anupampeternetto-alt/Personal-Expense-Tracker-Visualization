
import pandas as pd
import pytest

from src.ingest import read_expense_csv


def write_csv(tmp_path, rows):
    path = tmp_path / "test_expenses.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_valid_csv(tmp_path):
    path = write_csv(tmp_path, [{
        "Date": "2026-11-01",
        "Description": "Groceries",
        "Amount": -500,
        "Account": "Bank"
    }])

    clean, rejected = read_expense_csv(path)

    assert len(clean) == 1
    assert len(rejected) == 0
    assert clean.iloc[0]["amount"] == -500
    assert clean.iloc[0]["tx_date"] == "2026-11-01"


def test_missing_required_column(tmp_path):
    path = write_csv(tmp_path, [{
        "Date": "2026-11-01",
        "Description": "Food",
        "Amount": -200
    }])

    with pytest.raises(ValueError, match="Missing required columns"):
        read_expense_csv(path)


def test_invalid_date(tmp_path):
    path = write_csv(tmp_path, [{
        "Date": "invalid-date",
        "Description": "Food",
        "Amount": -200,
        "Account": "Cash"
    }])

    clean, rejected = read_expense_csv(path)

    assert len(clean) == 0
    assert len(rejected) == 1


def test_zero_amount(tmp_path):
    path = write_csv(tmp_path, [{
        "Date": "2026-11-01",
        "Description": "Food",
        "Amount": 0,
        "Account": "Cash"
    }])

    clean, rejected = read_expense_csv(path)

    assert len(clean) == 0
    assert len(rejected) == 1


def test_empty_description(tmp_path):
    path = write_csv(tmp_path, [{
        "Date": "2026-11-01",
        "Description": "   ",
        "Amount": -100,
        "Account": "Cash"
    }])

    clean, rejected = read_expense_csv(path)

    assert len(clean) == 0
    assert len(rejected) == 1


def test_mixed_valid_invalid_rows(tmp_path):
    path = write_csv(tmp_path, [
        {
            "Date": "2026-11-01",
            "Description": "Food",
            "Amount": -200,
            "Account": "Cash"
        },
        {
            "Date": "invalid-date",
            "Description": "Shopping",
            "Amount": -500,
            "Account": "Bank"
        },
        {
            "Date": "2026-11-03",
            "Description": "Salary",
            "Amount": 15000,
            "Account": "Bank"
        }
    ])

    clean, rejected = read_expense_csv(path)

    assert len(clean) == 2
    assert len(rejected) == 1
    assert clean["amount"].sum() == 14800
