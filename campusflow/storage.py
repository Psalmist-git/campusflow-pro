"""JSON persistence and validation for CampusFlow tickets.

Owner: Engineer A.

Storage contract:
- Missing or empty files return an empty ticket list.
- Malformed JSON and invalid ticket data raise StorageError.
- Legacy tickets remain supported without changing their schema.
- New-schema tickets must have consistent category, urgency,
  affected-user count, and calculated priority.
- Notes are validated and preserved.
- Saving validates the complete collection before writing.
- Saving uses atomic temporary-file replacement.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from campusflow.tickets import (
    VALID_PRIORITIES,
    VALID_STATUSES,
    VALID_URGENCIES,
    ValidationError,
    compute_priority,
    normalize_category,
    normalize_urgency,
    validate_affected_users,
    validate_title,
)

DEFAULT_PATH = Path("data") / "tickets.json"
DEFAULT_STORAGE_PATH = DEFAULT_PATH

_TICKET_ID_PATTERN = re.compile(r"^T\d+$")
_NOTE_ID_PATTERN = re.compile(r"^N\d+$")

_REQUIRED_TICKET_FIELDS = {
    "id",
    "title",
    "priority",
    "status",
    "assigned_to",
}

_NEW_SCHEMA_FIELDS = {
    "category",
    "urgency",
    "affected_users",
}


class StorageError(ValueError):
    """Raised when ticket storage cannot be read or validated."""


def _validate_note(note, ticket_id, seen_note_ids):
    """Validate one note and register its ID."""
    if not isinstance(note, dict):
        raise StorageError(
            f"Ticket {ticket_id}: every note must be an object."
        )

    required_fields = {"note_id", "author", "message"}
    missing = required_fields - note.keys()

    if missing:
        raise StorageError(
            f"Ticket {ticket_id}: note is missing fields: "
            f"{', '.join(sorted(missing))}."
        )

    note_id = note["note_id"]

    if (
        not isinstance(note_id, str)
        or not _NOTE_ID_PATTERN.fullmatch(note_id)
    ):
        raise StorageError(
            f"Ticket {ticket_id}: invalid note ID {note_id!r}."
        )

    if note_id in seen_note_ids:
        raise StorageError(
            f"Ticket {ticket_id}: duplicate note ID {note_id!r}."
        )

    seen_note_ids.add(note_id)

    author = note["author"]

    if not isinstance(author, str) or not author.strip():
        raise StorageError(
            f"Ticket {ticket_id}: note author must not be blank."
        )

    message = note["message"]

    if not isinstance(message, str):
        raise StorageError(
            f"Ticket {ticket_id}: note message must be text."
        )

    clean_message = message.strip()

    if not 5 <= len(clean_message) <= 300:
        raise StorageError(
            f"Ticket {ticket_id}: note message must contain "
            "5–300 characters after trimming."
        )


def _validate_ticket(ticket, seen_ticket_ids):
    """Validate one ticket without modifying it."""
    if not isinstance(ticket, dict):
        raise StorageError(
            "Every stored ticket must be a JSON object."
        )

    missing = _REQUIRED_TICKET_FIELDS - ticket.keys()

    if missing:
        raise StorageError(
            "Ticket is missing required fields: "
            f"{', '.join(sorted(missing))}."
        )

    ticket_id = ticket["id"]

    if (
        not isinstance(ticket_id, str)
        or not _TICKET_ID_PATTERN.fullmatch(ticket_id)
    ):
        raise StorageError(
            f"Invalid ticket ID: {ticket_id!r}."
        )

    normalized_id = ticket_id.upper()

    if normalized_id in seen_ticket_ids:
        raise StorageError(
            f"Duplicate ticket ID: {ticket_id}."
        )

    seen_ticket_ids.add(normalized_id)

    try:
        validate_title(ticket["title"])
    except ValidationError as exc:
        raise StorageError(
            f"Ticket {ticket_id}: {exc}"
        ) from exc

    priority = ticket["priority"]

    if (
        not isinstance(priority, str)
        or priority not in VALID_PRIORITIES
    ):
        raise StorageError(
            f"Ticket {ticket_id}: invalid priority {priority!r}."
        )

    status = ticket["status"]

    if (
        not isinstance(status, str)
        or status not in VALID_STATUSES
    ):
        raise StorageError(
            f"Ticket {ticket_id}: invalid status {status!r}."
        )

    assignee = ticket["assigned_to"]

    if assignee is not None and (
        not isinstance(assignee, str) or not assignee.strip()
    ):
        raise StorageError(
            f"Ticket {ticket_id}: assigned_to must be null "
            "or a nonblank name."
        )

    # Description is optional for compatibility with existing records.
    if "description" in ticket:
        description = ticket["description"]

        if (
            not isinstance(description, str)
            or not description.strip()
        ):
            raise StorageError(
                f"Ticket {ticket_id}: description must not be blank."
            )

    present_new_fields = _NEW_SCHEMA_FIELDS.intersection(
        ticket.keys()
    )

    # Legacy tickets may omit the new fields. If any new field exists,
    # all three fields must be present.
    if present_new_fields and present_new_fields != _NEW_SCHEMA_FIELDS:
        missing_new = _NEW_SCHEMA_FIELDS - ticket.keys()

        raise StorageError(
            f"Ticket {ticket_id}: incomplete category/urgency schema; "
            f"missing {', '.join(sorted(missing_new))}."
        )

    if present_new_fields:
        try:
            category = normalize_category(ticket["category"])
            urgency = normalize_urgency(ticket["urgency"])
            affected_users = validate_affected_users(
                ticket["affected_users"]
            )
        except ValidationError as exc:
            raise StorageError(
                f"Ticket {ticket_id}: {exc}"
            ) from exc

        # Require the canonical spelling used by the application.
        if ticket["category"] != category:
            raise StorageError(
                f"Ticket {ticket_id}: category must use canonical spelling."
            )

        if ticket["urgency"] != urgency:
            raise StorageError(
                f"Ticket {ticket_id}: urgency must use lowercase spelling."
            )

        expected_priority = compute_priority(
            urgency,
            affected_users,
        )

        if priority != expected_priority:
            raise StorageError(
                f"Ticket {ticket_id}: priority {priority!r} does not "
                f"match calculated priority {expected_priority!r}."
            )

    # Legacy tickets without a notes field remain valid.
    notes = ticket.get("notes", [])

    if not isinstance(notes, list):
        raise StorageError(
            f"Ticket {ticket_id}: notes must be a list."
        )

    seen_note_ids = set()

    for note in notes:
        _validate_note(note, ticket_id, seen_note_ids)


def _validate_collection(tickets):
    """Validate the complete collection without modifying it."""
    if not isinstance(tickets, list):
        raise StorageError(
            "Stored tickets must be a JSON list."
        )

    seen_ticket_ids = set()

    for ticket in tickets:
        _validate_ticket(ticket, seen_ticket_ids)


def load_tickets(path: Path | str = DEFAULT_PATH) -> list[dict]:
    """Load and validate tickets without modifying the stored file.

    Missing or empty files return an empty list. Legacy records without
    notes remain unchanged when loaded.
    """
    p = Path(path)

    if not p.exists():
        return []

    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise StorageError(
            f"Could not read {p}: {exc}"
        ) from exc

    if not raw.strip():
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise StorageError(
            f"{p} contains invalid JSON "
            f"({exc.msg} at line {exc.lineno}). "
            "The file was not modified."
        ) from exc

    try:
        _validate_collection(data)
    except StorageError as exc:
        raise StorageError(
            f"Invalid ticket data in {p}: {exc}"
        ) from exc

    # Do not modify legacy records after validation.
    return data


def save_tickets(
    tickets: list[dict],
    path: Path | str = DEFAULT_PATH,
) -> None:
    """Validate and atomically save the complete ticket collection."""
    # Reject invalid data before creating or replacing any file.
    _validate_collection(tickets)

    p = Path(path)
    tmp = p.with_suffix(p.suffix + ".tmp")

    try:
        p.parent.mkdir(parents=True, exist_ok=True)

        tmp.write_text(
            json.dumps(tickets, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        os.replace(tmp, p)

    except (OSError, TypeError, ValueError) as exc:
        raise StorageError(
            f"Could not save tickets to {p}: {exc}"
        ) from exc

    finally:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
