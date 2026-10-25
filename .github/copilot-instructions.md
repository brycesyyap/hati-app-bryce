# Hati development instructions

## Commands

- Install runtime and test dependencies: `python -m pip install -e . pytest httpx`
- Run all tests: `pytest -q`
- Run one test: `pytest test_main.py::test_split_expense_between_roommates -q`
- Lint: `ruff check .`
- Run the app: `python -m uvicorn main:app --reload`

## Architecture

- `main.py` contains the entire application: the FastAPI routes, settlement calculation, and the inline HTML/CSS/JavaScript page served by `GET /`.
- Expenses are stored only in the module-level `expenses` list. Restarting the process clears all data; there is no database or persistence layer.
- `POST /expenses` accepts form data, validates and stores an expense, then returns recalculated settlements. `GET /settlements` returns the same settlement data for the page's client-side refresh.
- `balances()` calculates each person's net balance in `Decimal` values, then matches debtors and creditors into payment instructions. Amounts are displayed as PHP strings by `pesos()`.

## Project conventions

- Keep the package version in `pyproject.toml` compliant with PEP 440. Use `MAJOR.MINOR.PATCH` releases such as `0.1.0`; use PEP 440 pre-release suffixes such as `0.2.0a1` or `0.2.0rc1` when needed.
- Keep currency calculations in `Decimal`; validate submitted amounts are finite and positive before storing or quantizing them.
- Do not use floating-point values for money.
- Never commit `.env` files or secrets.
- The browser page depends on the `expense-form`, `settlements`, and `settlement-status` element IDs plus the `/expenses` and `/settlements` endpoints. Preserve them when changing the UI.
- Render settlement data with DOM nodes and `textContent`, not `innerHTML`, because payer and participant names originate from form input.
- Tests import `main.app` directly. The autouse `clear_expenses` fixture resets the in-memory store for every test.
- Pytest uses `pythonpath = ["."]` from `pyproject.toml`, so tests live beside the application in `test_main.py`.

## Before finishing

- Run `pytest -q` and report the result.
