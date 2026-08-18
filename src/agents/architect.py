from pathlib import Path

from src.agents.base import get_llm
from src.schemas.architecture import BlueprintSpec
from src.schemas.contracts import APIContract, SchemaSpec


def run_architect(
    product_spec,
    task_graph
):

    llm = get_llm()

    blueprint_model = llm.with_structured_output(
        BlueprintSpec
    )

    schema_model = llm.with_structured_output(
        SchemaSpec
    )

    api_model = llm.with_structured_output(
        APIContract
    )

    prompt = Path(
        "src/prompts/architect.md"
    ).read_text()

    context = f"""
    Product specification:
    {product_spec.model_dump_json()}

    Task graph:
    {task_graph.model_dump_json()}
    """

    blueprint = blueprint_model.invoke([
        ("system", prompt),
        ("human", context)
    ])

    schema = schema_model.invoke([
        ("system", prompt),
        ("human", context)
    ])

    api_contract = api_model.invoke([
        ("system", prompt),
        ("human", context)
    ])

    return blueprint, schema, api_contract