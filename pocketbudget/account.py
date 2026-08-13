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
TransactionRecord = tuple[str, Decimal] | tuple[str, Decimal, str]

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
        self._spent: dict[str, Decimal] = {
            category: Decimal("0") for category in CATEGORIES
        }
        self._history: list[TransactionRecord] = []

    @property
    def balance(self) -> Decimal:
        """Read-only view of the current balance."""
        return self._balance

    @property
    def history(self) -> list[TransactionRecord]:
        """Defensive copy of the transaction history."""
        return list(self._history)

    @property
    def budgets(self) -> dict[str, Decimal | None]:
        """Defensive copy of the category budgets (None means unlimited)."""
        return dict(self._budgets)

    def add_income(self, amount: Money) -> None:
        """Record an income transaction and update the balance."""
        value = self._validate_amount(amount)
        self._balance += value
        self._history.append(("income", value))

    def add_expense(self, amount: Money, category: str) -> None:
        """Record an expense transaction and update the balance."""
        value = self._validate_amount(amount)
        self._validate_category(category)
        if value > self._balance:
            raise InsufficientBalanceError(value, self._balance)
        budget = self._budgets[category]
        if budget is not None:
            remaining = budget - self._spent[category]
            if value > remaining:
                raise BudgetExceededError(category, budget, value)
            self._spent[category] += value
        self._balance -= value
        self._history.append(("expense", value, category))

    def set_budget(self, category: str, amount: Money) -> None:
        """Set the spending limit for a category."""
        self._validate_category(category)
        self._budgets[category] = self._validate_amount(amount)
        self._spent[category] = Decimal("0")

    def remaining_budget(self, category: str) -> Decimal | None:
        """Return the amount left to spend in a category, or None if unlimited."""
        self._validate_category(category)
        budget = self._budgets[category]
        if budget is None:
            return None
        return budget - self._spent[category]

    def _validate_amount(self, amount: Money) -> Decimal:
        try:
            value = Decimal(amount)
        except (TypeError, ValueError, ArithmeticError) as exc:
            raise InvalidAmountError(amount) from exc
        if value <= Decimal("0"):
            raise InvalidAmountError(value)
        return value

    def _validate_category(self, category: str) -> None:
        if category not in CATEGORIES:
            raise InvalidCategoryError(category)
