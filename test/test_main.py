"""Tests for CampusFlow command-line handlers."""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import main


class TestSearchAndFilterMenu(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Broken classroom projector",
                "category": "Hardware",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
                "notes": [],
            },
            {
                "id": "T002",
                "title": "Campus network outage",
                "category": "Network",
                "urgency": "medium",
                "affected_users": 4,
                "priority": "medium",
                "status": "in_progress",
                "assigned_to": "Alex",
                "notes": [],
            },
        ]

    @patch("builtins.input", side_effect=["PROJECTOR", "Hardware", "open", "critical"])
    def test_search_menu_applies_all_filters(self, _mock_input):
        output = io.StringIO()

        with redirect_stdout(output):
            main.search_and_filter_menu(self.tickets)

        text = output.getvalue()
        self.assertIn("Found 1 matching ticket(s).", text)
        self.assertIn("T001", text)
        self.assertNotIn("T002", text)

    @patch("builtins.input", side_effect=["", "", "", ""])
    def test_blank_search_filters_display_all_tickets(self, _mock_input):
        output = io.StringIO()

        with redirect_stdout(output):
            main.search_and_filter_menu(self.tickets)

        text = output.getvalue()
        self.assertIn("Found 2 matching ticket(s).", text)
        self.assertIn("T001", text)
        self.assertIn("T002", text)


class TestAddTicketNoteMenu(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Broken classroom projector",
                "category": "Hardware",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
                "notes": [],
            }
        ]

    @patch("main.save_tickets")
    @patch("builtins.input", side_effect=["T001", "Alex", "Checked the projector"])
    def test_note_menu_adds_and_saves_note(
        self, _mock_input, mock_save
    ):
        output = io.StringIO()

        with redirect_stdout(output):
            main.add_ticket_note(self.tickets)

        self.assertEqual(
            self.tickets[0]["notes"],
            [
                {
                    "note_id": "N001",
                    "author": "Alex",
                    "message": "Checked the projector",
                }
            ],
        )
        mock_save.assert_called_once_with(self.tickets)
        self.assertIn("Note N001 added", output.getvalue())

    @patch("main.save_tickets")
    @patch("builtins.input", side_effect=["T999", "Alex", "Checked the projector"])
    def test_note_menu_rejects_unknown_ticket_without_saving(
        self, _mock_input, mock_save
    ):
        with self.assertRaises(ValueError):
            main.add_ticket_note(self.tickets)

        mock_save.assert_not_called()
        self.assertEqual(self.tickets[0]["notes"], [])


class TestTicketCreationRetries(unittest.TestCase):
    @patch("main.save_tickets")
    @patch(
        "builtins.input",
        side_effect=[
            "",                  # Invalid title
            "Broken projector",  # Valid title
            "InvalidCategory",   # Invalid category
            "hardware",          # Valid category, normalized
            "urgent",             # Invalid urgency
            "high",               # Valid urgency
            "zero",               # Invalid affected-user count
            "12",                 # Valid affected-user count
        ],
    )
    def test_invalid_inputs_retry_until_ticket_is_valid(
        self, _mock_input, mock_save
    ):
        tickets = []
        output = io.StringIO()

        with redirect_stdout(output):
            main.create_new_ticket(tickets)

        self.assertEqual(len(tickets), 1)

        ticket = tickets[0]
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["title"], "Broken projector")
        self.assertEqual(ticket["category"], "Hardware")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["affected_users"], 12)
        self.assertEqual(ticket["priority"], "critical")

        mock_save.assert_called_once_with(tickets)

        text = output.getvalue()
        self.assertGreaterEqual(text.count("Invalid input:"), 4)
        self.assertIn("Ticket T001 created successfully.", text)

    @patch("main.save_tickets")
    @patch(
        "builtins.input",
        side_effect=[
            "Broken projector",
            "Network",
            "medium",
            "not-a-number",
        ],
    )
    def test_incomplete_creation_does_not_append_or_save(
        self, _mock_input, mock_save
    ):
        tickets = []
        original_tickets = list(tickets)

        with self.assertRaises(StopIteration):
            main.create_new_ticket(tickets)

        self.assertEqual(tickets, original_tickets)
        mock_save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
