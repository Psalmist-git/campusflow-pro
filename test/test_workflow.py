import unittest

from campusflow.workflow import (
    assign_ticket,
    update_status,
    get_work_queue,
)
from campusflow.reports import generate_report


def make_ticket(
    ticket_id="T001",
    status="open",
    priority="high",
    assigned_to=None,
):
    return {
        "id": ticket_id,
        "title": "Test ticket",
        "category": "Software",
        "urgency": "medium",
        "affected_users": 3,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


class TestTicketAssignment(unittest.TestCase):
    def test_assign_ticket(self):
        tickets = [make_ticket()]
        result = assign_ticket(tickets, "T001", "  John  ")
        self.assertEqual(result["assigned_to"], "John")

    def test_unknown_ticket_is_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket([make_ticket()], "T999", "John")

    def test_blank_staff_name_is_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket([make_ticket()], "T001", "   ")

    def test_resolved_ticket_cannot_be_assigned(self):
        tickets = [make_ticket(status="resolved", assigned_to="John")]
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "Mary")


class TestCaseInsensitiveIds(unittest.TestCase):
    def test_lowercase_id_is_accepted_for_assign_and_status(self):
        tickets = [make_ticket()]
        assign_ticket(tickets, "t001", "Ada")
        update_status(tickets, "t001", "in_progress")
        self.assertEqual(tickets[0]["status"], "in_progress")
        self.assertEqual(tickets[0]["assigned_to"], "Ada")


class TestTicketWorkflow(unittest.TestCase):
    def test_unassigned_ticket_cannot_start(self):
        with self.assertRaises(ValueError):
            update_status([make_ticket()], "T001", "in_progress")

    def test_assigned_ticket_can_start(self):
        tickets = [make_ticket(assigned_to="John")]
        update_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "in_progress")

    def test_in_progress_ticket_can_be_resolved(self):
        tickets = [make_ticket(status="in_progress", assigned_to="John")]
        update_status(tickets, "T001", "resolved")
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_resolved_ticket_can_be_reopened(self):
        tickets = [make_ticket(status="resolved", assigned_to="John")]
        update_status(tickets, "T001", "open")
        self.assertEqual(tickets[0]["status"], "open")

    def test_invalid_transition_is_rejected(self):
        with self.assertRaises(ValueError):
            update_status([make_ticket()], "T001", "resolved")

    def test_unknown_status_is_rejected(self):
        with self.assertRaises(ValueError):
            update_status([make_ticket()], "T001", "waiting")


class TestWorkQueue(unittest.TestCase):
    def test_priority_then_numeric_id_order(self):
        tickets = [
            make_ticket("T003", priority="high"),
            make_ticket("T010", priority="critical"),
            make_ticket("T002", priority="high"),
            make_ticket("T004", priority="low"),
        ]
        result = get_work_queue(tickets)
        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T010", "T002", "T003", "T004"],
        )

    def test_resolved_tickets_are_excluded(self):
        tickets = [
            make_ticket("T001", priority="critical"),
            make_ticket("T002", status="resolved", priority="high"),
        ]
        self.assertEqual(
            [ticket["id"] for ticket in get_work_queue(tickets)],
            ["T001"],
        )

    def test_empty_queue(self):
        self.assertEqual(get_work_queue([]), [])


class TestReports(unittest.TestCase):
    def test_report_counts(self):
        tickets = [
            make_ticket("T001", priority="critical"),
            make_ticket("T002", status="in_progress", priority="high"),
            make_ticket("T003", status="resolved", priority="medium"),
            make_ticket("T004", priority="low"),
        ]
        report = generate_report(tickets)
        self.assertEqual(report["total_tickets"], 4)
        self.assertEqual(report["by_status"], {
            "open": 2, "in_progress": 1, "resolved": 1
        })
        self.assertEqual(report["by_priority"], {
            "critical": 1, "high": 1, "medium": 1, "low": 1
        })

    def test_empty_report_has_zero_counts(self):
        report = generate_report([])
        self.assertEqual(report["total_tickets"], 0)
        self.assertTrue(all(v == 0 for v in report["by_status"].values()))
        self.assertTrue(all(v == 0 for v in report["by_priority"].values()))


if __name__ == "__main__":
    unittest.main()