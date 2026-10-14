"""Tests for CampusFlow ticket creation, validation, and assignment."""
import unittest

from campusflow.tickets import (
    ValidationError,
    compute_priority,
    create_ticket,
    find_ticket,
    next_ticket_id,
    normalize_category,
    normalize_urgency,
    parse_affected_users,
    validate_affected_users,
    validate_title,
)
from campusflow.workflow import assign_ticket


class PriorityEngineTests(unittest.TestCase):
    def test_high_urgency_and_many_users_is_critical(self):
        self.assertEqual(compute_priority("high", 10), "critical")

    def test_high_urgency_alone_is_high(self):
        self.assertEqual(compute_priority("high", 1), "high")

    def test_many_users_alone_is_high(self):
        self.assertEqual(compute_priority("low", 10), "high")

    def test_medium_urgency_is_medium(self):
        self.assertEqual(compute_priority("medium", 1), "medium")

    def test_three_users_is_medium(self):
        self.assertEqual(compute_priority("low", 3), "medium")

    def test_low_urgency_and_few_users_is_low(self):
        self.assertEqual(compute_priority("low", 2), "low")


class ValidationTests(unittest.TestCase):
    def test_category_is_normalized(self):
        self.assertEqual(normalize_category(" network "), "Network")

    def test_invalid_category_is_rejected(self):
        with self.assertRaises(ValidationError):
            normalize_category("Electricity")

    def test_urgency_is_normalized(self):
        self.assertEqual(normalize_urgency(" HIGH "), "high")

    def test_invalid_urgency_is_rejected(self):
        with self.assertRaises(ValidationError):
            normalize_urgency("urgent")

    def test_title_is_trimmed(self):
        self.assertEqual(validate_title("  Broken projector  "), "Broken projector")

    def test_blank_title_is_rejected(self):
        with self.assertRaises(ValidationError):
            validate_title("   ")

    def test_affected_users_must_be_positive_integer(self):
        for value in (0, -1, 1.5, True, "5", None):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    validate_affected_users(value)


class CreateTicketTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []

    def test_creates_ticket_with_calculated_priority(self):
        ticket = create_ticket(
            self.tickets,
            title="Wi-Fi down",
            category="Network",
            urgency="high",
            affected_users=15,
        )
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["affected_users"], 15)

    def test_new_ticket_category_and_urgency_are_normalized(self):
        ticket = create_ticket(
            self.tickets,
            title="  Software issue  ",
            category=" software ",
            urgency=" MEDIUM ",
            affected_users=1,
        )
        self.assertEqual(ticket["title"], "Software issue")
        self.assertEqual(ticket["category"], "Software")
        self.assertEqual(ticket["urgency"], "medium")

    def test_invalid_category_creation_does_not_change_ticket_list(self):
        with self.assertRaises(ValidationError):
            create_ticket(
                self.tickets,
                title="Power failure",
                category="Electricity",
                urgency="high",
                affected_users=5,
            )
        self.assertEqual(self.tickets, [])

    def test_invalid_creation_does_not_change_ticket_list(self):
        with self.assertRaises(ValidationError):
            create_ticket(
                self.tickets,
                title="Wi-Fi down",
                category="Network",
                urgency="urgent",
                affected_users=5,
            )
        self.assertEqual(self.tickets, [])


class FindAndAssignTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(
            self.tickets,
            title="Broken projector",
            category="Hardware",
            urgency="medium",
            affected_users=4,
        )

    def test_next_ticket_id_uses_numeric_order(self):
        tickets = [{"id": "T009"}, {"id": "T010"}, {"id": "T002"}]
        self.assertEqual(next_ticket_id(tickets), "T011")

    def test_find_ticket_is_case_insensitive(self):
        self.assertIs(find_ticket(self.tickets, "t001"), self.tickets[0])

    def test_find_missing_ticket_returns_none(self):
        self.assertIsNone(find_ticket(self.tickets, "T999"))

    def test_assign_ticket_updates_staff_name(self):
        assigned = assign_ticket(self.tickets, "T001", "  Ada  ")
        self.assertEqual(assigned["assigned_to"], "Ada")

    def test_assign_unknown_ticket_is_rejected(self):
        with self.assertRaises(ValidationError):
            assign_ticket(self.tickets, "T999", "Ada")

    def test_blank_staff_name_is_rejected(self):
        with self.assertRaises(ValidationError):
            assign_ticket(self.tickets, "T001", "  ")


class ParseAffectedUsersTests(unittest.TestCase):
    def test_valid_text_is_converted(self):
        self.assertEqual(parse_affected_users(" 15 "), 15)

    def test_text_decimal_zero_and_negative_are_rejected(self):
        for bad in ("abc", "2.5", "0", "-3", ""):
            with self.subTest(bad=bad):
                with self.assertRaises(ValidationError):
                    parse_affected_users(bad)


if __name__ == "__main__":
    unittest.main()
