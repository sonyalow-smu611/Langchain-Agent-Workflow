"""
Second agent: takes the director's ProductSpec + TaskGraph and produces three
structured design artifacts — BlueprintSpec, SchemaSpec, APIContract.

Run: not run directly — called by src/graph/nodes.py's architect_node.

Learn: calling .with_structured_output() three times against the same
prompt/context to get three independent typed outputs, and
model_dump_json() to serialize Pydantic objects into a prompt.
"""

from pathlib import Path

from vibecoder.src.agents.base import get_llm
from vibecoder.src.schemas.architecture import BlueprintSpec
from vibecoder.src.schemas.contracts import APIContract, SchemaSpec


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