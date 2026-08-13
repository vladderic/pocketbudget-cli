"""Tests for the command-line interface."""

from decimal import Decimal
from pathlib import Path

import pytest

from pocketbudget.cli import main
from pocketbudget.storage import load_account


def _run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *args: str) -> int:
    monkeypatch.chdir(tmp_path)
    return main(list(args))


def test_add_income_records_a_deposit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert _run(tmp_path, monkeypatch, "add-income", "100", "Food") == 0
    assert load_account().balance == Decimal("100")


def test_add_income_accumulates_across_commands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _run(tmp_path, monkeypatch, "add-income", "100", "Food")
    _run(tmp_path, monkeypatch, "add-income", "50", "Food")
    assert load_account().balance == Decimal("150")


def test_add_expense_records_and_validates_against_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _run(tmp_path, monkeypatch, "add-income", "200", "Food")
    _run(tmp_path, monkeypatch, "set-budget", "Food", "100")
    assert _run(tmp_path, monkeypatch, "add-expense", "80", "Food") == 0
    account = load_account()
    assert account.balance == Decimal("120")
    assert account.remaining_budget("Food") == Decimal("20")


def test_add_expense_over_budget_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _run(tmp_path, monkeypatch, "add-income", "500", "Food")
    _run(tmp_path, monkeypatch, "set-budget", "Food", "100")
    exit_code = _run(tmp_path, monkeypatch, "add-expense", "101", "Food")
    account = load_account()
    assert exit_code != 0
    assert account.balance == Decimal("500")
    assert account.remaining_budget("Food") == Decimal("100")


def test_show_balance_prints_current_balance(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(tmp_path, monkeypatch, "add-income", "100", "Food")
    _run(tmp_path, monkeypatch, "add-expense", "40", "Food")
    _run(tmp_path, monkeypatch, "show-balance")
    assert "60" in capsys.readouterr().out


def test_show_history_lists_all_transactions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(tmp_path, monkeypatch, "add-income", "100", "Food")
    _run(tmp_path, monkeypatch, "add-expense", "40", "Food")
    _run(tmp_path, monkeypatch, "show-history")
    captured = capsys.readouterr().out
    assert "income" in captured
    assert "100" in captured
    assert "expense" in captured
    assert "40" in captured


def test_set_budget_sets_a_spending_ceiling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _run(tmp_path, monkeypatch, "set-budget", "Food", "200")
    assert load_account().remaining_budget("Food") == Decimal("200")


def test_show_summary_visualises_category_spending(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(tmp_path, monkeypatch, "set-budget", "Food", "100")
    _run(tmp_path, monkeypatch, "add-income", "200", "Food")
    _run(tmp_path, monkeypatch, "add-expense", "30", "Food")
    _run(tmp_path, monkeypatch, "show-summary")
    captured = capsys.readouterr().out
    assert "Food" in captured
    assert "30" in captured
    assert "70" in captured
