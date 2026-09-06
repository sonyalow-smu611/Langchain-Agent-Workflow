"""
Vibecoder LangChain workshop script.

This file is a readable, runnable walkthrough of the vibecoder multi-agent
coding workflow. It starts with a plain user request, sends that request
through LangChain agents that produce structured planning objects, wires those
agents into a LangGraph workflow, and shows where frontend, backend, QA, repair,
and human review steps fit. The production source code lives in ../src; this
script imports those modules and adds extra comments so readers can follow the
flow without jumping between files first.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.runnables import RunnableParallel
from langgraph.graph import END, START, StateGraph


# The runner file lives in vibecoder/run_vibecoder, but the project modules
# expect the current working directory to be vibecoder/ because prompts are
# loaded from paths such as "src/prompts/director.md".
VIBECODER_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_AGENTS_ROOT = VIBECODER_ROOT.parent
os.chdir(VIBECODER_ROOT)

# Load the vibecoder-local .env file before importing agent modules that create
# OpenAI clients. This keeps setup contained inside this example folder.
load_dotenv(VIBECODER_ROOT / ".env")

# Add the parent folder to sys.path so "import vibecoder.src..." works when this
# file is run directly with: python run_vibecoder/vibecoder_langchain.py
sys.path.insert(0, str(EXAMPLE_AGENTS_ROOT))

from vibecoder.src.agents.architect import run_architect
from vibecoder.src.agents.backend import run_backend_worker
from vibecoder.src.agents.base import get_llm
from vibecoder.src.agents.director import run_director
from vibecoder.src.agents.frontend import run_frontend_worker
from vibecoder.src.agents.qa_repair import run_qa, run_repair
from vibecoder.src.graph.routing import route_after_qa
from vibecoder.src.graph.state import WorkflowState
from vibecoder.src.schemas.product import ProductSpec
from vibecoder.src.schemas.testing import TestReport
from vibecoder.src.tools.filesystem import list_files, read_file, write_file
from vibecoder.src.tools.testing import run_tests


# 01. What are we building?
# This is the one product request that flows through the whole workshop.
USER_REQUEST = """
Build a simple task management application.
Users should be able to create, view, complete, and delete tasks.
The application should have a frontend, backend API, persistent storage,
basic validation, and tests for core functionality.
"""


def show_step(title: str) -> None:
    """Print a small section header so CLI output is easy to scan."""

    print(f"\n=== {title} ===")


def step_02_llm():
    """Create the shared chat model used by the vibecoder agents."""

    # get_llm() centralizes model name, temperature, and .env loading for every
    # agent. MODEL_NAME is optional; base.py defaults to gpt-4.1-mini.
    llm = get_llm()
    print(f"Loaded LLM: {llm.model_name}")
    return llm


def step_03_agent(llm) -> str:
    """Run the smallest possible LangChain agent-style call."""

    # This direct call is intentionally simple: one system message gives the
    # role, and one human message asks for a compact product interpretation.
    response = llm.invoke(
        [
            ("system", "You are a practical senior software planner."),
            ("human", f"Summarize this build request in one sentence:\n{USER_REQUEST}"),
        ]
    )

    # ChatOpenAI returns an AIMessage, so .content contains the generated text.
    print(response.content)
    return response.content


def step_04_tools() -> None:
    """Demonstrate the local filesystem tools agents can call."""

    # The tool layer writes only inside vibecoder/workspace, which keeps demo
    # file operations away from source files.
    write_file("workshop_note.txt", "Vibecoder tools can write workspace files.")

    # Reading the file back proves the write path and read path agree.
    content = read_file("workshop_note.txt")
    print(f"Read back: {content}")

    # list_files() gives agents a simple inventory of generated workspace files.
    print(f"Workspace files: {list_files()}")


def step_05_structured_output() -> ProductSpec:
    """Ask the LLM for typed JSON that matches the ProductSpec schema."""

    # LangChain's with_structured_output() makes the model return a Pydantic
    # object instead of free text. This is the same pattern director.py uses.
    product_model = get_llm().with_structured_output(ProductSpec)

    # The field descriptions in ProductSpec guide the model toward the expected
    # goal, users, MVP features, out-of-scope items, and acceptance criteria.
    product_spec = product_model.invoke(
        [
            ("system", "Extract a concise ProductSpec from the user's request."),
            ("human", USER_REQUEST),
        ]
    )

    print(product_spec.model_dump_json(indent=2))
    return product_spec


def step_06_state(product_spec: ProductSpec) -> WorkflowState:
    """Create the initial shared LangGraph state dictionary."""

    # WorkflowState is a TypedDict. Each graph node receives this state and
    # returns only the keys it wants to add or update.
    state: WorkflowState = {
        "user_request": USER_REQUEST,
        "product_spec": product_spec,
        "iteration": 0,
    }

    print(state)
    return state


def director_node(state: WorkflowState) -> WorkflowState:
    """Turn the raw request into a ProductSpec and TaskGraph."""

    # run_director() performs two structured LLM calls: first for product
    # planning, then for task planning.
    product_spec, task_graph = run_director(state["user_request"])

    # Returning a partial state update is the normal LangGraph node pattern.
    return {
        "product_spec": product_spec,
        "task_graph": task_graph,
    }


def architect_node(state: WorkflowState) -> WorkflowState:
    """Turn product and task planning into technical contracts."""

    # run_architect() creates the blueprint, database schema, and API contract
    # that later frontend and backend workers use as shared instructions.
    blueprint, schema_spec, api_contract = run_architect(
        state["product_spec"],
        state["task_graph"],
    )

    return {
        "blueprint": blueprint,
        "schema_spec": schema_spec,
        "api_contract": api_contract,
    }


def worker_node(state: WorkflowState) -> WorkflowState:
    """Run frontend and backend workers for the first matching tasks."""

    # The director may produce several tasks. This beginner script picks one
    # frontend task and one backend task so the worker step stays readable.
    frontend_task = next(
        (task for task in state["task_graph"].tasks if task.owner == "frontend"),
        None,
    )
    backend_task = next(
        (task for task in state["task_graph"].tasks if task.owner == "backend"),
        None,
    )

    # If the planner did not create both task types, return an explanatory
    # artifact instead of crashing the workshop run with StopIteration.
    if frontend_task is None or backend_task is None:
        return {
            "files": {
                "worker_warning.md": (
                    "The task graph did not contain both frontend and backend "
                    "tasks, so worker agents were skipped."
                )
            }
        }

    # RunnableParallel runs independent branches with the same input. Here each
    # branch calls a different worker agent with the same architecture context.
    workers = RunnableParallel(
        frontend=lambda _: run_frontend_worker(
            frontend_task,
            state["api_contract"],
            state["blueprint"],
        ),
        backend=lambda _: run_backend_worker(
            backend_task,
            state["api_contract"],
            state["schema_spec"],
            state["blueprint"],
        ),
    )

    # The worker agents return proposed code changes as text. They are saved in
    # state["files"] so QA or repair steps can inspect them later.
    changes = workers.invoke({})

    return {
        "files": {
            "frontend_proposal.md": changes["frontend"],
            "backend_proposal.md": changes["backend"],
        }
    }


def qa_node(state: WorkflowState) -> WorkflowState:
    """Run pytest and convert failures into repair tickets."""

    # run_tests() shells out to pytest and wraps the result in a TestReport.
    test_report: TestReport = run_tests()

    # run_qa() is deterministic Python: it maps failed tests into RepairTicket
    # objects that the repair agent can work from.
    qa_result = run_qa(test_report)

    return {
        "test_report": test_report,
        "repair_tickets": qa_result["repair_tickets"],
    }


def human_review_node(state: WorkflowState) -> WorkflowState:
    """Optional human-in-the-loop checkpoint before repair."""

    # Set HITL=1 to pause before repair. By default the workshop keeps running
    # without waiting for keyboard input, which is better for automated demos.
    if os.getenv("HITL") == "1" and state.get("repair_tickets"):
        input("Repair tickets were created. Press Enter to let repair continue.")

    # No state changes are required; this node exists to show where approval or
    # review would be inserted in a real agent workflow.
    return {}


def repair_node(state: WorkflowState) -> WorkflowState:
    """Ask the repair agent for a focused fix when QA fails."""

    # If QA passed or produced no tickets, there is nothing to repair.
    if not state.get("repair_tickets"):
        return {}

    # This workshop repairs the first ticket only. The loop can come back here
    # after QA if more attempts are needed.
    ticket = state["repair_tickets"][0]
    repair_text = run_repair(ticket, state.get("files", {}))

    # Keep repair output as another proposed file so the example avoids parsing
    # arbitrary LLM-generated patches.
    files = dict(state.get("files", {}))
    files[f"repair_{ticket.issue_id}.md"] = repair_text

    return {
        "files": files,
        "iteration": state.get("iteration", 0) + 1,
    }


def build_workshop_graph():
    """Build the LangGraph workflow used by this workshop file."""

    # StateGraph declares the shape of the shared state passed between nodes.
    builder = StateGraph(WorkflowState)

    # 07. Director -> Architect.
    # The first two nodes turn the request into product and technical plans.
    builder.add_node("director", director_node)
    builder.add_node("architect", architect_node)

    # 08. Parallel FE + BE.
    # The worker node uses RunnableParallel internally for independent workers.
    builder.add_node("workers", worker_node)

    # 09. QA.
    # QA runs tests and creates repair tickets from any failures.
    builder.add_node("qa", qa_node)

    # 11. Repair loop.
    # Repair reads tickets and adds a proposed fix back into state["files"].
    builder.add_node("repair", repair_node)

    # 12. HITL.
    # Human review is optional and controlled by HITL=1.
    builder.add_node("human_review", human_review_node)

    # The linear edges wire the happy path from request to QA.
    builder.add_edge(START, "director")
    builder.add_edge("director", "architect")
    builder.add_edge("architect", "workers")
    builder.add_edge("workers", "qa")

    # 10. Conditional routing.
    # route_after_qa() returns "end" when tests pass or attempts are exhausted;
    # otherwise it routes to repair.
    builder.add_conditional_edges(
        "qa",
        route_after_qa,
        {
            "end": END,
            "repair": "human_review",
        },
    )

    # Failed QA enters optional review, then repair, then loops back to QA.
    builder.add_edge("human_review", "repair")
    builder.add_edge("repair", "qa")

    # 13. Full workflow.
    # compile() validates the graph and returns an object with invoke().
    return builder.compile()


def run_workshop() -> WorkflowState:
    """Run the complete workshop progression from a single user request."""

    show_step("01. What are we building?")
    print(USER_REQUEST.strip())

    show_step("02. LLM")
    llm = step_02_llm()

    show_step("03. Agent")
    step_03_agent(llm)

    show_step("04. Tools")
    step_04_tools()

    show_step("05. Structured output")
    product_spec = step_05_structured_output()

    show_step("06. State")
    step_06_state(product_spec)

    show_step("07-13. Full LangGraph workflow")
    graph = build_workshop_graph()

    # The graph starts from the raw request. Every later object is produced by
    # a graph node and merged into the shared WorkflowState.
    result = graph.invoke(
        {
            "user_request": USER_REQUEST,
            "iteration": 0,
        }
    )

    # Printing keys gives a compact summary without dumping long LLM outputs.
    print(f"Final state keys: {sorted(result.keys())}")
    print(f"QA status: {result['test_report'].status}")
    print(f"Repair attempts: {result.get('iteration', 0)}")

    return result


if __name__ == "__main__":
    # Running this file makes real OpenAI calls. Make sure OPENAI_API_KEY is set
    # in vibecoder/.env before using the workshop script.
    run_workshop()
