"""Storage: saving and loading application state."""

import json
from decimal import Decimal
from pathlib import Path

from pocketbudget.account import Account, TransactionRecord

DEFAULT_DATA_PATH = Path("data") / "budget.json"


class StorageError(Exception):
    """Base class for storage errors."""


class CorruptFileError(StorageError):
    """Raised when the save file cannot be parsed or is malformed."""


def save_account(account: Account, path: Path = DEFAULT_DATA_PATH) -> None:
    """Write the account state to a JSON file at ``path``."""
    payload = {
        "currency": "$",
        "history": [_record_to_dict(record) for record in account.history],
        "budgets": {
            category: str(budget)
            for category, budget in account.budgets.items()
            if budget is not None
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))


def load_account(path: Path = DEFAULT_DATA_PATH) -> Account:
    """Load the account state from a JSON file.

    A missing file yields a clean, empty account. A file that cannot be
    parsed raises :class:`CorruptFileError`; invalid account data raises
    the same domain errors as live transactions.
    """
    if not path.exists():
        return Account()
    try:
        payload = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise CorruptFileError(str(path)) from exc
    return _account_from_payload(payload)


def _record_to_dict(record: TransactionRecord) -> dict[str, str]:
    if len(record) == 3:
        _, amount, category = record
        return {"type": "expense", "amount": str(amount), "category": category}
    _, amount = record
    return {"type": "income", "amount": str(amount)}


def _account_from_payload(payload: object) -> Account:
    if not isinstance(payload, dict):
        raise CorruptFileError("Save file is not a JSON object.")
    currency = payload.get("currency", "$")
    if not isinstance(currency, str):
        raise CorruptFileError("Save file has an invalid currency.")
    account = Account(currency=currency)
    _restore_budgets(account, payload.get("budgets", {}))
    history = payload.get("history", [])
    if not isinstance(history, list):
        raise CorruptFileError("Save file has an invalid history.")
    for entry in history:
        _apply_entry(account, entry)
    return account


def _restore_budgets(account: Account, budgets: object) -> None:
    if not isinstance(budgets, dict):
        raise CorruptFileError("Save file has invalid budgets.")
    for category, amount in budgets.items():
        if isinstance(category, str) and isinstance(amount, (str, int)):
            account.set_budget(category, amount)
            continue
        raise CorruptFileError("Save file has a malformed budget.")


def _apply_entry(account: Account, entry: object) -> None:
    if not isinstance(entry, dict):
        raise CorruptFileError("Save file has a malformed history entry.")
    kind = entry.get("type")
    amount = entry.get("amount")
    if kind == "income":
        if isinstance(amount, (str, int, Decimal)):
            account.add_income(amount)
            return
        raise CorruptFileError("Save file has a malformed income entry.")
    if kind == "expense":
        category = entry.get("category")
        if isinstance(amount, (str, int, Decimal)) and isinstance(category, str):
            account.add_expense(amount, category)
            return
        raise CorruptFileError("Save file has a malformed expense entry.")
    raise CorruptFileError("Save file has an unknown transaction type.")
