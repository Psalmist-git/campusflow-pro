
## Decision: Ticket Data Model

**Decision:** Represent each ticket as a Python dictionary containing its
identifier, title, priority, status, and assignment information. The original
ticket interface also stores a description. The newer interface supports
category, urgency, and the number of affected users.

**Rationale:** Dictionaries provide a simple data structure that can be
converted to and from JSON without requiring an object-relational mapper.

**Trade-off:** Dictionaries are flexible, but invalid fields and inconsistent
values must be prevented through validation.

## Decision: Ticket Identifiers

**Decision:** Use sequential identifiers in the format T001, T002, T003, and
so on.

**Rationale:** Readable identifiers make tickets easier to reference in the
command-line interface.

**Trade-off:** Sequential identifiers are not globally unique across
independent installations. A shared multi-user deployment would need a
centralized identifier-generation strategy.

## Decision: Priority Calculation

**Decision:** Support low, medium, high, and critical priorities. In the
category-and-urgency ticket interface, calculate priority using urgency and
the number of affected users.

The rules are applied in this order:

1. High urgency and at least 10 affected users: critical.
2. High urgency or at least 10 affected users: high.
3. Medium urgency or at least 3 affected users: medium.
4. Otherwise: low.

The original ticket-creation interface also supports an explicitly supplied
priority for compatibility.

**Rationale:** Automatic prioritization provides a consistent way to identify
tickets that need urgent attention.

**Trade-off:** Fixed thresholds are easy to understand and test, but may need
adjustment as operational requirements change.

## Decision: Ticket Status Lifecycle

**Decision:** Support three statuses: open, in_progress, and resolved.

The permitted transitions are:

- open -> in_progress, provided the ticket is assigned.
- in_progress -> resolved.
- resolved -> open, to reopen a ticket explicitly.

Other transitions are rejected.

**Rationale:** Explicit transitions prevent tickets from bypassing required
workflow steps.

**Trade-off:** The lifecycle is predictable, but additional statuses would
require changes to the workflow implementation and its tests.

## Decision: Ticket Assignment

**Decision:** A ticket can be assigned to a named staff member. Resolved
tickets cannot be reassigned until they have been reopened.

**Rationale:** Assignment establishes responsibility for handling a ticket
and prevents completed tickets from being modified through the normal
assignment operation.

**Trade-off:** The current implementation stores the staff member's name as
text. It does not provide staff accounts, authorization, or identity
verification.

## Decision: JSON Persistence

**Decision:** Store tickets in a JSON file at data/tickets.json. Missing or
empty files produce an empty ticket list. Invalid JSON, invalid top-level
data, and non-object ticket entries raise a storage error.

Saving writes to a temporary file and then replaces the destination file
atomically.

**Rationale:** JSON is human-readable, easy to inspect, and sufficient for
the current single-user project.

**Trade-off:** JSON files are not designed for concurrent multi-user writes,
large-scale queries, or database transactions. A production multi-user
application may require a database.

## Decision: Error Handling

**Decision:** Validate ticket input and reject invalid operations using
exceptions. The command-line application catches expected operational
errors and displays a message to the user.

**Rationale:** Invalid input should not silently create incorrect tickets
or produce unexpected workflow transitions.

**Trade-off:** Exceptions provide a straightforward error-handling
mechanism, but callers must handle them appropriately.

## Decision: Work Queue Ordering

**Decision:** Exclude resolved tickets from the active work queue. Sort the
remaining tickets by priority in the following order:

1. Critical
2. High
3. Medium
4. Low

Within the same priority, sort by the numeric portion of the ticket ID.

**Rationale:** Urgent tickets appear first, and numeric ordering keeps
ticket identifiers in their expected sequence.

**Trade-off:** The queue does not currently consider ticket age, deadlines,
staff workload, or service-level agreements.

## Decision: Automated Testing

**Decision:** Use Python's unittest framework to test ticket validation,
priority calculation, assignment, status transitions, persistence, reporting,
and work queue ordering.

**Rationale:** Automated tests make it easier to detect regressions when
features are changed or integrated from different branches.

**Trade-off:** Passing tests provide evidence that tested behavior works;
they do not prove that every possible failure or production scenario has
been covered.

## Decision: Command-Line Interface

**Decision:** Provide a menu-driven command-line interface for creating
tickets, assigning staff, updating statuses, viewing tickets, displaying
the prioritized work queue, and generating reports.

**Rationale:** A command-line interface keeps the application simple and
allows the core workflow to be exercised without a web server.

**Trade-off:** The current interface is not a multi-user web application and
does not provide a graphical dashboard.


## Decision: Module Ownership and Shared Contracts

**Decision:** `tickets.py` (creation, validation, priority, ID lookup) belongs to
Engineer A. `workflow.py` (assignment, status changes, queue) and `reports.py`
belong to Engineer B. `storage.py` is shared: Engineer A wrote the first version and
Engineer B integrated and tested it. All modules raise `ValidationError` (a subclass
of `ValueError`) for bad input and `StorageError` for file problems; the CLI catches
both and prints the message.

**Rationale:** One clear owner per module makes it easy to review and defend code.

## Decision: Single Assignment Function and Case-Insensitive IDs

**Decision:** `assign_ticket` exists only in `workflow.py`. Ticket IDs are matched
case-insensitively (`t001` finds `T001`) through `tickets.find_ticket`, which
`workflow.py` reuses.

**Rationale:** Two copies of `assign_ticket` behaved differently (one rejected
lowercase IDs, one allowed assigning resolved tickets). One implementation keeps
the rules consistent.

## Decision: CLI Input Parsing

**Decision:** The "affected users" text typed in the CLI is converted with
`parse_affected_users`, which raises `ValidationError` with a clear message for
text, decimals, zero and negatives. A "View one ticket" menu option (F2) was added.
