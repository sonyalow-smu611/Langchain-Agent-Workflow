"""
Example pytest test for a Pydantic schema — construct a ProductSpec and
assert a field round-trips correctly.

Run: `cd vibecoder && pytest` (or `pytest vibecoder/tests` from the repo
     root).

Learn: testing Pydantic models is just testing plain Python objects — no
mocking an LLM needed, since the schema itself has no external dependencies.
"""

from vibecoder.src.schemas.product import ProductSpec


def test_product_spec():

    spec = ProductSpec(
        goal="Build a todo app",
        target_users=["students"],
        mvp_features=[
            "create tasks",
            "complete tasks"
        ],
        acceptance_criteria=[
            "users can create tasks"
        ]
    )

    assert spec.goal == "Build a todo app"