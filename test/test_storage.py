"""Tests for CampusFlow ticket storage."""

import json
import tempfile
import unittest
from pathlib import Path

from campusflow import storage
from campusflow.tickets import add_note, create_ticket, next_ticket_id


class TestTicketStorage(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "data" / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_json(self, data):
        """Write test data directly to the storage file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(data),
            encoding="utf-8",
        )

    def _valid_new_ticket(self, **overrides):
        """Return a valid ticket using the newer ticket schema."""
        ticket = {
            "id": "T001",
            "title": "Wi-Fi is down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
            "notes": [],
        }
        ticket.update(overrides)
        return ticket

    # ---------------------------------------------------------
    # Existing storage tests
    # ---------------------------------------------------------

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(storage.load_tickets(self.path), [])

    def test_empty_file_returns_empty_list(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")

        self.assertEqual(storage.load_tickets(self.path), [])

    def test_save_and_load_tickets(self):
        tickets = [{
            "id": "T001",
            "title": "Broken projector",
            "description": "Room 2 projector is not working.",
            "priority": "high",
            "status": "open",
            "assigned_to": None,
        }]

        storage.save_tickets(tickets, self.path)

        self.assertEqual(storage.load_tickets(self.path), tickets)

    def test_round_trip_new_ticket_schema(self):
        tickets = []

        create_ticket(
            tickets,
            title="Wi-Fi down",
            category="Network",
            urgency="high",
            affected_users=20,
        )

        storage.save_tickets(tickets, self.path)
        reloaded = storage.load_tickets(self.path)

        self.assertEqual(reloaded, tickets)
        self.assertEqual(next_ticket_id(reloaded), "T002")

    def test_round_trip_empty_list(self):
        storage.save_tickets([], self.path)

        self.assertEqual(storage.load_tickets(self.path), [])

    def test_invalid_json_is_rejected(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("{invalid json", encoding="utf-8")

        with self.assertRaises(ValueError):
            storage.load_tickets(self.path)

    def test_malformed_json_raises_storage_error(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("{ not json", encoding="utf-8")

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

    def test_malformed_json_is_not_overwritten(self):
        original = "{ not json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(original, encoding="utf-8")

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            original,
        )

    def test_non_list_json_is_rejected(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            '{"id": "T001"}',
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            storage.load_tickets(self.path)

    def test_non_object_ticket_is_rejected(self):
        self._write_json([
            {"id": "T001"},
            "invalid ticket",
        ])

        with self.assertRaises(ValueError):
            storage.load_tickets(self.path)

    def test_save_creates_parent_directories(self):
        nested = (
            Path(self.temp_dir.name)
            / "deep"
            / "nested"
            / "tickets.json"
        )

        storage.save_tickets([], nested)

        self.assertTrue(nested.exists())

    def test_save_leaves_no_temporary_file(self):
        tickets = []

        create_ticket(
            tickets,
            title="Network issue",
            category="Other",
            urgency="low",
            affected_users=1,
        )

        storage.save_tickets(tickets, self.path)

        self.assertEqual(
            list(self.path.parent.glob("*.tmp")),
            [],
        )

    def test_new_ticket_after_reload_gets_unique_id(self):
        tickets = []

        create_ticket(
            tickets,
            title="A",
            category="Network",
            urgency="high",
            affected_users=12,
        )

        create_ticket(
            tickets,
            title="B",
            category="Other",
            urgency="low",
            affected_users=1,
        )

        storage.save_tickets(tickets, self.path)
        reloaded = storage.load_tickets(self.path)

        new = create_ticket(
            reloaded,
            title="C",
            category="Software",
            urgency="low",
            affected_users=1,
        )

        ids = [ticket["id"] for ticket in reloaded]

        self.assertEqual(new["id"], "T003")
        self.assertEqual(len(ids), len(set(ids)))

    # ---------------------------------------------------------
    # Strict ticket validation tests
    # ---------------------------------------------------------

    def test_duplicate_ticket_ids_are_rejected(self):
        first = self._valid_new_ticket()
        second = self._valid_new_ticket(title="Another issue")

        self._write_json([first, second])

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

    def test_blank_title_is_rejected(self):
        self._write_json([
            self._valid_new_ticket(title="   ")
        ])

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

    def test_invalid_category_is_rejected(self):
        self._write_json([
            self._valid_new_ticket(category="Electricity")
        ])

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

    def test_invalid_urgency_is_rejected(self):
        self._write_json([
            self._valid_new_ticket(urgency="urgent")
        ])

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

    def test_boolean_affected_users_is_rejected(self):
        self._write_json([
            self._valid_new_ticket(affected_users=True)
        ])

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

    def test_inconsistent_priority_is_rejected(self):
        self._write_json([
            self._valid_new_ticket(priority="low")
        ])

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

    def test_invalid_status_is_rejected(self):
        self._write_json([
            self._valid_new_ticket(status="pending")
        ])

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

    def test_blank_assignee_is_rejected(self):
        self._write_json([
            self._valid_new_ticket(assigned_to="   ")
        ])

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

    # ---------------------------------------------------------
    # Note validation tests
    # ---------------------------------------------------------

    def test_invalid_note_is_rejected(self):
        self._write_json([
            self._valid_new_ticket(
                notes=[
                    {
                        "note_id": "N001",
                        "author": "Ada",
                        "message": "Hi",
                    }
                ]
            )
        ])

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

    def test_duplicate_note_ids_are_rejected(self):
        self._write_json([
            self._valid_new_ticket(
                notes=[
                    {
                        "note_id": "N001",
                        "author": "Ada",
                        "message": "Router checked.",
                    },
                    {
                        "note_id": "N001",
                        "author": "Ben",
                        "message": "Cable replaced.",
                    },
                ]
            )
        ])

        with self.assertRaises(storage.StorageError):
            storage.load_tickets(self.path)

    # ---------------------------------------------------------
    # Save validation tests
    # ---------------------------------------------------------

    def test_invalid_data_is_rejected_before_saving(self):
        invalid_tickets = [
            self._valid_new_ticket(priority="low")
        ]

        with self.assertRaises(storage.StorageError):
            storage.save_tickets(invalid_tickets, self.path)

        self.assertFalse(self.path.exists())

    # ---------------------------------------------------------
    # Backward compatibility tests
    # ---------------------------------------------------------

    def test_legacy_ticket_without_notes_remains_supported(self):
        legacy_ticket = {
            "id": "T001",
            "title": "Broken projector",
            "description": "Room 2 projector is not working.",
            "priority": "high",
            "status": "open",
            "assigned_to": None,
        }

        self._write_json([legacy_ticket])

        loaded = storage.load_tickets(self.path)

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["id"], "T001")

    def test_notes_persist_and_note_ids_continue_after_reload(self):
        tickets = [self._valid_new_ticket()]

        add_note(tickets, "T001", "Ada", "Router checked.")
        storage.save_tickets(tickets, self.path)

        loaded_tickets = storage.load_tickets(self.path)

        self.assertEqual(
            loaded_tickets[0]["notes"],
            [
                {
                    "note_id": "N001",
                    "author": "Ada",
                    "message": "Router checked.",
                }
            ],
        )

        add_note(loaded_tickets, "T001", "Ben", "Cable replaced.")

        self.assertEqual(
            [note["note_id"] for note in loaded_tickets[0]["notes"]],
            ["N001", "N002"],
        )

if __name__ == "__main__":
    unittest.main()
