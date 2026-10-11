"""
End-to-end tests that make real OpenAI calls with the key in vibecoder/.env.

Run: `pytest e2e -m live` from vibecoder/. Skipped when OPENAI_API_KEY is
     missing. A full run costs a few cents on gpt-4.1-mini.

Learn: testing each structured-output schema on its own pinpoints which
schema the provider rejects, instead of only seeing the whole graph fail.
"""

import os
import subprocess
import sys

import pytest

from vibecoder.src.agents.base import get_llm
from vibecoder.src.agents.director import run_director
from vibecoder.src.graph.graph import build_graph
from vibecoder.src.schemas.architecture import BlueprintSpec
from vibecoder.src.schemas.contracts import APIContract, SchemaSpec
from vibecoder.src.schemas.product import ProductSpec
from vibecoder.src.schemas.tasks import TaskGraph

from conftest import RUNNER_PATH, VIBECODER_ROOT

pytestmark = pytest.mark.live

REQUEST = """
Build a simple task management application.
Users should be able to create, view, complete, and delete tasks.
The application should have a frontend and a backend API.
"""


def test_llm_responds():

    response = get_llm().invoke("Reply with the single word: ready")

    assert response.content.strip()


@pytest.mark.parametrize(
    "schema",
    [ProductSpec, TaskGraph, BlueprintSpec, SchemaSpec, APIContract],
    ids=lambda schema: schema.__name__,
)
def test_schema_works_as_structured_output(schema):

    result = get_llm().with_structured_output(schema).invoke(
        [
            ("system", f"Produce a small, realistic {schema.__name__}."),
            ("human", REQUEST),
        ]
    )

    assert isinstance(result, schema)


def test_director_plans_frontend_and_backend_tasks():

    product_spec, task_graph = run_director(REQUEST)

    assert product_spec.mvp_features
    owners = {task.owner for task in task_graph.tasks}
    assert {"frontend", "backend"} <= owners


def test_reference_graph_director_to_architect():

    result = build_graph().invoke({"user_request": REQUEST})

    assert result["blueprint"].project_structure
    assert result["schema_spec"].models
    assert result["api_contract"].endpoints


def test_full_workshop_graph(runner, venv_on_path):

    result = runner.build_workshop_graph().invoke(
        {"user_request": REQUEST, "iteration": 0}
    )

    assert result["api_contract"].endpoints
    assert result["schema_spec"].models
    assert set(result["files"]) >= {"frontend_proposal.md", "backend_proposal.md"}
    assert all(text.strip() for text in result["files"].values())
    assert result["test_report"].status == "passed"
    assert result["iteration"] == 0


def test_workshop_script_runs_start_to_finish(venv_on_path):
    """The README command: python run_vibecoder/vibecoder_langchain.py"""

    result = subprocess.run(
        [sys.executable, str(RUNNER_PATH)],
        capture_output=True,
        text=True,
        cwd=VIBECODER_ROOT,
        timeout=600,
    )

    assert result.returncode == 0, result.stderr[-1500:]
    assert "=== 07-13. Full LangGraph workflow ===" in result.stdout
    assert "QA status: passed" in result.stdout


def test_reference_graph_documented_command():
    """graph.py docstring: `python -m vibecoder.src.graph.graph` from the repo root."""

    env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}

    result = subprocess.run(
        [sys.executable, "-m", "vibecoder.src.graph.graph"],
        capture_output=True,
        text=True,
        env=env,
        cwd=VIBECODER_ROOT.parent,
        timeout=600,
    )

    assert result.returncode == 0, result.stderr[-1500:]
