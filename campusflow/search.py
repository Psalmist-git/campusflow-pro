"""Search and filter CampusFlow tickets."""

from campusflow.tickets import (
    VALID_CATEGORIES,
    VALID_STATUSES,
    VALID_PRIORITIES,
    ValidationError,
)


def search_tickets(tickets, query=""):
    """Return tickets whose titles contain query, ignoring case."""
    if not isinstance(query, str):
        raise ValidationError("Search query must be text.")

    query = query.strip().casefold()

    if not query:
        return list(tickets)

    return [
        ticket
        for ticket in tickets
        if isinstance(ticket.get("title"), str)
        and query in ticket["title"].casefold()
    ]


def filter_tickets(tickets, category=None, status=None, priority=None):
    """Filter tickets using AND logic across supplied criteria."""
    if category is not None:
        if not isinstance(category, str):
            raise ValidationError("Category filter must be text.")

        category_lookup = {value.casefold(): value for value in VALID_CATEGORIES}
        category = category_lookup.get(category.strip().casefold())

        if category is None:
            raise ValidationError(
                f"Invalid category filter. Choose from "
                f"{', '.join(VALID_CATEGORIES)}."
            )

    if status is not None:
        if not isinstance(status, str):
            raise ValidationError("Status filter must be text.")

        status = status.strip().casefold()

        if status not in VALID_STATUSES:
            raise ValidationError(
                f"Invalid status filter. Choose from "
                f"{', '.join(sorted(VALID_STATUSES))}."
            )

    if priority is not None:
        if not isinstance(priority, str):
            raise ValidationError("Priority filter must be text.")

        priority = priority.strip().casefold()

        if priority not in VALID_PRIORITIES:
            raise ValidationError(
                f"Invalid priority filter. Choose from "
                f"{', '.join(sorted(VALID_PRIORITIES))}."
            )

    return [
        ticket
        for ticket in tickets
        if (category is None or ticket.get("category") == category)
        and (
            status is None
            or str(ticket.get("status", "")).casefold() == status
        )
        and (
            priority is None
            or str(ticket.get("priority", "")).casefold() == priority
        )
    ]


def search_and_filter_tickets(
    tickets,
    query="",
    category=None,
    status=None,
    priority=None,
):
    """Apply title search and all supplied filters together."""
    matches = search_tickets(tickets, query)

    return filter_tickets(
        matches,
        category=category,
        status=status,
        priority=priority,
    )
