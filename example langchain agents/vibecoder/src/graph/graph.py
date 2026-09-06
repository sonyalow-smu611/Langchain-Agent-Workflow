"""
Assembles and runs the LangGraph workflow. Currently wires
director -> architect -> END; the frontend/backend/qa/repair loop described
in the README isn't connected here yet (routing.py's route_after_qa shows
how that loop would plug in).

Run: `python -m vibecoder.src.graph.graph` from the repo root (needs
     OPENAI_API_KEY; makes several real LLM calls with structured output).

Learn: StateGraph(WorkflowState), add_node/add_edge, START/END, and
.compile() + .invoke() to run the whole graph on one input.
"""

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from vibecoder.src.graph.state import WorkflowState
from vibecoder.src.graph.nodes import (
    director_node,
    architect_node
)


def build_graph():

    builder = StateGraph(
        WorkflowState
    )

    builder.add_node(
        "director",
        director_node
    )

    builder.add_node(
        "architect",
        architect_node
    )

    builder.add_edge(
        START,
        "director"
    )

    builder.add_edge(
        "director",
        "architect"
    )

    builder.add_edge(
        "architect",
        END
    )

    return builder.compile()


if __name__ == "__main__":

    graph = build_graph()

    result = graph.invoke({
        "user_request": """
        Build a simple task management application.
        Users should be able to create, complete,
        and delete tasks.
        """
    })

    print(result)