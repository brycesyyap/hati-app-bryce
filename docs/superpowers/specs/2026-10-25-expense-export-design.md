# Expense CSV Export Design

## Intent

Allow roommates to download the current in-memory expenses as a CSV file from `POST /expenses/export`.

## Goals

- Return a downloadable CSV containing each expense's description, amount, payer, and shared participants.
- Preserve the existing expense creation, settlement, and page behavior.

## Non-goals

- Persisting expenses, adding an export button, or changing existing routes.
- Streaming large exports or adding a JSON export.

## Constraints

- The application has a module-level in-memory `expenses` list.
- Currency values remain `Decimal` values and must be represented without floating-point conversion.

## Approaches

- Standard in-memory CSV response: generate the small export with Python's standard `csv` module, then return it as an attachment. Chosen because all data is already held in memory and it is the simplest reliable implementation.
- Streaming CSV response: generate rows incrementally. Rejected because it adds complexity without memory savings for the existing in-memory store.

## Design

The route will mirror the existing expense route's simple FastAPI function structure. It will serialize the current `expenses` records to CSV using an in-memory text buffer, set `text/csv` and a `Content-Disposition` attachment filename, and return the result without modifying any data.
