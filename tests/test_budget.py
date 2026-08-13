"""Tests for category spending limits.

These tests match rules.md Rule 4: an expense that exceeds a category's
budget is blocked with an error message, even when the balance covers it.
"""

from decimal import Decimal

import pytest

from pocketbudget.account import Account
from pocketbudget.exceptions import BudgetExceededError


@pytest.mark.parametrize("category", ["Food", "Transport"])
def test_budget_can_be_set_for_a_category(category: str) -> None:
    account = Account()
    account.set_budget(category, Decimal("100"))

    assert account.remaining_budget(category) == Decimal("100")


def test_remaining_budget_decreases_after_expense() -> None:
    account = Account()
    account.set_budget("Food", Decimal("100"))
    account.add_income(Decimal("200"))

    account.add_expense(Decimal("30"), "Food")

    assert account.remaining_budget("Food") == Decimal("70")


def test_expense_that_uses_the_full_budget_is_allowed() -> None:
    account = Account()
    account.set_budget("Food", Decimal("100"))
    account.add_income(Decimal("100"))

    account.add_expense(Decimal("100"), "Food")

    assert account.remaining_budget("Food") == Decimal("0")


def test_expense_exceeding_remaining_budget_is_blocked() -> None:
    account = Account()
    account.set_budget("Food", Decimal("100"))
    account.add_income(Decimal("200"))
    account.add_expense(Decimal("80"), "Food")

    with pytest.raises(BudgetExceededError):
        account.add_expense(Decimal("21"), "Food")

    assert account.remaining_budget("Food") == Decimal("20")


def test_expense_over_budget_is_blocked_even_when_balance_covers_it() -> None:
    account = Account()
    account.set_budget("Food", Decimal("50"))
    account.add_income(Decimal("500"))

    with pytest.raises(BudgetExceededError):
        account.add_expense(Decimal("51"), "Food")

    assert account.balance == Decimal("500")
    assert account.remaining_budget("Food") == Decimal("50")


def test_over_budget_error_displays_a_message() -> None:
    account = Account()
    account.set_budget("Food", Decimal("50"))
    account.add_income(Decimal("500"))

    with pytest.raises(BudgetExceededError) as excinfo:
        account.add_expense(Decimal("51"), "Food")

    assert "budget" in str(excinfo.value)
