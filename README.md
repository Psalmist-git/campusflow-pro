# CampusFlow

CampusFlow is a Python command-line helpdesk for Learn2Earn campus staff. Technical
support requests (Wi-Fi outages, faulty laptops, broken dev environments) are
recorded as tickets, prioritised automatically, assigned to staff, tracked through
a simple workflow and saved to a JSON file.

## Team

| Fellow | Role | Main contribution |
|---|---|---|
| Deborah John | Engineer A | Ticket creation, input validation, priority engine, matching tests |
| Jedidiah | Engineer B | Assignment, status workflow, work queue, reports, matching tests |

Both fellows: agreed function contracts (`docs/design-decisions.md`), JSON persistence
integration, cross-reviewed each other's pull requests, AI learning logs.

> Edit the table above if the names/roles differ.

## Requirements

- Python 3.10 or newer (standard library only, no packages to install)

## Run the app

```bash
python3 main.py
```

Menu options:

1. Create a ticket
2. Assign a ticket
3. Update ticket status
4. View prioritized work queue
5. View all tickets
6. View one ticket
7. Generate report
8. Exit

Ticket IDs are not case-sensitive (`t001` works as well as `T001`).

## Run the tests

```bash
python3 -m unittest discover -s test -v
```

The suite (60 tests) covers: priority rules and their boundaries, input validation,
unique ID generation, assignment, status transitions (including rejected ones and
reopen), work-queue ordering and ties, reports (including zero tickets), JSON
save/load round trips, malformed JSON, and creating a ticket after reload without
duplicating an ID. Storage tests use temporary files, so your real data is never touched.

## Ticket rules

Each ticket stores `id`, `title`, `category`, `urgency`, `affected_users`,
`priority`, `status`, `assigned_to`.

- **Category:** Network, Hardware, Software, Other
- **Urgency:** low, medium, high
- **Title:** must not be blank. **Affected users:** a positive whole number.

Priority is calculated by ordinary Python code; the first matching rule wins:

1. high urgency AND 10+ affected users -> **critical**
2. high urgency OR 10+ affected users -> **high**
3. medium urgency OR 3+ affected users -> **medium**
4. otherwise -> **low**

Status workflow: `open -> in_progress -> resolved`.

- A ticket must be assigned before it can become `in_progress`.
- A resolved ticket cannot be changed (including reassignment) until it is
  explicitly reopened to `open`.

The work queue shows unresolved tickets ordered critical -> high -> medium -> low,
with ties broken by the lower numeric ticket ID.

## Where data is saved

Tickets are saved to `data/tickets.json` after every change and loaded on startup.
To start fresh, delete that file. A missing file starts an empty list. A malformed
file produces a clear error and is never overwritten. The file is listed in
`.gitignore`.

## Known limitations

- Single user only; JSON files are not safe for concurrent writes.
- Staff names are plain text (no accounts or authentication).
- `create_ticket` still accepts an older "description + explicit priority" call
  style kept for compatibility. The CLI always uses the calculated-priority style.
- Tickets created in the older style have no category/urgency/affected users.
- No ticket editing or deletion, and no search or filter.

## Pull requests and reviews

- Engineer A's PR: `<paste link>`
- Engineer B's PR: `<paste link>`

## Documentation

- `docs/design-decisions.md` – agreed interfaces and trade-offs
- `docs/ai-learning-log*.md` – AI learning logs
