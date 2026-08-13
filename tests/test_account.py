"""Single source of truth for account balance behaviour.

These tests are the contract for how money may move into and out of the
account, and they must match rules.md.
"""

from decimal import Decimal

import pytest

from pocketbudget.account import Account
from pocketbudget.exceptions import (
    BudgetExceededError,
    InsufficientBalanceError,
    InvalidAmountError,
    InvalidCategoryError,
    InvalidCurrencyError,
)


def test_new_account_starts_at_zero() -> None:
    account = Account()
    assert account.balance == Decimal("0")


def test_balance_is_readable_from_outside() -> None:
    account = Account()
    account.add_income(Decimal("100"))
    assert account.balance == Decimal("100")


def test_balance_cannot_be_assigned_from_outside() -> None:
    account = Account()
    with pytest.raises(AttributeError):
        account.balance = Decimal("500")  # type: ignore[misc]


def test_only_income_and_expense_change_balance() -> None:
    account = Account()
    account.add_income(Decimal("100"))
    account.add_expense(Decimal("40"), "Food")
    assert account.balance == Decimal("60")


def test_income_accumulates() -> None:
    account = Account()
    account.add_income(Decimal("10"))
    account.add_income(Decimal("15.50"))
    assert account.balance == Decimal("25.50")


def test_expense_reduces_balance() -> None:
    account = Account()
    account.add_income(Decimal("100"))
    account.add_expense(Decimal("37.25"), "Transport")
    assert account.balance == Decimal("62.75")


@pytest.mark.parametrize("bad_amount", [-10, 0, -Decimal("0.01")])
def test_negative_or_zero_income_is_rejected(bad_amount: Decimal | int) -> None:
    account = Account()
    with pytest.raises(InvalidAmountError):
        account.add_income(bad_amount)
    assert account.balance == Decimal("0")


@pytest.mark.parametrize("bad_amount", [-10, 0, -Decimal("0.01")])
def test_negative_or_zero_expense_is_rejected(bad_amount: Decimal | int) -> None:
    account = Account()
    with pytest.raises(InvalidAmountError):
        account.add_expense(bad_amount, "Food")
    assert account.balance == Decimal("0")


def test_expense_larger_than_balance_is_blocked() -> None:
    account = Account()
    account.add_income(Decimal("50"))
    with pytest.raises(InsufficientBalanceError):
        account.add_expense(Decimal("60"), "Food")
    assert account.balance == Decimal("50")


def test_balance_never_goes_negative() -> None:
    account = Account()
    account.add_income(Decimal("10"))
    with pytest.raises(InsufficientBalanceError):
        account.add_expense(Decimal("10.01"), "Transport")
    assert account.balance == Decimal("10")


def test_expense_of_full_balance_is_allowed() -> None:
    account = Account()
    account.add_income(Decimal("50"))
    account.add_expense(Decimal("50"), "Food")
    assert account.balance == Decimal("0")


def test_only_dollar_currency_is_allowed() -> None:
    with pytest.raises(InvalidCurrencyError):
        Account(currency="€")


def test_dollar_currency_is_accepted() -> None:
    account = Account(currency="$")
    assert account.balance == Decimal("0")


@pytest.mark.parametrize("bad_category", ["Groceries", "Clothing", ""])
def test_unknown_category_is_rejected(bad_category: str) -> None:
    account = Account()
    with pytest.raises(InvalidCategoryError):
        account.add_expense(Decimal("10"), bad_category)
    assert account.balance == Decimal("0")


def test_expense_within_budget_is_allowed() -> None:
    account = Account()
    account.add_income(Decimal("100"))
    account.set_budget("Food", Decimal("30"))
    account.add_expense(Decimal("30"), "Food")
    assert account.balance == Decimal("70")


def test_expense_over_budget_is_blocked() -> None:
    account = Account()
    account.add_income(Decimal("100"))
    account.set_budget("Food", Decimal("30"))
    with pytest.raises(BudgetExceededError):
        account.add_expense(Decimal("31"), "Food")
    assert account.balance == Decimal("100")
