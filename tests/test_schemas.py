from src.schemas.product import ProductSpec


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