# AI Learning Log — Jedidiah

**Project:** CampusFlow  
**Role:** Engineer B — Ticket Workflow and Reporting  
**Period:** 10–11 October 2026

## Entry 1: Understanding the Ticket Workflow

### Objective
Understand how ticket assignment, status transitions, and work queue prioritization should operate.

### How I used AI
I used AI to help review the workflow requirements and understand how the different ticket operations should work together.

I sought guidance on:
- Assigning tickets to staff members.
- Preventing unassigned tickets from entering the in-progress state.
- Resolving tickets only after they reach the in-progress state.
- Reopening resolved tickets.
- Ordering the work queue by priority and ticket ID.

### What I learned
I learned that a ticket workflow needs explicit rules governing valid state transitions. Without these rules, tickets could move into invalid states or be processed in the wrong order.

I also learned why resolved tickets should be excluded from the active work queue.

### Implementation and verification
I reviewed `campusflow/workflow.py` and the associated tests to check the workflow rules.

The automated tests passed for ticket assignment, status transitions, and work queue ordering.

---

## Entry 2: Integrating Ticket Assignment and Status Management

### Objective
Connect the workflow functions to the CampusFlow command-line application.

### How I used AI
I used AI to help review `main.py` and understand how the command-line interface connects to ticket creation, assignment, status updates, reporting, and storage.

### What I learned
I learned that implementing individual functions is not enough. The application must connect those functions correctly so that users can perform complete tasks through the interface.

I also learned the importance of checking imports and function calls when integrating code from different modules.

### Implementation and verification
I reviewed the CLI functions for assigning tickets, changing ticket status, displaying the work queue, and generating reports.

I launched the application using:

    python3 main.py

The application loaded the saved ticket data, displayed the menu, accepted the exit option, and terminated normally.

---

## Entry 3: Testing JSON Persistence and the Ticket Lifecycle

### Objective
Verify that ticket data can be created, updated, saved, and loaded without losing important information.

### How I used AI
I used AI to help design a temporary integration test that combined ticket creation, assignment, status transitions, JSON persistence, and work queue filtering.

### What I learned
I learned that unit tests and integration tests serve different purposes.

Unit tests check individual functions, while integration tests help establish whether several components work together correctly.

I also learned the importance of using temporary files during testing to avoid accidentally modifying existing project data.

### Implementation and verification
I ran an integration test using a temporary JSON file.

The test:
1. Created a ticket.
2. Assigned it to a staff member.
3. Changed its status to `in_progress`.
4. Resolved the ticket.
5. Saved and reloaded the ticket.
6. Verified that the assignment and resolved status were preserved.
7. Confirmed that the resolved ticket was excluded from the work queue.

The integration test passed, and the existing `data/tickets.json` file was not modified.

---

## Entry 4: Resolving Git Merge Conflicts and Verifying the Merge

### Objective
Integrate changes from `origin/main` into `jedidiah_branch` while preserving the functionality of both branches.

### How I used AI
I used AI for step-by-step guidance while resolving Git merge conflicts.

The conflicts affected:
- `.gitignore`
- `campusflow/storage.py`
- `campusflow/tickets.py`
- `test/test_storage.py`
- `test/test_tickets.py`

I also used AI to help reason about compatibility between the original ticket creation interface and the newer category, urgency, and automatic-priority features.

### What I learned
I learned that resolving merge conflicts requires more than deleting conflict markers. The final code must preserve the required functionality from both branches.

I also learned the importance of maintaining a backup branch, reviewing Git status, running tests, and checking Python compilation before creating a merge commit.

### Implementation and verification
I resolved the conflicts and staged the corrected files.

I ran:

    python3 -m unittest discover -s test -v

All 56 tests passed.

I also ran Python compilation checks and `git diff --check`. Both completed successfully.

I created the merge commit:

    0a1da91 Merge main into jedidiah_branch

The branch was subsequently synchronized with GitHub, and `git status` confirmed that the working tree was clean.

---

## Reflection: What I Learned from Using AI

Using AI helped me understand unfamiliar code, reason about workflow rules, investigate integration requirements, and follow a structured process for resolving merge conflicts.

One important lesson was that AI assistance does not replace verification. I still needed to run tests, inspect command output, check Git status, and confirm that the application behaved as expected.

I also learned to preserve existing data during testing and to use a temporary environment when checking persistence.

Going forward, I will aim to understand the proposed changes before applying them, test each important feature, and document the results rather than relying solely on AI-generated explanations.

## Evidence of Verification

- Automated test suite: 56 tests passed.
- Python compilation checks: passed.
- Git whitespace/conflict-marker check: passed.
- CLI startup and exit test: passed.
- Temporary ticket lifecycle and persistence integration test: passed.
- Merge commit: `0a1da91`.
- Final Git working tree: clean.

## Final Reflection

AI was a development assistant, not a substitute for my own understanding or responsibility for the project.

The most useful part of the process was learning to combine code review, automated testing, integration testing, and version control checks to establish whether the implementation worked.

---

## Entry 5 (TO COMPLETE): An AI suggestion I corrected, improved or rejected

> Jedidiah: the entries above describe tasks. The guide also requires one entry where
> you checked an AI suggestion yourself and changed or rejected it. Fill this in
> truthfully using the template in `ai-learning-log.md` (your actual prompt, your own
> experiment, what you observed, your decision). For example, if you reviewed the
> case-sensitive ticket-ID lookup or the duplicated `assign_ticket` function and
> changed it, say what you tested and why. Delete this note once done.
