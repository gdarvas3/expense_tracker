# AGENTS.md — Rules and context for AI assistants

This file is the single source of truth for every AI coding assistant working in this
repository (Claude Code, GitHub Copilot, Cursor, Codex, …). There are no tool-specific
instruction files. If an instruction here conflicts with a tool's default behaviour, this file wins.

## 1. Project

**Shared Household Expense Splitter** — a full-stack web application (FastAPI backend +
React frontend) that lets roommates / travel groups record shared expenses, split them with
several rules (equal, percentage, exact), record settlements, and compute a simplified
debt-settlement plan.

University homework (BME, *AI Assisted Software Development*). Besides working code, the
grading values **traceable AI usage**: tests for every acceptance criterion, a documented
failing → passing test run, and documented AI decisions.

## 2. Tech stack

### Backend (`backend/`)

| Concern    | Choice                                   |
|------------|------------------------------------------|
| Language   | Python 3.12+                             |
| Web        | FastAPI (JSON API under `/api`)          |
| ORM / DB   | SQLAlchemy 2.x (typed `Mapped[]` style), SQLite (local file; in-memory for tests) |
| Validation | Pydantic v2                              |
| Tests      | pytest + FastAPI `TestClient` (httpx)    |

### Frontend (`frontend/`)

| Concern    | Choice                                              |
|------------|-----------------------------------------------------|
| Language   | TypeScript (`strict: true`)                         |
| Framework  | React 18 + Vite                                     |
| Routing    | React Router                                        |
| HTTP       | native `fetch` wrapped in one typed API client (`src/api/`) |
| Styling    | plain CSS modules (no UI framework)                 |
| Tests      | Vitest + React Testing Library                      |

Do not add new dependencies (Python or npm) without asking the user first.

## 3. Architecture

```
backend/
  app/
    main.py          # FastAPI app factory, router registration, exception handlers
    database.py      # engine, SessionLocal, Base, get_db dependency
    exceptions.py    # domain exceptions, each carrying its HTTP status code
    dependencies.py  # get_current_user (X-User-Id), group-membership / admin guards
    models/          # SQLAlchemy ORM models — no business logic
    schemas/         # Pydantic request/response models — no DB access
    services/        # business logic (splitting, balances, settlement) — no FastAPI imports
    routers/         # thin HTTP layer: parse → call service → map errors to HTTP status
  tests/
    conftest.py         # in-memory DB, TestClient, user/group fixtures
    test_acceptance.py  # one test per AC (AC-1 … AC-8)
    test_*.py           # unit tests per service
  requirements.txt   # pinned dependencies
  pyproject.toml     # pytest configuration
frontend/
  src/
    api/             # typed API client: the ONLY place that calls fetch
    types/           # TypeScript types mirroring the backend schemas
    pages/           # route-level components (GroupList, GroupDetail, …)
    components/      # reusable presentational components
    hooks/           # data-fetching / state hooks (useGroup, useBalances, …)
    utils/money.ts   # cents ↔ display formatting
  package.json
docs/
  test-runs/         # saved test outputs (failing → passing evidence)
```

Backend layer rules:
- Routers never contain business logic; services never import `fastapi`.
- Services raise domain exceptions (`ValidationError`, `ConflictError`, `ForbiddenError`,
  `NotFoundError`); `main.py` maps them to HTTP status codes in one place.
- The debt-simplification algorithm is a **pure function** with no DB access (see §5).

Frontend layer rules:
- **The backend is the single source of truth for business rules.** The frontend never
  computes shares, balances or the settlement plan; it only displays what the API returns.
  Client-side validation (e.g. "percentages must sum to 100") is a UX convenience only —
  the backend still enforces it (AC-5).
- Components never call `fetch` directly — only through `src/api/`.
- Pages compose hooks + components; presentational components receive data via props.
- Money is kept as integer cents in the frontend too; format only at display time
  (`utils/money.ts`), parse user input to cents without floating-point arithmetic.
- The current user is chosen on a "Log in as…" screen (user dropdown), kept in React context
  (and `localStorage`), and sent by the API client as the `X-User-Id` header on every request.
- API errors (400/401/403/404/409) are shown to the user with a readable message.

## 4. Domain rules (from the approved specification — do not change)

### Money
- **All amounts are stored and computed as integer cents (`int`). Never use `float` for money.**
- The API accepts/returns amounts as decimal strings or numbers with at most 2 decimals
  (e.g. `"100.00"`); conversion to cents happens in the schema layer via `Decimal`, never `float`.
