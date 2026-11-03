# Shared Household Expense Splitter

A full-stack web application for roommates and travel groups to record shared expenses,
split them (equal, percentage, exact), record settlements, and get a simplified
debt-settlement plan.

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic, SQLite
- **Frontend:** React, TypeScript, Vite
- **AI rules:** [`AGENTS.md`](AGENTS.md) — shared instructions for all AI assistants

## Setup

Requirements: Python 3.12+, Node.js 20+.

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend

_TODO_

## Running the application

```bash
cd backend
uvicorn app.main:app --reload
```

The API runs on http://127.0.0.1:8000 (Swagger UI: http://127.0.0.1:8000/docs).
The SQLite database file (`expense_tracker.db`) is created on first start; set
`DATABASE_URL` to use a different location.

## Running the tests

```bash
cd backend
pytest -v
```

Tests use an isolated in-memory SQLite database, so they never touch the local database file.

## Acceptance criteria coverage

End-to-end API tests live in `backend/tests/test_acceptance.py` (run one AC with
`pytest -k ac4 -v`); the business rules also have unit tests.

| AC   | Description                         | Acceptance test(s)                                  | Unit tests |
|------|-------------------------------------|-----------------------------------------------------|------------|
| AC-1 | Equal split                         | `test_ac1_equal_split_gives_each_member_a_quarter`  | `test_split.py`, `test_balance.py` |
| AC-2 | Percentage split                    | `test_ac2_percentage_split_follows_the_given_percentages` | `test_split.py` |
| AC-3 | Penny rounding                      | `test_ac3_leftover_cent_goes_to_the_lowest_user_id`, `test_ac3_leftover_cents_follow_numeric_user_id_order` | `test_split.py` |
| AC-4 | Transitive debt simplification      | `test_ac4_transitive_debt_becomes_a_single_payment` | `test_settlement.py` |
| AC-5 | Invalid split rejected (400)        | `test_ac5_invalid_split_is_rejected_with_400` (6 cases) | `test_split.py`, `test_schemas.py` |
| AC-6 | Removal with balance rejected (409) | `test_ac6_member_with_balance_cannot_be_removed`, `test_ac6_member_with_zero_balance_can_be_removed` | — |
| AC-7 | Non-member access rejected (403)    | `test_ac7_non_member_is_rejected_with_403` (8 endpoints) | `test_dependencies.py` |
| AC-8 | Settlement zeroes balances          | `test_ac8_settlement_brings_balances_to_zero`       | `test_balance.py` |

## Failing → passing test run

Development followed TDD: the acceptance tests were written first, against an API whose
business logic was stubbed with `NotImplementedError`.

| Run | Result | Commit |
|-----|--------|--------|
| [`2026-11-03-acceptance-red.txt`](docs/test-runs/2026-11-03-acceptance-red.txt) | 12 failed, 66 passed — every business-logic test fails; AC-7 and schema-level AC-5 already pass | `ef03804` |
| [`2026-11-03-acceptance-green.txt`](docs/test-runs/2026-11-03-acceptance-green.txt) | 131 passed — after implementing splitting, balances and debt simplification | _this commit_ |

## Dual-AI implementation (AC-4)

_TODO: compare the two debt-simplification implementations._

## AI decision log

### Case 1

- **Problem:**  The specification requires a full-stack web application, but the approved tech stack only defined the backend. A UI technology had to be chosen.
- **Tool:** Claude Code (Opus 5.5)
- **Prompt:** The application needs a UI what options do you suggest?
- **Suggestion:** Server-rendered Jinja2 templates + HTMX. Rationale: single language (Python), no build toolchain, UI testable with the same pytest/TestClient setup, less AI-generated code to review, lower delivery risk. A comparison table against a React SPA was provided.
- **User decision:** Rejected - React (TypeScript, Vite) was chosen because it provides a clear separation between the frontend and bakcend, and React with Typescript is also the industry standard frontend stack nowadays. 
- **Verification:** `npm run build` and `npm test` pass; a UI test checks that a non-member sees the 403 error message; all business rules remain covered by the backend acceptance tests (AC-1 … AC-8).

### Case 2

- **Problem:**
- **Tool:**
- **Prompt:**
- **Suggestion:**
- **User decision:**
- **Verification:**

### Case 3

- **Problem:**
- **Tool:**
- **Prompt:**
- **Suggestion:**
- **User decision:**
- **Verification:**
