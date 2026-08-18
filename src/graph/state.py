from typing import TypedDict

from src.schemas.product import ProductSpec
from src.schemas.architecture import BlueprintSpec
from src.schemas.contracts import APIContract, SchemaSpec
from src.schemas.tasks import TaskGraph
from src.schemas.testing import TestReport, RepairTicket


class WorkflowState(TypedDict, total=False):

    # Original user request
    user_request: str

    # Planning
    product_spec: ProductSpec
    blueprint: BlueprintSpec

    # Technical contracts
    api_contract: APIContract
    schema_spec: SchemaSpec

    # Execution
    task_graph: TaskGraph

    # Generated project
    files: dict[str, str]

    # Verification
    test_report: TestReport

    # Repair
    repair_tickets: list[RepairTicket]

    # Workflow control
    iteration: int