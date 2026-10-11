"""
Shared fixtures for the vibecoder end-to-end tests.

Run: `pytest e2e` from vibecoder/ (offline + live), `pytest e2e -m "not live"`
     for the offline tests only. Live tests use OPENAI_API_KEY from
     vibecoder/.env and make real OpenAI calls.

Learn: importing a script by file path with importlib, and swapping the LLM
for a fake so graph wiring can be tested without network calls.
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
from langchain_core.messages import AIMessage

VIBECODER_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = VIBECODER_ROOT / "run_vibecoder" / "vibecoder_langchain.py"

# qa_node shells out to a bare `pytest`. If that inner run collected this
# folder it would start the workflow again, so the inner run ignores e2e/.
if os.environ.get("VIBECODER_E2E_ACTIVE"):
    collect_ignore_glob = ["*"]
os.environ["VIBECODER_E2E_ACTIVE"] = "1"

load_dotenv(VIBECODER_ROOT / ".env")

# HITL=1 makes human_review_node call input(), which would hang a test run.
os.environ["HITL"] = "0"

from vibecoder.src.schemas.architecture import ArchitectureDecision, BlueprintSpec
from vibecoder.src.schemas.contracts import (
    APIContract,
    APIEndpoint,
    DatabaseModel,
    FieldSpec,
    SchemaSpec,
)
from vibecoder.src.schemas.product import ProductSpec
from vibecoder.src.schemas.tasks import Task, TaskGraph
from vibecoder.src.schemas.testing import TestFailure, TestReport

AGENT_MODULES = ["architect", "backend", "director", "frontend", "qa_repair"]


def pytest_collection_modifyitems(config, items):
    if os.environ.get("OPENAI_API_KEY"):
        return

    skip_live = pytest.mark.skip(reason="OPENAI_API_KEY is not set in vibecoder/.env")

    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


def canned_outputs() -> dict:
    """One valid instance of every schema the agents ask the LLM for."""

    return {
        ProductSpec: ProductSpec(
            goal="Build a todo app",
            target_users=["students"],
            mvp_features=["create tasks"],
            acceptance_criteria=["users can create tasks"],
        ),
        TaskGraph: TaskGraph(
            tasks=[
                Task(id="T1", owner="backend", description="Build the task API"),
                Task(
                    id="T2",
                    owner="frontend",
                    description="Build the task list UI",
                    dependencies=["T1"],
                ),
            ]
        ),
        BlueprintSpec: BlueprintSpec(
            project_structure=["backend/", "frontend/"],
            architecture_summary="React frontend talking to a FastAPI backend.",
            decisions=[
                ArchitectureDecision(
                    technology="SQLite",
                    decision="Use SQLite for storage",
                    rationale="Simple persistent storage",
                )
            ],
            frontend_requirements=["task list"],
            backend_requirements=["task CRUD"],
        ),
        SchemaSpec: SchemaSpec(
            models=[
                DatabaseModel(
                    name="Task",
                    fields=[
                        FieldSpec(name="id", type="int"),
                        FieldSpec(name="title", type="str"),
                    ],
                )
            ]
        ),
        APIContract: APIContract(
            endpoints=[
                APIEndpoint(method="GET", path="/tasks", description="List tasks")
            ]
        ),
    }


class FakeStructuredLLM:

    def __init__(self, parent, schema):
        self.parent = parent
        self.schema = schema

    def invoke(self, messages):
        self.parent.calls.append((self.schema.__name__, messages))
        return self.parent.outputs[self.schema]


class FakeLLM:
    """Stands in for ChatOpenAI: canned structured output, canned text."""

    model_name = "fake-llm"

    def __init__(self):
        self.outputs = canned_outputs()
        self.calls = []

    def with_structured_output(self, schema):
        return FakeStructuredLLM(self, schema)

    def invoke(self, messages):
        self.calls.append(("text", messages))
        return AIMessage(content=f"fake response {len(self.calls)}")

    def call_names(self) -> list[str]:
        return [name for name, _ in self.calls]


@pytest.fixture(scope="session")
def runner():
    """The workshop script, imported as a module without running it."""

    spec = importlib.util.spec_from_file_location("vibecoder_runner", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def in_vibecoder_root(monkeypatch):
    """Agents load prompts from relative paths, so pin cwd like the runner does."""

    monkeypatch.chdir(VIBECODER_ROOT)


@pytest.fixture
def fake_llm(monkeypatch, runner):
    llm = FakeLLM()

    for name in AGENT_MODULES:
        monkeypatch.setattr(f"vibecoder.src.agents.{name}.get_llm", lambda: llm)

    monkeypatch.setattr(runner, "get_llm", lambda: llm)
    return llm


@pytest.fixture
def passing_report():
    return TestReport(status="passed", tests_run=2, tests_passed=2, tests_failed=0)


@pytest.fixture
def failing_report():
    return TestReport(
        status="failed",
        tests_run=2,
        tests_passed=1,
        tests_failed=1,
        failures=[TestFailure(test_name="test_api", error="AssertionError: 500 != 200")],
    )


@pytest.fixture
def venv_on_path(monkeypatch):
    """Mimic an activated venv so qa_node's bare `pytest` resolves."""

    bin_dir = str(Path(sys.executable).parent)
    monkeypatch.setenv("PATH", bin_dir + os.pathsep + os.environ.get("PATH", ""))