- Percentages are stored as integer **basis points** (100% = 10000, 33.33% = 3333).

### Splitting
- Split types: `equal`, `percentage`, `exact`.
- Every share is in cents; **the sum of shares must equal the expense amount exactly.**
- **Rounding remainder:** leftover cents (from integer division) are assigned one cent each
  to the first participants **sorted ascending by user ID**.
  Example (AC-3): 100.00 / 3 → 33.34, 33.33, 33.33.
  *Interpretation:* the spec says "alphabetically by user ID"; user IDs are integers, so we
  sort them numerically ascending (alphabetic string order would put 10 before 9).

### Balances
- Net balance of a member = (amounts they paid) − (their shares) + (settlements they paid)
  − (settlements they received). Positive = others owe them.
- The sum of all net balances in a group is always exactly 0.

### Debt simplification (AC-4)
- Input: net balances. Output: list of transfers `(from_user, to_user, amount_cents)`.
- Greedy: repeatedly match the **largest debtor** with the **largest creditor**, transfer
  `min(|debt|, credit)`, repeat until all balances are 0.
- Ties are broken by ascending user ID (determinism is required for tests).

### Membership & authorization
- The caller is identified by the **`X-User-Id`** request header (no passwords / tokens —
  out of scope for this assignment). Missing or unknown user → **401**.
- Group creator becomes **admin**. Only admins add/remove members and change settings.
- Members and admins can view data and log expenses / settlements.
- Non-member accessing any group resource → **403** (AC-7).
- A member can be removed only if their net balance is exactly 0 → otherwise **409** (AC-6).

### HTTP status codes
| Situation                                              | Status |
|--------------------------------------------------------|--------|
| Invalid input (amount ≤ 0, % ≠ 100, exact sum ≠ total, malformed body) | **400** |
| Missing/unknown `X-User-Id`                            | 401    |
| Not a member / not an admin                            | 403    |
| Resource not found                                     | 404    |
| Removing a member with non-zero balance                | 409    |

FastAPI returns 422 for request-validation errors by default; `main.py` registers a handler
that converts `RequestValidationError` to **400** so AC-5 holds for every invalid input.

## 5. Dual-AI implementation (AC-4)

The debt-simplification algorithm is implemented **twice, by two different AI tools**, behind
one interface so both run against the same tests:

```python
# backend/app/services/settlement/<variant>.py
def simplify_debts(balances: dict[int, int]) -> list[Transfer]: ...
```

- `backend/app/services/settlement/claude_code.py` — Claude Code implementation
- `backend/app/services/settlement/<other_tool>.py` — second tool's implementation
- `backend/tests/test_settlement.py` is parametrized over both implementations.
- An AI assistant must **only edit its own variant file**, never the other tool's.

## 6. Working rules for AI assistants

1. **TDD:** write or extend a failing test first, run it, show it fails, then implement.
2. **Never weaken, skip, or delete a test to make it pass.** If a test seems wrong, stop and
   ask the user.
3. Every acceptance criterion AC-1 … AC-8 has at least one backend test in
   `backend/tests/test_acceptance.py` whose name starts with `test_ac<N>_`. Frontend tests
   cover UI behaviour (forms, error display, current-user header), not business rules.
4. Keep changes small and focused on the requested task; do not refactor unrelated code.
5. Follow the **Clean Code** rules in §6.1.
6. Before claiming a task is done, run the relevant tests (`pytest -v` in `backend/`,
   `npm test` in `frontend/`) and quote the result.
7. Do not commit, push, or rewrite git history unless the user asks.
8. When you make a non-trivial design decision (or the user overrides your suggestion),
   say so explicitly in your answer, so the user can record it in the README's
   *AI decision log* (Problem, Tool, Prompt, Suggestion, User decision, Verification).

### 6.1 Clean Code (mandatory)

- **Meaningful names:** intention-revealing names for variables, functions and classes
  (`amount_cents`, `largest_debtor`, not `a`, `tmp`, `x`). No abbreviations except well-known
  ones (`id`, `db`).
- **Small functions that do one thing**, at one level of abstraction. If a function needs a
  comment to explain *what* its blocks do, extract those blocks into named functions.
- **No lambda expressions.** Use a named function (`def`) instead — including sort keys
  and callbacks. For simple attribute/item access use `operator.attrgetter` /
  `operator.itemgetter`.
  ```python
  # wrong
  members.sort(key=lambda member: member.user_id)
  # right
  members.sort(key=attrgetter("user_id"))
  ```
