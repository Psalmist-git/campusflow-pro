# Baseline Check

## 1. Purpose

This document records the application's test results and checks related to
ticket creation, workflow safety, and notes.

## 2. Environment

- Python version: 3.12.3
- Branch: `kofi-Terdoo_branch`

## 3. Test Command

```bash
python3 -m unittest discover -s test -v
```

## 4. Automated Test Results

- Result: 105 tests passed.
- Status: PASS
- Evidence: The recorded test run completed successfully with `OK`.

## 5. Three Inputs Tested

### Input 1: Ticket creation

- Input: Create a ticket using valid title, category, urgency, and affected-user values.
- Expected result: A ticket is created with the correct priority.
- Actual result: Not yet verified.
- Outcome: Not verified.

### Input 2: Workflow safety

- Input: Attempt to move an unassigned open ticket to `in_progress`.
- Expected result: The transition is rejected without changing the ticket.
- Actual result: Not yet verified.
- Outcome: Not verified.

### Input 3: Note on a resolved ticket

- Input: Attempt to add a follow-up note to a resolved ticket.
- Expected result: The note is rejected and existing data is preserved.
- Actual result: Not yet verified.
- Outcome: Not verified.

## 6. Original Audit Findings

The original audit findings still need to be confirmed from the audit report.

- Finding 1: Awaiting confirmation.
- Finding 2: Awaiting confirmation.
- Finding 3: Awaiting confirmation.

## 7. Conclusion

The recorded automated test run passed all 105 tests. The three manual checks
and original audit findings still require verification.
