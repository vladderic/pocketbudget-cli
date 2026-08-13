"""Test that the account history is protected from outside mutation."""

from decimal import Decimal

from pocketbudget.account import Account


def test_mutating_returned_history_does_not_change_account_history() -> None:
    account = Account()
    account.add_income(Decimal("100"))
    account.add_expense(Decimal("40"), "Food")

    returned = account.history
    returned.append(("expense", Decimal("999"), "Transport"))

    assert account.history == [
        ("income", Decimal("100")),
        ("expense", Decimal("40"), "Food"),
    ]


def test_clearing_returned_history_does_not_change_account_history() -> None:
    account = Account()
    account.add_income(Decimal("100"))

    returned = account.history
    returned.clear()

    assert account.history == [("income", Decimal("100"))]
