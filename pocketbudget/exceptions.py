"""Custom domain exceptions."""

from decimal import Decimal


class PocketBudgetError(Exception):
    """Base class for all PocketBudget domain errors."""


class InvalidAmountError(PocketBudgetError):
    """Raised when a transaction amount is not a positive number."""

    def __init__(self, amount: object) -> None:
        super().__init__(f"Amount must be a positive number, got {amount!r}.")


class InvalidCategoryError(PocketBudgetError):
    """Raised when a transaction uses a category that is not allowed."""

    def __init__(self, category: str) -> None:
        super().__init__(
            f"Unknown category '{category}'. Allowed categories are Food and Transport."
        )


class InvalidCurrencyError(PocketBudgetError):
    """Raised when a currency other than the dollar is used."""

    def __init__(self, currency: str) -> None:
        super().__init__(f"Only $ currency is supported, got '{currency}'.")


class InsufficientBalanceError(PocketBudgetError):
    """Raised when an expense is larger than the current balance."""

    def __init__(self, amount: Decimal, balance: Decimal) -> None:
        super().__init__(f"Cannot spend {amount} with a balance of {balance}.")


class BudgetExceededError(PocketBudgetError):
    """Raised when an expense exceeds its category's budget."""

    def __init__(self, category: str, budget: Decimal, amount: Decimal) -> None:
        super().__init__(
            f"Expense of {amount} exceeds the {category} budget of {budget}."
        )
