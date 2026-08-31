"""
Adapters between LangGraph nodes and the plain-Python agent functions in
src/agents/ — each node pulls what it needs from WorkflowState and returns a
partial-state update.

Run: not run directly — imported by graph.py.

Learn: the thin "node" pattern — nodes don't contain logic themselves, they
just wire state in and out of an existing function.
"""

from vibecoder.src.agents.director import run_director
from vibecoder.src.agents.architect import run_architect


def director_node(state):

    product_spec, task_graph = run_director(
        state["user_request"]
    )

    return {
        "product_spec": product_spec,
        "task_graph": task_graph
    }


def architect_node(state):

    blueprint, schema, api_contract = run_architect(
        state["product_spec"],
        state["task_graph"]
    )

    return {
        "blueprint": blueprint,
        "schema_spec": schema,
        "api_contract": api_contract
    }