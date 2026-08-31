"""
The one shared state dict threaded through the whole LangGraph workflow —
every node reads from and writes back into this TypedDict.

Run: not run directly — imported by graph.py and nodes.py.

Learn: LangGraph's TypedDict(total=False) state pattern, where each node
only needs to return the keys it updates, not the whole state.
"""

from typing import TypedDict

from vibecoder.src.schemas.product import ProductSpec
from vibecoder.src.schemas.architecture import BlueprintSpec
from vibecoder.src.schemas.contracts import APIContract, SchemaSpec
from vibecoder.src.schemas.tasks import TaskGraph
from vibecoder.src.schemas.testing import TestReport, RepairTicket


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