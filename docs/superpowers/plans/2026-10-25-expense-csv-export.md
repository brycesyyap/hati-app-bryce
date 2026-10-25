# Expense CSV Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `POST /expenses/export` to download the current expenses as a CSV attachment.

**Architecture:** Keep the route in `main.py`, alongside the existing expense routes. Serialize the module-level `expenses` list with Python's standard `csv` module into an in-memory text buffer, then return it as a CSV attachment without changing expense data.

**Tech Stack:** Python 3.12, FastAPI, pytest, standard-library `csv` and `io`.

**Spec:** `docs/superpowers/specs/2026-10-25-expense-export-design.md`

## Global Constraints

- Expenses remain in the module-level in-memory `expenses` list.
- Currency values remain `Decimal` values and must not be converted through floating point.
- The export is read-only and must not change existing expense, settlement, or page behavior.
- Do not add a UI export button, persistence, streaming, or JSON export.

## Review Focus

- An empty expense list produces a valid CSV attachment with a header row; covered by Task 1.
- Descriptions, payers, and participant names containing commas or quotes are escaped as valid CSV; covered by Task 1.
- A decimal amount is represented exactly with two decimal places, without float artifacts; covered by Task 1.
- The shares list is represented in one deterministic CSV field; covered by Task 1.
- Repeated exports leave the in-memory expense list unchanged; covered by Task 1.

---

### Task 1: CSV Export Endpoint

**Files:**
- Modify: `main.py:1-8,138-140`
- Modify: `test_main.py:57-65`

**Interfaces:**
- Consumes: `expenses: list[dict[str, object]]`
- Produces: `export_expenses() -> Response` at `POST /expenses/export`, returning a `text/csv` attachment named `expenses.csv`.

- [ ] **Step 1: Write the failing export tests**
- [ ] **Step 2: Run the new tests to verify they fail**
- [ ] **Step 3: Implement `export_expenses() -> Response` in `main.py`**
- [ ] **Step 4: Run export tests to verify they pass**
- [ ] **Step 5: Run the full test suite**
- [ ] **Step 6: Commit**
