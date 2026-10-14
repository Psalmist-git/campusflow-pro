"""Tests for CampusFlow ticket search and filtering."""

import unittest

from campusflow.search import (
    filter_tickets,
    search_and_filter_tickets,
    search_tickets,
)
from campusflow.tickets import ValidationError


def make_ticket(
    ticket_id,
    title,
    category="Network",
    status="open",
    priority="medium",
):
    return {
        "id": ticket_id,
        "title": title,
        "category": category,
        "status": status,
        "priority": priority,
    }


class TestTicketSearch(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            make_ticket("T001", "Campus Wi-Fi outage", priority="critical"),
            make_ticket(
                "T002",
                "Broken classroom projector",
                category="Hardware",
                status="in_progress",
                priority="high",
            ),
            make_ticket(
                "T003",
                "Wi-Fi password reset",
                category="Software",
                status="resolved",
                priority="low",
            ),
        ]

    def test_search_is_case_insensitive(self):
        result = search_tickets(self.tickets, "wI-fI")
        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T001", "T003"],
        )

    def test_search_matches_substring(self):
        result = search_tickets(self.tickets, "project")
        self.assertEqual([ticket["id"] for ticket in result], ["T002"])

    def test_blank_search_returns_all_tickets(self):
        self.assertEqual(search_tickets(self.tickets, "  "), self.tickets)

    def test_search_with_no_matches_returns_empty_list(self):
        self.assertEqual(search_tickets(self.tickets, "printer"), [])

    def test_non_text_search_is_rejected(self):
        with self.assertRaises(ValidationError):
            search_tickets(self.tickets, None)

    def test_filter_by_category(self):
        result = filter_tickets(self.tickets, category="hardware")
        self.assertEqual([ticket["id"] for ticket in result], ["T002"])

    def test_filter_by_status(self):
        result = filter_tickets(self.tickets, status="RESOLVED")
        self.assertEqual([ticket["id"] for ticket in result], ["T003"])

    def test_filter_by_priority(self):
        result = filter_tickets(self.tickets, priority="critical")
        self.assertEqual([ticket["id"] for ticket in result], ["T001"])

    def test_combined_filters_use_and_logic(self):
        result = filter_tickets(
            self.tickets,
            category="Network",
            status="open",
            priority="critical",
        )
        self.assertEqual([ticket["id"] for ticket in result], ["T001"])

    def test_combined_filters_can_return_no_matches(self):
        result = filter_tickets(
            self.tickets,
            category="Hardware",
            status="resolved",
        )
        self.assertEqual(result, [])

    def test_search_and_filters_work_together(self):
        result = search_and_filter_tickets(
            self.tickets,
            query="wi-fi",
            status="resolved",
            priority="low",
        )
        self.assertEqual([ticket["id"] for ticket in result], ["T003"])

    def test_invalid_category_filter_is_rejected(self):
        with self.assertRaises(ValidationError):
            filter_tickets(self.tickets, category="Electricity")

    def test_invalid_status_filter_is_rejected(self):
        with self.assertRaises(ValidationError):
            filter_tickets(self.tickets, status="waiting")

    def test_invalid_priority_filter_is_rejected(self):
        with self.assertRaises(ValidationError):
            filter_tickets(self.tickets, priority="urgent")


if __name__ == "__main__":
    unittest.main()
