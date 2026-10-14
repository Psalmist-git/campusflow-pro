"""Tests for ticket notes and note ID handling."""
import unittest

from campusflow.tickets import ValidationError, create_ticket, add_note
from campusflow.workflow import update_status


class TestTicketNotes(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        self.ticket = create_ticket(
            self.tickets,
            title="Wi-Fi is down",
            category="Network",
            urgency="high",
            affected_users=15,
        )

    def test_new_ticket_starts_with_empty_notes(self):
        self.assertEqual(self.ticket["notes"], [])

    def test_add_note_trims_author_and_message(self):
        note = add_note(
            self.tickets,
            "T001",
            "  Ada  ",
            "  The router has been restarted.  ",
        )

        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(note["author"], "Ada")
        self.assertEqual(note["message"], "The router has been restarted.")
        self.assertEqual(self.ticket["notes"], [note])

    def test_blank_author_is_rejected(self):
        with self.assertRaises(ValidationError):
            add_note(self.tickets, "T001", "  ", "Router restarted.")

        self.assertEqual(self.ticket["notes"], [])

    def test_message_shorter_than_five_characters_is_rejected(self):
        with self.assertRaises(ValidationError):
            add_note(self.tickets, "T001", "Ada", "Help")

        self.assertEqual(self.ticket["notes"], [])

    def test_message_longer_than_300_characters_is_rejected(self):
        with self.assertRaises(ValidationError):
            add_note(self.tickets, "T001", "Ada", "x" * 301)

        self.assertEqual(self.ticket["notes"], [])

    def test_rejected_note_does_not_consume_note_id(self):
        with self.assertRaises(ValidationError):
            add_note(self.tickets, "T001", "", "Invalid author")

        note = add_note(self.tickets, "T001", "Ada", "Router checked.")
        self.assertEqual(note["note_id"], "N001")

    def test_resolved_ticket_rejects_notes(self):
        self.ticket["assigned_to"] = "Ada"
        update_status(self.tickets, "T001", "in_progress")
        update_status(self.tickets, "T001", "resolved")

        with self.assertRaises(ValidationError):
            add_note(self.tickets, "T001", "Ada", "Still investigating.")

        self.assertEqual(self.ticket["notes"], [])

    def test_notes_survive_resolve_and_reopen(self):
        add_note(self.tickets, "T001", "Ada", "Router checked.")

        self.ticket["assigned_to"] = "Ada"
        update_status(self.tickets, "T001", "in_progress")
        update_status(self.tickets, "T001", "resolved")
        update_status(self.tickets, "T001", "open")

        self.assertEqual(len(self.ticket["notes"]), 1)
        self.assertEqual(
            self.ticket["notes"][0]["message"],
            "Router checked.",
        )

    def test_notes_receive_sequential_ids(self):
        first = add_note(self.tickets, "T001", "Ada", "Router checked.")
        second = add_note(self.tickets, "T001", "Ben", "Cable replaced.")

        self.assertEqual(first["note_id"], "N001")
        self.assertEqual(second["note_id"], "N002")

    def test_malformed_existing_note_is_rejected_without_mutation(self):
        malformed_note = {
            "note_id": "invalid",
            "author": "Ada",
            "message": "Router checked.",
        }
        self.ticket["notes"] = [malformed_note]

        with self.assertRaises(ValidationError):
            add_note(
                self.tickets,
                "T001",
                "Ben",
                "Cable replaced.",
            )

        self.assertEqual(self.ticket["notes"], [malformed_note])

    def test_duplicate_existing_note_ids_are_rejected_without_mutation(self):
        first_note = {
            "note_id": "N001",
            "author": "Ada",
            "message": "Router checked.",
        }
        second_note = {
            "note_id": "N001",
            "author": "Ben",
            "message": "Cable replaced.",
        }
        self.ticket["notes"] = [first_note, second_note]

        with self.assertRaises(ValidationError):
            add_note(
                self.tickets,
                "T001",
                "Chris",
                "Connection restored.",
            )

        self.assertEqual(
            self.ticket["notes"],
            [first_note, second_note],
        )

    def test_unknown_ticket_is_rejected(self):
        with self.assertRaises(ValidationError):
            add_note(self.tickets, "T999", "Ada", "Router checked.")


if __name__ == "__main__":
    unittest.main()
