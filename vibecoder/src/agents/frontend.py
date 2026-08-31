"""
Frontend worker agent: given one Task + the API contract + architecture, asks
the LLM to implement that slice of the frontend and return proposed file
changes.

Run: not run directly — called from a graph node (not yet wired into
     src/graph/graph.py; see routing.py for how it would join the loop).

Learn: a plain llm.invoke() (no structured output) is used here instead of
.with_structured_output() — free-text code/diffs are the desired output,
not JSON.
"""

from pathlib import Path

from vibecoder.src.agents.base import get_llm


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