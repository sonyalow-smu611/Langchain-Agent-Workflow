from pathlib import Path

from src.agents.base import get_llm


def run_backend_worker(
    task,
    api_contract,
    schema,
    architecture
):

    llm = get_llm()

    prompt = Path(
        "src/prompts/backend.md"
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

            Database Schema:
            {schema.model_dump_json()}

            Architecture:
            {architecture.model_dump_json()}

            Implement the assigned backend work.
            Return the proposed file changes.
            """
        )
    ])

    return response.content