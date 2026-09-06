"""
Backend worker agent — the backend counterpart to frontend.py. Given one
Task + the API contract + DB schema + architecture, implements that backend
slice.

Run: not run directly — same pattern as frontend.py, just with a schema arg
     too.

Learn: worker agents share one pattern — invoke with rich JSON context,
return free-text file changes. Compare directly against frontend.py.
"""

from pathlib import Path

from vibecoder.src.agents.base import get_llm


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