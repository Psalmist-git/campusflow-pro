"""Ticket creation, validation, priority calculation, and assignment."""
from __future__ import annotations

VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_CATEGORIES = ("Network", "Hardware", "Software", "Other")
VALID_URGENCIES = ("low", "medium", "high")
VALID_STATUSES = ("open", "in_progress", "resolved")

_CATEGORY_LOOKUP = {c.lower(): c for c in VALID_CATEGORIES}
_URGENCY_LOOKUP = {u.lower(): u for u in VALID_URGENCIES}


class ValidationError(ValueError):
    """Raised when ticket input fails validation."""


def normalize_category(raw: str) -> str:
    if not isinstance(raw, str):
        raise ValidationError("Category must be text.")

    key = raw.strip().lower()
    if key not in _CATEGORY_LOOKUP:
        raise ValidationError(
            f"Unknown category {raw!r}. "
            f"Choose from {', '.join(VALID_CATEGORIES)}."
        )
    return _CATEGORY_LOOKUP[key]


def normalize_urgency(raw: str) -> str:
    if not isinstance(raw, str):
        raise ValidationError("Urgency must be text.")

    key = raw.strip().lower()
    if key not in _URGENCY_LOOKUP:
        raise ValidationError(
            f"Unknown urgency {raw!r}. "
            f"Choose from {', '.join(VALID_URGENCIES)}."
        )
    return _URGENCY_LOOKUP[key]


def validate_title(raw: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise ValidationError("Title must not be blank.")
    return raw.strip()


def validate_description(raw: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise ValidationError("Description must not be blank.")
    return raw.strip()


def validate_affected_users(raw) -> int:
    if isinstance(raw, bool) or not isinstance(raw, int) or raw <= 0:
        raise ValidationError("Affected users must be a positive integer.")
    return raw


def parse_affected_users(text) -> int:
    """Convert typed input (e.g. from the CLI) to a valid affected_users int.

    Rejects text, decimals, zero and negatives with a ValidationError.
    """
    if not isinstance(text, str):
        return validate_affected_users(text)
    try:
        value = int(text.strip())
    except ValueError:
        raise ValidationError(
            "Affected users must be a positive whole number (e.g. 15)."
        ) from None
    return validate_affected_users(value)


def compute_priority(urgency: str, affected_users: int) -> str:
    """Calculate priority; the first matching rule wins."""
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def next_ticket_id(tickets: list[dict]) -> str:
    """Return the next sequential ID, using numeric rather than text ordering."""
    highest = 0

    for ticket in tickets:
        if not isinstance(ticket, dict):
            continue

        ticket_id = ticket.get("id", "")
        if (
            isinstance(ticket_id, str)
            and ticket_id.startswith("T")
            and ticket_id[1:].isdigit()
        ):
            highest = max(highest, int(ticket_id[1:]))

    return f"T{highest + 1:03d}"


def find_ticket(tickets: list[dict], ticket_id: str) -> dict | None:
    """Find a ticket by ID without regard to letter case."""
    if not isinstance(ticket_id, str):
        return None

    wanted = ticket_id.strip().upper()

    for ticket in tickets:
        if isinstance(ticket, dict):
            existing = ticket.get("id")
            if isinstance(existing, str) and existing.upper() == wanted:
                return ticket

    return None


def create_ticket(
    tickets: list[dict],
    *args,
    title=None,
    description=None,
    priority=None,
    category=None,
    urgency=None,
    affected_users=None,
) -> dict:
    """Create a ticket using either supported interface.

    Legacy interface:
        create_ticket(tickets, title, description, priority="medium")

    Category/urgency interface:
        create_ticket(
            tickets, title="Wi-Fi down", category="Network",
            urgency="high", affected_users=15
        )

    Validation happens before appending, so invalid input leaves the list
    unchanged.
    """
    if args:
        if len(args) not in (2, 3):
            raise ValidationError(
                "Legacy creation requires title, description, and optional priority."
            )
        if title is not None or description is not None:
            raise ValidationError("Do not mix positional and keyword title/description.")
        title, description = args[:2]
        if len(args) == 3:
            if priority is not None:
                raise ValidationError("Priority was supplied more than once.")
            priority = args[2]

    clean_title = validate_title(title)
    ticket_id = next_ticket_id(tickets)

    # New interface: calculate priority from urgency and affected users.
    if category is not None or urgency is not None or affected_users is not None:
        clean_category = normalize_category(category)
        clean_urgency = normalize_urgency(urgency)
        clean_users = validate_affected_users(affected_users)

        ticket = {
            "id": ticket_id,
            "title": clean_title,
            "category": clean_category,
            "urgency": clean_urgency,
            "affected_users": clean_users,
            "priority": compute_priority(clean_urgency, clean_users),
            "status": "open",
            "assigned_to": None,
        }

        if description is not None:
            ticket["description"] = validate_description(description)

    # Original interface: accept a description and optional explicit priority.
    else:
        clean_description = validate_description(description)
        chosen_priority = "medium" if priority is None else priority

        if not isinstance(chosen_priority, str):
            raise ValidationError("Priority must be a string.")

        chosen_priority = chosen_priority.strip().lower()
        if chosen_priority not in VALID_PRIORITIES:
            raise ValidationError(f"Invalid priority: {chosen_priority}")

        ticket = {
            "id": ticket_id,
            "title": clean_title,
            "description": clean_description,
            "priority": chosen_priority,
            "status": "open",
            "assigned_to": None,
        }

    tickets.append(ticket)
    return ticket
