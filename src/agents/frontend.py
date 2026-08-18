from pathlib import Path

from src.agents.base import get_llm


def run_frontend_worker(
    task,
    api_contract,
    architecture
):

    llm = get_llm()

    prompt = Path(
        "src/prompts/frontend.md"
    ).read_text()

    response = llm.invoke([
        ("system", prompt),
        (
            "human",
            f"""
            Task:
            {task.model_dump_json()}

            API Contract:
            {api_contract.model_dump_json()}

            Architecture:
            {architecture.model_dump_json()}

            Implement the assigned frontend work.
            Return the proposed file changes.
            """
        )
    ])

    return response.content