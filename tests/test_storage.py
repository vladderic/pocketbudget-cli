"""Tests for saving and loading the account state."""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from pocketbudget.account import Account
from pocketbudget.exceptions import (
    InvalidAmountError,
    InvalidCategoryError,
    InvalidCurrencyError,
)
from pocketbudget.storage import CorruptFileError, load_account, save_account


def test_saving_writes_account_state_to_data_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    account = Account()
    account.add_income(Decimal("100"))

    save_account(account)

    path = Path("data") / "budget.json"
    assert path.exists()
    json.loads(path.read_text())


def test_loading_rebuilds_saved_balance_and_history(tmp_path: Path) -> None:
    account = Account()
    account.add_income(Decimal("100"))
    account.add_expense(Decimal("40"), "Food")
    path = tmp_path / "budget.json"

    save_account(account, path)
    loaded = load_account(path)

    assert loaded.balance == Decimal("60")
    assert loaded.history == account.history


def test_loading_missing_file_returns_empty_account(tmp_path: Path) -> None:
    loaded = load_account(tmp_path / "missing.json")

    assert loaded.balance == Decimal("0")
    assert loaded.history == []


def test_loading_corrupted_file_does_not_crash_or_silently_change_balance(
    tmp_path: Path,
) -> None:
    path = tmp_path / "budget.json"
    path.write_text("{ definitely not valid json")

    with pytest.raises(CorruptFileError):
        load_account(path)


def test_loaded_negative_income_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text(
        json.dumps({"currency": "$", "history": [{"type": "income", "amount": "-100"}]})
    )

    with pytest.raises(InvalidAmountError):
        load_account(path)


def test_loaded_invalid_category_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text(
        json.dumps(
            {
                "currency": "$",
                "history": [
                    {"type": "expense", "amount": "10", "category": "Groceries"}
                ],
            }
        )
    )

    with pytest.raises(InvalidCategoryError):
        load_account(path)


def test_loaded_wrong_currency_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text(json.dumps({"currency": "€"}))

    with pytest.raises(InvalidCurrencyError):
        load_account(path)
