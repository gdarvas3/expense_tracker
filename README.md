# Shared Household Expense Splitter

A full-stack web application for roommates and travel groups to record shared expenses,
split them (equal, percentage, exact), record settlements, and get a simplified
debt-settlement plan.

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic, SQLite
- **Frontend:** React, TypeScript, Vite
- **AI rules:** [`AGENTS.md`](AGENTS.md) — shared instructions for all AI assistants

## Project status

_Last updated: 2026-11-12._

The main user workflow works end to end, through both the REST API and the web UI:

1. Log in as an existing user or create a new one.
2. Create a group (the creator becomes its admin) and, as admin, add or remove members.
3. Record an expense with an equal, percentage or exact split.
4. See every member's net balance and the simplified settlement plan.
5. Record a payment between two members; the balances and the plan update.

| Area | State |
|------|-------|
| Backend API: users, groups, members, expenses, settlements, balances, settlement plan | Done — AC-1 … AC-8 covered by acceptance tests; 143 tests pass |
| Frontend: login, group list, group page with expense, payment and member forms | Done — 22 tests pass; lint and typecheck are clean |
| Dual-AI implementation of debt simplification (AC-4) | Done — the Claude Code and the GitHub Copilot variants pass the same tests; see the [comparison](#dual-ai-implementation-ac-4) |
| AI decision log | 2 of 3 cases recorded |

Known limitations:

- No real authentication: the caller is identified by the `X-User-Id` header, without
  passwords or tokens (out of scope for the assignment).
- Expenses and settlements cannot be edited or deleted; recorded settlements are visible
  only through their effect on the balances.
- Local development setup only: a SQLite file database, no deployment or CI configuration.

The development history is documented by the git log (small, focused commits), the saved
[failing → passing test runs](#failing--passing-test-run) and the
[AI decision log](#ai-decision-log).

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

```bash
cd frontend
npm install
```

## Running the application

Start the backend and the frontend in two terminals:

```bash
cd backend
uvicorn app.main:app --reload
```

```bash
cd frontend
npm run dev
```

Open http://localhost:5173. The Vite dev server forwards `/api` requests to the backend.
The API runs on http://127.0.0.1:8000 (Swagger UI: http://127.0.0.1:8000/docs).
The SQLite database file (`expense_tracker.db`) is created on first start; set
`DATABASE_URL` to use a different location.

## Running the tests

```bash
cd backend
pytest -v
```

Tests use an isolated in-memory SQLite database, so they never touch the local database file.

```bash
cd frontend
npm test            # Vitest + React Testing Library (fetch is mocked)
npm run lint        # oxlint, including the no-lambdas rule from AGENTS.md
npm run typecheck
```

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

Development followed TDD: the tests were written first and run against stubs, so the
failing run shows assertion failures of the real tests, not import errors.

**Backend** — business logic stubbed with `NotImplementedError`:

| Run | Result | Commit |
|-----|--------|--------|
| [`2026-11-03-acceptance-red.txt`](docs/test-runs/2026-11-03-acceptance-red.txt) | 12 failed, 66 passed — every business-logic test fails; AC-7 and schema-level AC-5 already pass | `ef03804` |
| [`2026-11-03-acceptance-green.txt`](docs/test-runs/2026-11-03-acceptance-green.txt) | 131 passed — after implementing splitting, balances and debt simplification | `01df994` |

**Frontend** — expense and settlement forms stubbed as components that render nothing:

| Run | Result |
|-----|--------|
| [`2026-11-03-frontend-forms-red.txt`](docs/test-runs/2026-11-03-frontend-forms-red.txt) | 11 failed, 11 passed — every form and group-page test fails |
| [`2026-11-03-frontend-forms-green.txt`](docs/test-runs/2026-11-03-frontend-forms-green.txt) | 22 passed — after implementing the forms, member management and expense list |

## Dual-AI implementation (AC-4)

The debt-simplification algorithm was written twice, by two different AI tools, behind one
interface — `simplify_debts(balances: dict[int, int]) -> list[Transfer]`, see
[`AGENTS.md`](AGENTS.md) §5. `backend/tests/test_settlement.py` is parametrized over both
variants, so every test runs against each of them.

| | Claude Code | GitHub Copilot |
|---|---|---|
| Model | Opus 5.5 | Copilot Fusion |
| File | [`claude_code.py`](backend/app/services/settlement/claude_code.py) | [`copilot.py`](backend/app/services/settlement/copilot.py) |
| Commit | `01df994` | `5d11167` |
| Data structure | one dict of the open balances | two `heapq` heaps: debtors and creditors |
| Finding the largest debtor and creditor | linear scan with `max()` in every round | heap pop; an unsettled remainder is pushed back |
| Time complexity for n members | O(n²) | O(n log n) |
| Tie-break by ascending user ID | negated IDs in the `max()` key | natural ordering of `(-amount, user_id)` tuples |
| Structure | 4 small functions, 40 non-blank lines | 1 function, 41 non-blank lines |
| Unbalanced input | `ValueError` | `ValueError` |

### Correctness

Both variants pass the same 12 unit tests. The Copilot variant was added test-first, like
the rest of the project:

| Run | Result |
|-----|--------|
| [`2026-11-12-copilot-settlement-red.txt`](docs/test-runs/2026-11-12-copilot-settlement-red.txt) | 12 failed, 12 passed — every `[copilot]` case fails on the `NotImplementedError` stub |
| [`2026-11-12-copilot-settlement-green.txt`](docs/test-runs/2026-11-12-copilot-settlement-green.txt) | 143 passed — the whole backend suite, both variants included |

Beyond the unit tests, a differential check fed 5,000 random balanced inputs (2–30 members,
about a third of them with forced ties) to both variants: they returned identical transfer
lists every time.

### Performance

Best wall-clock time of one call on a random balanced input (Python 3.14):

| Members | Claude Code | GitHub Copilot |
|--------:|------------:|---------------:|
| 4       | 0.006 ms    | 0.003 ms       |
| 20      | 0.05 ms     | 0.02 ms        |
| 100     | 0.66 ms     | 0.17 ms        |
| 1,000   | 60 ms       | 1.1 ms         |
| 2,000   | 280 ms      | 2.4 ms         |

The heap-based variant is faster at every size and scales far better. For a household or a
travel group both finish in microseconds, so the difference cannot be observed in the
application.

### Code quality

Measured against the Clean Code rules in [`AGENTS.md`](AGENTS.md) §6.1:

- **Claude Code** follows the project rules more closely: small single-purpose functions,
  absolute imports like the rest of the code base, and a docstring that documents the
  `ValueError`. Its weak points are the quadratic algorithm, the negated-ID trick that
  needs a comment to be understood, and a helper (`settle_largest_pair`) that both mutates
  its argument and returns a value.
- **GitHub Copilot** chose the more efficient algorithm, and its tie-break needs no trick.
  Its weak points are structural: the whole algorithm is one 40-line function that mixes
  levels of abstraction, it uses a relative import, its one-line docstring does not mention
  the `ValueError`, and it contains leftovers (an unneeded `dict(balances)` copy, `-abs()`
  on a value that is already negative).

### Notes on the comparison

- The two tools did not work under identical conditions. The unit tests were committed
  together with the Claude Code variant (`01df994`), so they fix the exact order of the
  transfers; Copilot implemented against this finished test suite and was instructed not
  to read `claude_code.py`.
- The differential check and the timings were run once with an ad-hoc script that is not
  part of the repository.
- This comparison was drafted with Claude Code, one of the two tools compared.

The API uses the Claude Code variant (`backend/app/services/settlement/__init__.py`).
Because both variants return identical plans, switching is a one-line import change.

## AI decision log

### Case 1

- **Problem:**  The specification requires a full-stack web application, but the approved tech stack only defined the backend. A UI technology had to be chosen.
- **Tool:** Claude Code (Opus 5.5)
- **Prompt:** The application needs a UI what options do you suggest?
- **Suggestion:** Server-rendered Jinja2 templates + HTMX. Rationale: single language (Python), no build toolchain, UI testable with the same pytest/TestClient setup, less AI-generated code to review, lower delivery risk. A comparison table against a React SPA was provided.
- **User decision:** Rejected - React (TypeScript, Vite) was chosen because it provides a clear separation between the frontend and bakcend, and React with Typescript is also the industry standard frontend stack nowadays. 
- **Verification:** `npm run build` and `npm test` pass; a UI test checks that a non-member sees the 403 error message; all business rules remain covered by the backend acceptance tests (AC-1 … AC-8).

### Case 2

- **Problem:** The React frontend worked but had no real design: a plain default stylesheet in GitHub style. We needed a modern look for the main screen. The existing frontend tests had to keep passing. No new dependecies.
- **Tool:** Claude Code (Claude Opus 5.5). The designs were made with the `/design` command.
- **Prompt:** "/design lets implement the ui design. give me 5 modern suitable designs", "design 5th option in 3 other colors. Label it: 5A 5B 5C", "My choice is: 5C · Night shift"
- **Suggestion:** Claude made five directions for the group detail page, all with the same consistent sample data: (1) Ledger, Swiss minimal; (2) Soft, card-based fintech; (3) Midnight, dark dashboard; (4) Bold, neo-brutalist; (5) Receipt, with the expenses shown as a printed receipt and the settlement-plan transfers as "IOU" slips. It recommended Ledger as the easiest to port. Asked for three colour variants of Receipt, it made 5A Terracotta, 5B Blueprint and 5C Night shift.
- **User decision:** rejected the recommended option, decided to ask for 3 new variants of the receipt option. And then picked the 5C nightshift option. 
- **Verification:** `npm test` gave 22/22 passing both before and after the change, with no test modified. `npm run lint` and `npm run typecheck` were clean. A manual check in the browser (login, group list, group detail) at 1280 px and 375 px width showed no horizontal overflow and confirmed the fonts load.

### Case 3

- **Problem:**
- **Tool:**
- **Prompt:**
- **Suggestion:**
- **User decision:**
- **Verification:**
