"""Ticket assignment, lifecycle management, and work queue for CampusFlow."""
from campusflow.tickets import ValidationError, find_ticket

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

ALLOWED_STATUSES = {"open", "in_progress", "resolved"}


def _find_ticket(tickets, ticket_id):
    """Return a ticket by ID (case-insensitive) or raise ValidationError."""
    ticket = find_ticket(tickets, ticket_id)
    if ticket is None:
        raise ValidationError(f"Ticket {ticket_id!r} was not found.")
    return ticket


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign an existing, non-resolved ticket to a named staff member."""
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValidationError("Staff name cannot be empty.")

    ticket = _find_ticket(tickets, ticket_id)

    if ticket.get("status") == "resolved":
        raise ValidationError(
            "Reopen the ticket before modifying its assignment."
        )

    ticket["assigned_to"] = staff_name.strip()
    return ticket


def update_status(tickets, ticket_id, new_status):
    """Apply a valid ticket status transition and return the updated ticket.

    Allowed transitions:
      open -> in_progress (only when assigned)
      in_progress -> resolved
      resolved -> open (explicit reopen)
    """
    if not isinstance(new_status, str):
        raise ValidationError("Status must be a string.")

    new_status = new_status.strip().lower()
    if new_status not in ALLOWED_STATUSES:
        raise ValidationError(f"Invalid status: {new_status}")

    ticket = _find_ticket(tickets, ticket_id)
    current_status = ticket.get("status")

    if current_status not in ALLOWED_STATUSES:
        raise ValidationError(f"Ticket has invalid current status: {current_status}")

    if current_status == "resolved":
        if new_status != "open":
            raise ValidationError(
                "Resolved tickets must be explicitly reopened to open first."
            )
        ticket["status"] = "open"
        return ticket

    if new_status == "open":
        raise ValidationError(
            "Only resolved tickets can be reopened; this ticket is not resolved."
        )

    if current_status == "open" and new_status == "in_progress":
        if not ticket.get("assigned_to"):
            raise ValidationError(
                "Assign the ticket before moving it to in_progress."
            )
        ticket["status"] = "in_progress"
        return ticket

    if current_status == "in_progress" and new_status == "resolved":
        ticket["status"] = "resolved"
        return ticket

    raise ValidationError(
        f"Invalid status transition: {current_status} -> {new_status}."
    )


def get_work_queue(tickets):
    """Return unresolved tickets ordered by priority, then numeric ticket ID."""
    unresolved = [
        ticket for ticket in tickets
        if ticket.get("status") != "resolved"
    ]

    def sort_key(ticket):
        priority = str(ticket.get("priority", "")).lower()
        if priority not in PRIORITY_ORDER:
            raise ValidationError(
                f"Ticket {ticket.get('id')} has invalid priority: {priority}"
            )

        ticket_id = ticket.get("id", "")
        if not isinstance(ticket_id, str) or not ticket_id.startswith("T"):
            raise ValidationError(f"Invalid ticket ID: {ticket_id}")

        try:
            numeric_id = int(ticket_id[1:])
        except (TypeError, ValueError):
            raise ValidationError(f"Invalid ticket ID: {ticket_id}") from None

        return PRIORITY_ORDER[priority], numeric_id

    return sorted(unresolved, key=sort_key)
