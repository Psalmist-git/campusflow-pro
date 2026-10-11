"""CampusFlow command-line application."""

from campusflow.reports import print_report
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_ticket,
    get_work_queue,
    update_status,
)


def display_tickets(tickets):
    if not tickets:
        print("\nNo tickets found.")
        return

    print("\n=== CampusFlow Tickets ===")
    for ticket in tickets:
        print(f"\nID:          {ticket.get('id')}")
        print(f"Title:       {ticket.get('title')}")
        print(f"Description: {ticket.get('description')}")
        print(f"Priority:    {ticket.get('priority')}")
        print(f"Status:      {ticket.get('status')}")
        print(f"Assigned to: {ticket.get('assigned_to') or 'Unassigned'}")


def create_new_ticket(tickets):
    title = input("Ticket title: ").strip()
    category = input("Category (Network/Hardware/Software/Other): ").strip()
    urgency = input("Urgency (low/medium/high): ").strip()
    affected_users = int(input("Number of affected users: "))

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
    ticket_id = input("Ticket ID: ").strip()
    staff_name = input("Staff member's name: ").strip()

    assign_ticket(tickets, ticket_id, staff_name)
    save_tickets(tickets)
    print(f"\nTicket {ticket_id} assigned to {staff_name}.")


def change_ticket_status(tickets):
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


def show_menu():
    print("\n========== CAMPUSFLOW ==========")
    print("1. Create a ticket")
    print("2. Assign a ticket")
    print("3. Update ticket status")
    print("4. View prioritized work queue")
    print("5. View all tickets")
    print("6. Generate report")
    print("7. Exit")
    print("================================")


def main():
    try:
        tickets = load_tickets()
    except (ValueError, OSError) as error:
        print(f"Could not load ticket data: {error}")
        return

    print("\nWelcome to CampusFlow!")
    print(f"Loaded {len(tickets)} ticket(s).")

    while True:
        show_menu()
        choice = input("Select an option (1-7): ").strip()

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
                print_report(tickets)
            elif choice == "7":
                print("\nThank you for using CampusFlow. Goodbye!")
                break
            else:
                print("\nInvalid choice. Select a number from 1 to 7.")

        except (ValueError, OSError) as error:
            print(f"\nOperation failed: {error}")


if __name__ == "__main__":
    main()