- **No magic numbers:** name constants (`FULL_PERCENT_BASIS_POINTS = 10_000`).
- **Few parameters:** more than 3 parameters → group them into a dataclass / Pydantic model.
- **No duplication (DRY):** shared logic lives in one service function.
- **Guard clauses over deep nesting;** keep nesting depth ≤ 2 where possible.
- **Comments and docstrings** — see §6.3.
- **Explicit error handling:** raise specific domain exceptions; never use bare `except:` or
  silently swallow errors.
- **Type hints on all functions;** follow PEP 8 (line length 100).

### 6.2 Clean Code in the frontend (TypeScript / React)

The rules of §6.1 apply to TypeScript too. Arrow functions are TypeScript's lambdas, so:

- **No inline arrow functions.** Components, hooks, event handlers, `map`/`filter`
  callbacks and sort comparators are **named functions** (`function` declarations, or
  named handler functions declared inside the component).
  ```tsx
  // wrong
  <button onClick={() => removeMember(member.id)}>Remove</button>
  {expenses.map((expense) => <ExpenseRow key={expense.id} expense={expense} />)}

  // right
  function handleRemoveClick(): void { removeMember(member.id); }
  <button onClick={handleRemoveClick}>Remove</button>

  function renderExpenseRow(expense: Expense): JSX.Element {
    return <ExpenseRow key={expense.id} expense={expense} />;
  }
  {expenses.map(renderExpenseRow)}
  ```
  Per-item handlers go into the item component (`<MemberRow>` owns its own
  `handleRemoveClick`) instead of being created inline in the parent's `map`.
- Exception: callbacks whose signature is fixed by a library and that cannot be named
  sensibly (e.g. a `useEffect` cleanup) may be named local functions — still not anonymous.
- `strict` TypeScript, **no `any`**; explicit return types on exported functions.
- One component per file; file name = component name (`ExpenseForm.tsx`).
- No magic strings for API paths or split types — use shared constants / union types.

### 6.3 Comments and docstrings

All comments, docstrings, identifiers and commit messages are in **English**. Be **concise
and to the point**: if the code can say it, the comment shouldn't.

- **Explain *why*, not *what*.** Comment intent, business rules, non-obvious decisions and
  edge cases — never restate the code.
  ```python
  # wrong: adds the remainder to the first shares
  # right: spec — leftover cents go to the lowest user IDs (AC-3)
  ```
- **Reference the spec** where a rule comes from it: `# AC-6: only zero-balance members can leave`.
- **Docstrings (Python, PEP 257, Google style)** on public modules, classes and functions:
  a one-line imperative summary ending with a period; add `Args:` / `Returns:` / `Raises:`
  only when they add information beyond the type hints.
  ```python
  def split_equally(amount_cents: int, user_ids: list[int]) -> dict[int, int]:
      """Split an amount into equal shares, giving leftover cents to the lowest user IDs.

      Raises:
          ValidationError: If the amount is not positive or there are no participants.
      """
  ```
- **TSDoc (`/** … */`)** on exported functions, hooks and non-obvious component props;
  same one-line-summary rule. Not needed for self-explanatory components.
- No redundant comments (`# increment i`), no commented-out code, no change history in
  comments (git records that), no noise like `# --- helpers ---` banners.
- `TODO(<name>): <action>` only for tracked follow-ups; do not leave vague TODOs.
- Keep comments up to date: when code changes, fix or delete the comment in the same edit.

## 7. Commands

```bash
# ---- backend (from backend/) ----
python -m venv .venv
# Windows: .venv\Scripts\activate    | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload          # API on http://127.0.0.1:8000, Swagger at /docs

pytest -v                              # all backend tests
pytest tests/test_acceptance.py -v     # acceptance tests only
pytest -k ac4 -v                       # a single AC

# ---- frontend (from frontend/) ----
npm install
npm run dev                            # http://localhost:5173, proxies /api to :8000
npm test                               # Vitest
npm run lint                           # ESLint (+ typecheck)

# ---- save a test run as evidence (failing → passing) ----
pytest -v 2>&1 | tee ../docs/test-runs/<yyyy-mm-dd>-<name>.txt              # bash
pytest -v 2>&1 | Tee-Object ..\docs\test-runs\<yyyy-mm-dd>-<name>.txt       # PowerShell
```

The Vite dev server proxies `/api` to the backend, so no CORS setup is needed in development.
On Windows consoles set `PYTHONIOENCODING=utf-8` if output contains non-ASCII characters.
