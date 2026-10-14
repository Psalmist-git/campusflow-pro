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

The suite currently contains 84 tests covering: priority rules and their
boundaries, input validation, unique ticket ID generation, assignment, status
transitions (including rejected transitions and reopening), open work-queue
ordering, reports, JSON save/load round trips, malformed JSON, ticket and note
validation, note persistence, and ID continuity after reload. Storage tests use
temporary files, so your real data is never touched.

## Ticket rules

Each ticket stores `id`, `title`, `category`, `urgency`, `affected_users`,
`priority`, `status`, and `assigned_to`. The newer ticket schema also supports
an optional `notes` list, defaulting to an empty list for newly created tickets.
Each note stores `note_id`, `author`, and `message`. Legacy tickets without
notes remain supported.

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

The work queue shows only tickets with `open` status, ordered by priority
critical -> high -> medium -> low. Tickets with the same priority are ordered
by ascending numeric ticket ID. Tickets with `in_progress` or `resolved`
status are excluded.

## Where data is saved

Tickets are saved to `data/tickets.json` after every change and loaded on
startup. A missing file starts an empty collection. Malformed JSON produces a
clear error and is never overwritten.

The storage layer validates the complete ticket collection before saving or
accepting loaded data. Validation covers required fields, ticket IDs and
duplicates, category, urgency, priority consistency, status, assignee, and note
structure. Invalid data is rejected rather than silently accepted.

Notes are stored within their ticket records. Each note has a unique ID within
its ticket, a nonblank author, and a trimmed message between 5 and 300
characters. Notes can be added to open or in-progress tickets, but not resolved
tickets. Note IDs continue sequentially when tickets are reloaded.

The JSON file is listed in `.gitignore`.

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
