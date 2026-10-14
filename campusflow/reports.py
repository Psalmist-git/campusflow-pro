"""Reporting functions for CampusFlow."""

from collections import Counter

from campusflow.tickets import (
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    VALID_STATUSES,
    ValidationError,
)


def generate_report(tickets):
    """Generate ticket totals by status, priority, and category."""
    status_counts = Counter()
    priority_counts = Counter()
    category_counts = Counter()

    categories = (*VALID_CATEGORIES, "Uncategorized")

    for ticket in tickets:
        status = ticket.get("status", "open")
        priority = str(ticket.get("priority", "medium")).casefold()
        category = ticket.get("category", "Uncategorized")

        if status not in VALID_STATUSES:
            raise ValidationError(f"Unknown ticket status: {status}")

        if priority not in VALID_PRIORITIES:
            raise ValidationError(f"Unknown ticket priority: {priority}")

        if category is None or category == "":
            category = "Uncategorized"

        if category not in categories:
            raise ValidationError(f"Unknown ticket category: {category}")

        status_counts[status] += 1
        priority_counts[priority] += 1
        category_counts[category] += 1

    total = len(tickets)
    resolved = status_counts["resolved"]
    unresolved = total - resolved
    resolution_percentage = (resolved / total * 100) if total else 0.0

    return {
        "total_tickets": total,
        "by_status": {
            status: status_counts[status]
            for status in ("open", "in_progress", "resolved")
        },
        "by_priority": {
            priority: priority_counts[priority]
            for priority in ("critical", "high", "medium", "low")
        },
        "by_category": {
            category: category_counts[category]
            for category in categories
        },
        "unresolved_tickets": unresolved,
        "resolved_tickets": resolved,
        "resolution_percentage": round(resolution_percentage, 2),
    }


def print_report(tickets, file=None):
    """Print a readable ticket report."""
    report = generate_report(tickets)

    print("=== CampusFlow Ticket Report ===", file=file)
    print(f"Total tickets: {report['total_tickets']}", file=file)

    print("\nBy status:", file=file)
    for status, count in report["by_status"].items():
        print(f"  {status}: {count}", file=file)

    print("\nBy priority:", file=file)
    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}", file=file)

    print("\nBy category:", file=file)
    for category, count in report["by_category"].items():
        print(f"  {category}: {count}", file=file)

    print(
        f"\nUnresolved tickets: {report['unresolved_tickets']}",
        file=file,
    )
    print(
        f"Resolved tickets: {report['resolved_tickets']}",
        file=file,
    )
    print(
        f"Resolution percentage: {report['resolution_percentage']:.2f}%",
        file=file,
    )

    return report
