"""Tests for CampusFlow ticket storage."""
import json
import tempfile
import unittest
from pathlib import Path

from campusflow import storage
from campusflow.tickets import create_ticket, next_ticket_id


class TestTicketStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "data" / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

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
        self.path.write_text('{"id": "T001"}', encoding="utf-8")

        with self.assertRaises(ValueError):
            storage.load_tickets(self.path)

    def test_non_object_ticket_is_rejected(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([{"id": "T001"}, "invalid ticket"]),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            storage.load_tickets(self.path)

    def test_save_creates_parent_directories(self):
        nested = Path(self.temp_dir.name) / "deep" / "nested" / "tickets.json"
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
        create_ticket(tickets, title="A", category="Network",
                      urgency="high", affected_users=12)
        create_ticket(tickets, title="B", category="Other",
                      urgency="low", affected_users=1)
        storage.save_tickets(tickets, self.path)

        reloaded = storage.load_tickets(self.path)
        new = create_ticket(reloaded, title="C", category="Software",
                            urgency="low", affected_users=1)

        ids = [t["id"] for t in reloaded]
        self.assertEqual(new["id"], "T003")
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
