# PocketBudget

A command-line budgeting application that tracks income and expenses across a small set of spending categories (Food and Transport). Money is protected behind a validated domain model: balances and budgets can only change through explicit, validated transactions, and everything is persisted to a single JSON file (`data/budget.json`).

## Installation & Setup

Requirements: Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the `pocketbudget` command. If it is not found, run `pyenv rehash` (when using pyenv) or make sure the virtual environment's `bin` directory is on your PATH.

Install the pre-commit hooks (ruff lint, ruff format, mypy --strict, pytest):

```bash
pip install pre-commit
pre-commit install
```

## Usage

Run `pocketbudget <command>`. Every command follows the same lifecycle: it loads the saved state, runs the domain operation, and writes the result back to `data/budget.json`.

| Command | Description |
| --- | --- |
| `pocketbudget add-income <amount> <category>` | Record a deposit into the account. |
| `pocketbudget add-expense <amount> <category>` | Record an expense (blocked if it exceeds the balance or the category's budget). |
| `pocketbudget set-budget <category> <limit>` | Set a spending ceiling for a category. |
| `pocketbudget show-balance` | Print the current balance. |
| `pocketbudget show-history` | List all executed transactions. |
| `pocketbudget show-summary` | Show per-category spending against budgets. |

Only two categories are allowed: **Food** and **Transport**. The currency is always the dollar (`$`).

Example session:

```bash
$ pocketbudget add-income 100 Food
$ pocketbudget set-budget Food 60
$ pocketbudget add-expense 40 Food
$ pocketbudget show-balance
Balance: $60
$ pocketbudget show-history
income 100
expense 40 Food
$ pocketbudget show-summary
Food: spent $40 of $60 (remaining $20)
Transport: spent $0 (no budget set)
```

## Running the Tests

```bash
pytest
# or, to run the same checks as the commit hook:
pre-commit run --all-files
```

All hooks must pass before a commit is accepted.

## Design Decisions

- **Protected balance:** `Account.balance` is a read-only property with no setter, so outside code can never assign `account.balance = ...`. The only way to change it is through `add_income()` and `add_expense()`.
- **Protected history:** `Account.history` returns a fresh copy of the transaction list, and each record is an immutable tuple. Callers can mutate the copy without affecting the account's internal state.
- **Validation before mutation:** every transaction is validated (positive amount, allowed category, sufficient balance, budget remaining) before the balance, history, or budget state is touched. Failed operations leave the account unchanged and raise a domain exception (`InvalidAmountError`, `InvalidCategoryError`, `InsufficientBalanceError`, `BudgetExceededError`).
- **Strict budget limits:** an expense that exceeds a category's remaining budget is blocked with an error — even when the total balance could cover it — per the application rules in `rules.md`.
- **Persistence with safety:** state is stored as JSON in `data/budget.json`. A missing file yields a clean account; a corrupted file raises `CorruptFileError` rather than crashing or silently returning a wrong balance. Loaded data passes through the same validation as live data.
- **TDD:** every behaviour above was driven by tests written first (`tests/`), which remain the source of truth for the domain rules in `rules.md`.
