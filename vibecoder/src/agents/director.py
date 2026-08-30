from pathlib import Path

from vibecoder.src.agents.base import get_llm
from vibecoder.src.schemas.product import ProductSpec
from vibecoder.src.schemas.tasks import TaskGraph


def build_director():

    llm = get_llm()

    product_model = llm.with_structured_output(
        ProductSpec
    )

    task_model = llm.with_structured_output(
        TaskGraph
    )

    prompt = Path(
        "src/prompts/director.md"
    ).read_text()

    return product_model, task_model, prompt


def run_director(user_request: str):

    product_model, task_model, prompt = build_director()

    product_spec = product_model.invoke([
        ("system", prompt),
        (
            "human",
            f"""
            User request:

            {user_request}

            Extract the product specification.
            """
        )
    ])

    task_graph = task_model.invoke([
        ("system", prompt),
        (
            "human",
            f"""
            Product specification:

            {product_spec.model_dump_json()}

            Create the execution task graph.
            """
        )
    ])

    return product_spec, task_graph