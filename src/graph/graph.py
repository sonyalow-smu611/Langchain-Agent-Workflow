from langgraph.graph import (
    StateGraph,
    START,
    END
)

from src.graph.state import WorkflowState
from src.graph.nodes import (
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