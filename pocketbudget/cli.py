"""CLI: user input and command routing."""

from collections.abc import Callable
from decimal import Decimal
from sys import argv, stderr

from pocketbudget.account import CATEGORIES, Account, TransactionRecord
from pocketbudget.exceptions import PocketBudgetError
from pocketbudget.storage import load_account, save_account


def main(args: list[str] | None = None) -> int:
    """Route the command-line arguments to the matching command."""
    arguments = argv[1:] if args is None else args
    if not arguments:
        print("Hello PocketBudget")
        return 0
    command, *rest = arguments
    try:
        return _dispatch(command, rest)
    except (PocketBudgetError, ValueError) as exc:
        print(f"Error: {exc}", file=stderr)
        return 1


def _add_income(args: list[str]) -> int:
    _require(args, 2, "Usage: add-income <amount> <category>")
    account = load_account()
    account.add_income(Decimal(args[0]))
    save_account(account)
    return 0


def _add_expense(args: list[str]) -> int:
    _require(args, 2, "Usage: add-expense <amount> <category>")
    account = load_account()
    account.add_expense(Decimal(args[0]), args[1])
    save_account(account)
    return 0


def _set_budget(args: list[str]) -> int:
    _require(args, 2, "Usage: set-budget <category> <limit>")
    account = load_account()
    account.set_budget(args[0], Decimal(args[1]))
    save_account(account)
    return 0


def _show_balance(args: list[str]) -> int:
    _require(args, 0, "Usage: show-balance")
    account = load_account()
    print(f"Balance: ${account.balance}")
    return 0


def _show_history(args: list[str]) -> int:
    _require(args, 0, "Usage: show-history")
    account = load_account()
    for record in account.history:
        print(_format_record(record))
    return 0


def _show_summary(args: list[str]) -> int:
    _require(args, 0, "Usage: show-summary")
    account = load_account()
    print(_format_summary(account))
    return 0


_COMMANDS: dict[str, Callable[[list[str]], int]] = {
    "add-income": _add_income,
    "add-expense": _add_expense,
    "set-budget": _set_budget,
    "show-balance": _show_balance,
    "show-history": _show_history,
    "show-summary": _show_summary,
}


def _dispatch(command: str, args: list[str]) -> int:
    handler = _COMMANDS.get(command)
    if handler is None:
        raise ValueError(f"Unknown command: {command}")
    return handler(args)


def _require(args: list[str], count: int, usage: str) -> None:
    if len(args) != count:
        raise ValueError(usage)


def _format_record(record: TransactionRecord) -> str:
    if len(record) == 3:
        _, amount, category = record
        return f"expense {amount} {category}"
    _, amount = record
    return f"income {amount}"


def _format_summary(account: Account) -> str:
    lines = [_format_category_line(account, category) for category in CATEGORIES]
    return "\n".join(lines)


def _format_category_line(account: Account, category: str) -> str:
    spent = _spent_in_category(account, category)
    remaining = account.remaining_budget(category)
    if remaining is None:
        return f"{category}: spent ${spent} (no budget set)"
    total = spent + remaining
    return f"{category}: spent ${spent} of ${total} (remaining ${remaining})"


def _spent_in_category(account: Account, category: str) -> Decimal:
    total = Decimal("0")
    for record in account.history:
        if len(record) == 3 and record[2] == category:
            total += record[1]
    return total


if __name__ == "__main__":
    raise SystemExit(main())
