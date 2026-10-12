# AI Learning Log — Jedidiah (Engineer B)

**Project:** CampusFlow
**Role:** Engineer B — assignment, lifecycle, work queue, reports
**Period:** 10–11 October 2026

> Lines marked **[ADD: …]** are details the guide requires that the earlier version of
> this log did not state. Fill each one in with what you really did, or delete the
> line if it does not apply. Do not invent results.

## Fellow: Jedidiah

### Interaction #1 — Ticket workflow rules (assignment, status transitions, queue)
Problem: I needed to understand how assignment, status transitions and work-queue ordering should operate together.
My initial understanding: **[ADD: what you believed before asking, in your own words]**
Prompt to AI: **[ADD: your actual prompt]** (topics covered: assigning tickets, blocking unassigned tickets from `in_progress`, resolving only from `in_progress`, reopening resolved tickets, ordering the queue by priority then ticket ID)
Useful AI guidance: A workflow needs explicit rules for valid state transitions, otherwise tickets can reach invalid states or be handled in the wrong order. Resolved tickets belong outside the active work queue.
My independent experiment/test: I read `campusflow/workflow.py` and its tests to check each rule. **[ADD: any prediction you made before running a test, e.g. "I expected resolved -> in_progress to fail"]**
Verification source or result: The automated tests for assignment, status transitions and queue ordering passed.
Decision: **[ADD: accepted / improved / rejected, and why]**
Related file/commit: `campusflow/workflow.py`, `test/test_workflow.py`
What I can now explain without AI: Explicit transition rules stop tickets entering invalid states, and resolved tickets are excluded from the active queue because there is no work left on them.

---

### Interaction #2 — Connecting workflow functions to the CLI
Problem: Individual functions are not enough; the menu must call them correctly so a user can finish a whole task.
My initial understanding: **[ADD: how you thought the CLI connected to the modules]**
Prompt to AI: **[ADD: your actual prompt]** (I asked for help reviewing `main.py` and how it connects creation, assignment, status updates, reports and storage.)
Useful AI guidance: Check imports and function calls carefully when integrating code written by different people.
My independent experiment/test: I reviewed the CLI functions for assigning, changing status, viewing the queue and reports, then ran `python3 main.py`. It loaded the saved ticket data, showed the menu, accepted the exit option and closed normally.
Verification source or result: The program started and exited correctly with the saved data.
Decision: **[ADD: what you kept or changed in `main.py` as a result]**
Related file/commit: `main.py`
What I can now explain without AI: The CLI only collects input and displays results; the modules do the real work, so each import and call must match the function contracts.

---

### Interaction #3 — Integration test of the ticket lifecycle with JSON
Problem: I needed to check that a ticket can be created, updated, saved and reloaded without losing information.
My initial understanding: **[ADD: what you expected to happen]**
Prompt to AI: **[ADD: your actual prompt]** (I asked for help designing a temporary integration test combining creation, assignment, status changes, JSON persistence and queue filtering.)
Useful AI guidance: Unit tests check single functions, integration tests check that components work together. Use temporary files so real project data is not changed.
My independent experiment/test: I ran an integration test with a temporary JSON file that (1) created a ticket, (2) assigned it, (3) set `in_progress`, (4) resolved it, (5) saved and reloaded it, (6) checked assignment and resolved status were kept, and (7) confirmed the resolved ticket was missing from the work queue.
Verification source or result: The test passed, and the existing `data/tickets.json` was not modified.
Decision: Accepted the temporary-file approach so the real data stayed untouched.
Related file/commit: temporary integration test (not committed), `campusflow/storage.py`, `campusflow/workflow.py`
What I can now explain without AI: The difference between unit and integration tests, and why tests should write to temporary files.

---

### Interaction #4 — Resolving a merge conflict between `jedidiah_branch` and `origin/main`
Problem: My branch and `origin/main` conflicted and I needed to combine both without losing features.
My initial understanding: **[ADD: what you thought a merge conflict required]**
Prompt to AI: **[ADD: your actual prompt]** (I asked for step-by-step guidance while resolving the conflicts and for help with compatibility between the original ticket-creation interface and the newer category/urgency/automatic-priority interface.)
Useful AI guidance: Resolve conflicts by combining the needed behaviour from both sides, keep a backup branch, check `git status`, run the tests and check Python compilation before the merge commit.
My independent experiment/test: The conflicts were in `.gitignore`, `campusflow/storage.py`, `campusflow/tickets.py`, `test/test_storage.py` and `test/test_tickets.py`. I resolved and staged them, ran `python3 -m unittest discover -s test -v` (56 tests passed at that point), ran Python compilation checks and `git diff --check`, then created the merge commit.
Verification source or result: All 56 tests passed, compilation and whitespace/conflict-marker checks passed, `git status` was clean after syncing with GitHub.
Decision: **[ADD: any AI suggestion you checked and changed or rejected here; if none, say so]**
Related file/commit: merge commit `0a1da91`
What I can now explain without AI: Deleting conflict markers is not enough; the final code must keep what both branches need, and the tests prove it.

---

### Interaction #5 — An AI suggestion I corrected, improved or rejected (REQUIRED)
Problem: **[ADD]**
My initial understanding: **[ADD]**
Prompt to AI: **[ADD: your actual prompt]**
Useful AI guidance: **[ADD: a short summary of what the AI said]**
My independent experiment/test: **[ADD: what you ran yourself and what you observed]**
Verification source or result: **[ADD: test result or documentation you checked]**
Decision: **[ADD: how you corrected, improved or rejected the suggestion, and why]**
Related file/commit: **[ADD: path, test name, SHA or PR link]**
What I can now explain without AI: **[ADD: in your own words]**

Ideas from your own code, if one really happened to you: lowercase ticket IDs failing in `assign_ticket` but not in `find_ticket`; having two copies of `assign_ticket`; or ticket IDs sorted as text (`T10` before `T9`).

---

## Reflection: What I learned from using AI

AI helped me understand unfamiliar code, reason about workflow rules, plan integration checks and follow a structured process for merge conflicts. It did not replace verification: I still had to run tests, read command output, check Git status and confirm the application behaved as expected.

Going forward I will understand a proposed change before applying it, test each important feature, and record results instead of relying on AI explanations.

## Evidence of verification (at merge commit `0a1da91`)

- Automated tests: 56 passed
- Python compilation checks: passed
- `git diff --check`: passed
- CLI startup and exit: passed
- Temporary lifecycle and persistence integration test: passed
- Final Git working tree: clean
