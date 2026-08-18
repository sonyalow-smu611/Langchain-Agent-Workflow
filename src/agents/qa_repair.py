from pathlib import Path

from src.agents.base import get_llm
from src.schemas.testing import RepairTicket


def run_qa(test_report):

    if test_report.status == "passed":

        return {
            "status": "passed",
            "repair_tickets": []
        }

    tickets = []

    for index, failure in enumerate(
        test_report.failures
    ):

        tickets.append(
            RepairTicket(
                issue_id=f"BUG-{index + 1}",
                description=failure.error,
                file=failure.file,
                error=failure.error,
                expected_behavior="Test should pass.",
                suggested_owner="backend",
                attempt=1
            )
        )

    return {
        "status": "failed",
        "repair_tickets": tickets
    }


def run_repair(
    repair_ticket,
    files
):

    llm = get_llm()

    prompt = Path(
        "src/prompts/qa_repair.md"
    ).read_text()

    response = llm.invoke([
        ("system", prompt),
        (
            "human",
            f"""
            Repair ticket:

            {repair_ticket.model_dump_json()}

            Relevant files:

            {files}

            Produce the smallest safe fix.
            """
        )
    ])

    return response.content