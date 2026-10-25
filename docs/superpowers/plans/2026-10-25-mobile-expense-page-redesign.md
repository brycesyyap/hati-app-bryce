# Mobile Expense Page Redesign Implementation Plan

**Goal:** Redesign Hati's main page into a polished, trustworthy mobile-first expense splitter without changing expense entry or settlement behavior.

**Architecture:** Keep the current single inline FastAPI HTML template and existing browser fetch calls. Replace its semantic structure and CSS with a responsive calm-blue design; use the existing `/expenses` and `/settlements` responses unchanged.

**Tech Stack:** Python 3.12, FastAPI, inline HTML/CSS/JavaScript, pytest.

**Spec:** `docs/superpowers/specs/2026-10-25-mobile-expense-page-design.md`
