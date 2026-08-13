"""Deliberately bad input raises the right custom exception."""

from decimal import Decimal
from pathlib import Path

import pytest

from pocketbudget.account import Account
from pocketbudget.exceptions import BudgetExceededError, InvalidAmountError
from pocketbudget.storage import CorruptFileError, load_account


@pytest.mark.parametrize("bad_amount", [Decimal("-1"), Decimal("-0.01")])
def test_negative_amount_raises_invalid_amount_error(bad_amount: Decimal) -> None:
    account = Account()

    with pytest.raises(InvalidAmountError):
        account.add_income(bad_amount)
    with pytest.raises(InvalidAmountError):
        account.add_expense(bad_amount, "Food")

    assert account.balance == Decimal("0")
    assert account.history == []


@pytest.mark.parametrize("bad_amount", ["abc", "12x"])
def test_non_numeric_amount_raises_invalid_amount_error(bad_amount: str) -> None:
    account = Account()

    with pytest.raises(InvalidAmountError):
        account.add_income(bad_amount)

    assert account.balance == Decimal("0")
    assert account.history == []


def test_invalid_amount_error_message() -> None:
    account = Account()

    with pytest.raises(InvalidAmountError) as excinfo:
        account.add_income(Decimal("-5"))

    assert "positive" in str(excinfo.value)


def test_expense_over_budget_raises_budget_exceeded_error() -> None:
    account = Account()
    account.add_income(Decimal("500"))
    account.set_budget("Food", Decimal("100"))

    with pytest.raises(BudgetExceededError):
        account.add_expense(Decimal("101"), "Food")

    assert account.balance == Decimal("500")
    assert account.remaining_budget("Food") == Decimal("100")
    assert account.history == [("income", Decimal("500"))]


def test_corrupted_file_raises_corrupt_file_error(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text("{ this is not valid json")

    with pytest.raises(CorruptFileError):
        load_account(path)


def test_non_object_file_raises_corrupt_file_error(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text("[1, 2, 3]")

    with pytest.raises(CorruptFileError):
        load_account(path)
