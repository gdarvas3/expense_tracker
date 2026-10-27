# Shared Household Expense Splitter

A full-stack web application for roommates and travel groups to record shared expenses,
split them (equal, percentage, exact), record settlements, and get a simplified
debt-settlement plan.

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic, SQLite
- **Frontend:** React, TypeScript, Vite
- **AI rules:** [`AGENTS.md`](AGENTS.md) — shared instructions for all AI assistants

## Setup

_TODO: backend and frontend setup steps._

## Running the application

_TODO: how to start the backend and the frontend._

## Running the tests

_TODO: backend (pytest) and frontend (Vitest) test commands._

## Acceptance criteria coverage

| AC   | Description                  | Test |
|------|------------------------------|------|
| AC-1 | Equal split                  | _TODO_ |
| AC-2 | Percentage split             | _TODO_ |
| AC-3 | Penny rounding               | _TODO_ |
| AC-4 | Transitive debt simplification | _TODO_ |
| AC-5 | Invalid split rejected (400) | _TODO_ |
| AC-6 | Removal with balance rejected (409) | _TODO_ |
| AC-7 | Non-member access rejected (403) | _TODO_ |
| AC-8 | Settlement zeroes balances   | _TODO_ |

## Failing → passing test run

_TODO: link the saved runs in `docs/test-runs/`._

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
