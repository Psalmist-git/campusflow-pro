"""Engineering Understanding Check for CampusFlow."""

QUESTION_BANK = [
    {
        "id": 1,
        "question": "Why should an unassigned ticket not move to in_progress?",
        "options": {
            "A": "Because tickets cannot be updated",
            "B": "Because a staff member must be assigned before work starts",
            "C": "Because every ticket must be resolved immediately",
            "D": "Because priority cannot be calculated",
        },
        "answer": "B",
    },
    {
        "id": 2,
        "question": "What should the resolution percentage be when there are no tickets?",
        "options": {
            "A": "100%",
            "B": "50%",
            "C": "0%",
            "D": "An error must always occur",
        },
        "answer": "C",
    },
    {
        "id": 3,
        "question": (
            "A search specifies category Network, status open, "
            "and priority critical. How should these filters work?"
        ),
        "options": {
            "A": "Return tickets matching any one filter",
            "B": "Ignore the category filter",
            "C": "Return every open ticket",
            "D": "Return only tickets matching all three filters",
        },
        "answer": "D",
    },
    {
        "id": 4,
        "question": (
            "What should happen when someone adds a follow-up note "
            "to a resolved ticket?"
        ),
        "options": {
            "A": "Reject the note until the ticket is reopened",
            "B": "Delete the ticket",
            "C": "Automatically assign the ticket",
            "D": "Change the ticket priority",
        },
        "answer": "A",
    },
    {
        "id": 5,
        "question": (
            "What should safe JSON loading do when duplicate ticket IDs "
            "are found?"
        ),
        "options": {
            "A": "Silently delete one ticket",
            "B": "Rename the duplicate automatically",
            "C": "Reject the invalid data and preserve existing in-memory tickets",
            "D": "Delete the entire tickets file",
        },
        "answer": "C",
    },
    {
        "id": 6,
        "question": (
            "A pull request changes validation but adds no tests for "
            "invalid input. What is the best review response?"
        ),
        "options": {
            "A": "Approve without testing",
            "B": "Request negative tests and an explanation of the expected behaviour",
            "C": "Delete all existing tests",
            "D": "Merge directly into main",
        },
        "answer": "B",
    },
]


def score_answers(answers, question_bank=QUESTION_BANK):
    """Return the number of correct answers."""
    score = 0

    for question in question_bank:
        question_id = question["id"]
        submitted_answer = answers.get(question_id, "")

        # Ignore unexpected types instead of crashing.
        if not isinstance(submitted_answer, str):
            continue

        if submitted_answer.strip().upper() == question["answer"]:
            score += 1

    return score


def ask_valid_answer(question, input_fn=input, output_fn=print):
    """Ask a question until the user supplies A, B, C, or D."""
    output_fn(f"\nQuestion {question['id']}: {question['question']}")

    for option, text in question["options"].items():
        output_fn(f"  {option}. {text}")

    while True:
        answer = input_fn("Your answer (A/B/C/D): ").strip().upper()

        if answer in question["options"]:
            return answer

        output_fn("Invalid answer. Please enter A, B, C, or D.")


def ask_for_explanation(question_id, input_fn=input, output_fn=print):
    """Ask for a non-empty explanation."""
    while True:
        explanation = input_fn(
            f"Explain your reasoning for Question {question_id}: "
        ).strip()

        if explanation:
            return explanation

        output_fn("Your explanation cannot be empty. Please try again.")


def run_understanding_check(input_fn=input, output_fn=print):
    """Run the understanding check and return answers and explanations."""
    output_fn("\n=== CampusFlow Engineering Understanding Check ===")
    output_fn("Answer all six questions.")

    answers = {}

    for question in QUESTION_BANK:
        answers[question["id"]] = ask_valid_answer(
            question,
            input_fn=input_fn,
            output_fn=output_fn,
        )

    score = score_answers(answers)

    output_fn(f"\nYour score: {score}/{len(QUESTION_BANK)}")

    explanations = {}

    for question_id in (1, 5):
        explanations[question_id] = ask_for_explanation(
            question_id,
            input_fn=input_fn,
            output_fn=output_fn,
        )

    output_fn("\nUnderstanding check completed.")

    return {
        "score": score,
        "answers": answers,
        "explanations": explanations,
    }
