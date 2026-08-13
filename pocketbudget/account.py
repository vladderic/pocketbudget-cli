"""Domain: budgeting rules and protected account state."""

from decimal import Decimal

from pocketbudget.exceptions import (
    BudgetExceededError,
    InsufficientBalanceError,
    InvalidAmountError,
    InvalidCategoryError,
    InvalidCurrencyError,
)

Money = Decimal | int | str

CURRENCY = "$"
CATEGORIES: tuple[str, ...] = ("Food", "Transport")


class Account:
    """Protected account state; the balance only changes via transactions."""

    def __init__(self, currency: str = CURRENCY) -> None:
        if currency != CURRENCY:
            raise InvalidCurrencyError(currency)
        self._balance: Decimal = Decimal("0")
        self._budgets: dict[str, Decimal | None] = {
            category: None for category in CATEGORIES
        }

    @property
    def balance(self) -> Decimal:
        """Read-only view of the current balance."""
        return self._balance

    def add_income(self, amount: Money) -> None:
        """Record an income transaction and update the balance."""
        value = self._validate_amount(amount)
        self._balance += value

    def add_expense(self, amount: Money, category: str) -> None:
        """Record an expense transaction and update the balance."""
        value = self._validate_amount(amount)
        self._validate_category(category)
        if value > self._balance:
            raise InsufficientBalanceError(value, self._balance)
        budget = self._budgets[category]
        if budget is not None and value > budget:
            raise BudgetExceededError(category, budget, value)
        self._balance -= value

    def set_budget(self, category: str, amount: Money) -> None:
        """Set the spending limit for a category."""
        self._validate_category(category)
        self._budgets[category] = self._validate_amount(amount)

    def _validate_amount(self, amount: Money) -> Decimal:
        value = Decimal(amount)
        if value <= Decimal("0"):
            raise InvalidAmountError(value)
        return value

    def _validate_category(self, category: str) -> None:
        if category not in CATEGORIES:
            raise InvalidCategoryError(category)
