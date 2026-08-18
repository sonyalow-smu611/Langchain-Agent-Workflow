from src.agents.director import run_director
from src.agents.architect import run_architect


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