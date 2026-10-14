"""Tests for CampusFlow ticket reports."""

import unittest

from campusflow.reports import generate_report, print_report
from campusflow.tickets import ValidationError


def make_ticket(
    ticket_id,
    status="open",
    priority="medium",
    category="Network",
):
    return {
        "id": ticket_id,
        "title": f"Ticket {ticket_id}",
        "status": status,
        "priority": priority,
        "category": category,
    }


class TestExpandedReports(unittest.TestCase):
    def test_report_includes_category_and_resolution_metrics(self):
        tickets = [
            make_ticket("T001", category="Network", priority="critical"),
            make_ticket("T002", category="Hardware", priority="high"),
            make_ticket(
                "T003",
                status="in_progress",
                category="Network",
                priority="medium",
            ),
            make_ticket(
                "T004",
                status="resolved",
                category="Software",
                priority="low",
            ),
        ]

        report = generate_report(tickets)

        self.assertEqual(report["total_tickets"], 4)
        self.assertEqual(report["resolved_tickets"], 1)
        self.assertEqual(report["unresolved_tickets"], 3)
        self.assertEqual(report["resolution_percentage"], 25.0)
        self.assertEqual(
            report["by_category"],
            {
                "Network": 2,
                "Hardware": 1,
                "Software": 1,
                "Other": 0,
                "Uncategorized": 0,
            },
        )

    def test_empty_report_has_zero_resolution_percentage(self):
        report = generate_report([])

        self.assertEqual(report["total_tickets"], 0)
        self.assertEqual(report["resolved_tickets"], 0)
        self.assertEqual(report["unresolved_tickets"], 0)
        self.assertEqual(report["resolution_percentage"], 0.0)

    def test_legacy_ticket_without_category_is_uncategorized(self):
        ticket = make_ticket("T001")
        ticket.pop("category")

        report = generate_report([ticket])

        self.assertEqual(report["by_category"]["Uncategorized"], 1)

    def test_invalid_category_is_rejected(self):
        ticket = make_ticket("T001", category="Electricity")

        with self.assertRaises(ValidationError):
            generate_report([ticket])

    def test_print_report_includes_resolution_metrics(self):
        from io import StringIO

        output = StringIO()
        print_report(
            [make_ticket("T001", status="resolved")],
            file=output,
        )

        rendered = output.getvalue()
        self.assertIn("By category:", rendered)
        self.assertIn("Resolved tickets: 1", rendered)
        self.assertIn("Resolution percentage: 100.00%", rendered)


if __name__ == "__main__":
    unittest.main()
