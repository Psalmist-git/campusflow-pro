import unittest

from campusflow.understanding_check import (
    QUESTION_BANK,
    ask_valid_answer,
    run_understanding_check,
    score_answers,
)


class TestUnderstandingCheck(unittest.TestCase):

    def test_all_correct_answers_score_six(self):
        answers = {
            question["id"]: question["answer"]
            for question in QUESTION_BANK
        }
        self.assertEqual(score_answers(answers), 6)

    def test_all_wrong_answers_score_zero(self):
        answers = {
            question["id"]: (
                "B" if question["answer"] != "B" else "A"
            )
            for question in QUESTION_BANK
        }
        self.assertEqual(score_answers(answers), 0)

    def test_missing_answer_does_not_earn_a_point(self):
        self.assertEqual(score_answers({}), 0)

    def test_lowercase_answers_are_accepted(self):
        answers = {
            question["id"]: question["answer"].lower()
            for question in QUESTION_BANK
        }
        self.assertEqual(score_answers(answers), 6)

    def test_question_bank_has_six_questions(self):
        self.assertEqual(len(QUESTION_BANK), 6)

    def test_each_question_has_four_options(self):
        for question in QUESTION_BANK:
            with self.subTest(question=question["id"]):
                self.assertEqual(len(question["options"]), 4)

    def test_invalid_answer_is_rejected_and_reprompted(self):
        responses = iter(["X", "B"])
        messages = []

        answer = ask_valid_answer(
            QUESTION_BANK[0],
            input_fn=lambda prompt: next(responses),
            output_fn=lambda message: messages.append(message),
        )

        self.assertEqual(answer, "B")
        self.assertGreaterEqual(len(messages), 1)

    def test_check_collects_two_explanations(self):
        responses = [
            question["answer"] for question in QUESTION_BANK
        ]
        responses.extend([
            "An unassigned ticket must be assigned before work starts.",
            "Duplicate IDs could cause tickets to be confused.",
        ])

        supplied_responses = []

        def fake_input(prompt):
            response = responses.pop(0)
            supplied_responses.append(response)
            return response

        run_understanding_check(
            input_fn=fake_input,
            output_fn=lambda message: None,
        )

        self.assertEqual(len(supplied_responses), 8)
        self.assertEqual(len(responses), 0)

    def test_non_string_answer_does_not_crash_or_earn_point(self):
        answers = {
            1: None,
            2: "C",
        }
        self.assertEqual(score_answers(answers), 1)

    def test_integer_answer_does_not_crash_or_earn_point(self):
        answers = {
            1: 123,
        }
        self.assertEqual(score_answers(answers), 0)


if __name__ == "__main__":
    unittest.main()
