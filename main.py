"""CampusFlow command-line application."""

from campusflow.reports import print_report
from campusflow.search import search_and_filter_tickets
from campusflow.storage import load_tickets, save_tickets
from campusflow.understanding_check import run_understanding_check
from campusflow.tickets import (
    ValidationError,
    add_note,
    create_ticket,
    find_ticket,
    normalize_category,
    normalize_urgency,
    parse_affected_users,
    validate_title,
)
from campusflow.workflow import (
    assign_ticket,
    get_work_queue,
    update_status,
)


def print_ticket(ticket):
    """Print a ticket and its notes."""
    print(f"\nID:             {ticket.get('id')}")
    print(f"Title:          {ticket.get('title')}")

    if ticket.get("description"):
        print(f"Description:    {ticket['description']}")

    if ticket.get("category"):
        print(f"Category:       {ticket['category']}")

    if ticket.get("urgency"):
        print(f"Urgency:        {ticket['urgency']}")

    if ticket.get("affected_users") is not None:
        print(f"Affected users: {ticket['affected_users']}")

    print(f"Priority:       {ticket.get('priority')}")
    print(f"Status:         {ticket.get('status')}")
    print(f"Assigned to:    {ticket.get('assigned_to') or 'Unassigned'}")

    notes = ticket.get("notes", [])

    print(f"Notes:          {len(notes)}")

    for note in notes:
        print(
            f"  {note.get('note_id')} | "
            f"{note.get('author')} | "
            f"{note.get('message')}"
        )


def display_tickets(tickets):
    """Display a collection of tickets."""
    if not tickets:
        print("\nNo tickets found.")
        return

    print("\n=== CampusFlow Tickets ===")

    for ticket in tickets:
        print_ticket(ticket)


def view_one_ticket(tickets):
    """Find and display one ticket."""
    ticket_id = input("Ticket ID: ").strip()
    ticket = find_ticket(tickets, ticket_id)

    if ticket is None:
        raise ValidationError(f"Ticket {ticket_id!r} was not found.")

    print_ticket(ticket)


def prompt_until_valid(prompt, validator):
    """Repeat a prompt until its value passes the supplied validator."""
    while True:
        raw_value = input(prompt)

        try:
            return validator(raw_value)
        except ValidationError as error:
            print(f"Invalid input: {error}")


def create_new_ticket(tickets):
    """Create and save a ticket after all required inputs are valid."""
    title = prompt_until_valid("Ticket title: ", validate_title)

    category = prompt_until_valid(
        "Category (Network/Hardware/Software/Other): ",
        normalize_category,
    )

    urgency = prompt_until_valid(
        "Urgency (low/medium/high): ",
        normalize_urgency,
    )

    affected_users = prompt_until_valid(
        "Number of affected users: ",
        parse_affected_users,
    )

    # No ticket is created until every required field is valid.
    ticket = create_ticket(
        tickets,
        title=title,
        category=category,
        urgency=urgency,
        affected_users=affected_users,
    )

    save_tickets(tickets)

    print(f"\nTicket {ticket['id']} created successfully.")
    print(f"Calculated priority: {ticket['priority']}")

def assign_existing_ticket(tickets):
    """Assign a ticket to a staff member."""
    ticket_id = input("Ticket ID: ").strip()
    staff_name = input("Staff member's name: ").strip()

    assign_ticket(tickets, ticket_id, staff_name)
    save_tickets(tickets)

    print(f"\nTicket {ticket_id} assigned to {staff_name.strip()}.")


def change_ticket_status(tickets):
    """Change a ticket's status."""
    ticket_id = input("Ticket ID: ").strip()

    print("\n1. open")
    print("2. in_progress")
    print("3. resolved")

    choices = {
        "1": "open",
        "2": "in_progress",
        "3": "resolved",
    }

    choice = input("Choose a status (1-3): ").strip()
    new_status = choices.get(choice)

    if new_status is None:
        print("Invalid choice. No changes made.")
        return

    update_status(tickets, ticket_id, new_status)
    save_tickets(tickets)

    print(f"\nTicket {ticket_id} status updated to {new_status}.")


def display_work_queue(tickets):
    """Display open tickets in priority order."""
    queue = get_work_queue(tickets)

    if not queue:
        print("\nThe work queue is empty.")
        return

    print("\n=== Prioritized Work Queue ===")

    for ticket in queue:
        print(
            f"{ticket['id']} | "
            f"{ticket['priority'].upper()} | "
            f"{ticket['status']} | "
            f"{ticket['title']} | "
            f"Assigned to: {ticket.get('assigned_to') or 'Unassigned'}"
        )


def search_and_filter_menu(tickets):
    """Search titles and apply optional AND-combined filters."""
    print("\n=== Search and Filter Tickets ===")
    print("Leave any prompt blank to skip that criterion.")

    query = input("Title contains: ").strip()
    category = input(
        "Category (Network/Hardware/Software/Other): "
    ).strip()
    status = input(
        "Status (open/in_progress/resolved): "
    ).strip()
    priority = input(
        "Priority (low/medium/high/critical): "
    ).strip()

    matches = search_and_filter_tickets(
        tickets,
        query=query,
        category=category or None,
        status=status or None,
        priority=priority or None,
    )

    print(f"\nFound {len(matches)} matching ticket(s).")
    display_tickets(matches)


def add_ticket_note(tickets):
    """Add a note to an eligible ticket and persist it."""
    print("\n=== Add Ticket Note ===")

    ticket_id = input("Ticket ID: ").strip()
    author = input("Your name: ").strip()
    message = input("Note (5–300 characters): ")

    note = add_note(
        tickets,
        ticket_id=ticket_id,
        author=author,
        message=message,
    )

    save_tickets(tickets)

    print(
        f"\nNote {note['note_id']} added to ticket "
        f"{ticket_id.upper()} successfully."
    )


def show_menu():
    """Display the main menu."""
    print("\n========== CAMPUSFLOW ==========")
    print("1. Create a ticket")
    print("2. Assign a ticket")
    print("3. Update ticket status")
    print("4. View prioritized work queue")
    print("5. View all tickets")
    print("6. View one ticket")
    print("7. Generate report")
    print("8. Search and filter tickets")
    print("9. Add a ticket note")
    print("10. Engineering Understanding Check")
    print("11. Exit")
    print("================================")


def main():
    """Run the CampusFlow CLI."""
    try:
        tickets = load_tickets()
    except (ValueError, OSError) as error:
        print(f"Could not load ticket data: {error}")
        return

    print("\nWelcome to CampusFlow!")
    print(f"Loaded {len(tickets)} ticket(s).")

    while True:
        show_menu()
        choice = input("Select an option (1-10): ").strip()

        try:
            if choice == "1":
                create_new_ticket(tickets)
            elif choice == "2":
                assign_existing_ticket(tickets)
            elif choice == "3":
                change_ticket_status(tickets)
            elif choice == "4":
                display_work_queue(tickets)
            elif choice == "5":
                display_tickets(tickets)
            elif choice == "6":
                view_one_ticket(tickets)
            elif choice == "7":
                print_report(tickets)
            elif choice == "8":
                search_and_filter_menu(tickets)
            elif choice == "9":
                add_ticket_note(tickets)
            elif choice == "10":
                run_understanding_check()
            elif choice == "11":
                print("\nThank you for using CampusFlow Pro. I hope we helped resolved you challenge.")
                break
            else:
                print("\nInvalid choice. Select a number from 1 to 10.")

        except (ValueError, OSError) as error:
            print(f"\nOperation failed: {error}")


if __name__ == "__main__":
    main()
