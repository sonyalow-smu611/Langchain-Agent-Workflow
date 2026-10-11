"""
End-to-end tests of the workshop LangGraph workflow with the LLM faked out —
every node, edge, and the repair loop runs for real, but no network calls.

Run: `pytest e2e -m "not live"` from vibecoder/.

Learn: a graph's wiring (edges, routing, state merging) can be tested
deterministically by replacing only the model, not the nodes.
"""

import os
import subprocess
import sys

from vibecoder.src.graph.routing import route_after_qa
from vibecoder.src.schemas.tasks import Task, TaskGraph
from vibecoder.src.tools.testing import run_tests

from conftest import VIBECODER_ROOT

REQUEST = "Build a simple todo app."


def test_happy_path_runs_every_stage(runner, fake_llm, passing_report, monkeypatch):

    monkeypatch.setattr(runner, "run_tests", lambda: passing_report)

    result = runner.build_workshop_graph().invoke(
        {"user_request": REQUEST, "iteration": 0}
    )

    assert set(result) >= {
        "user_request",
        "product_spec",
        "task_graph",
        "blueprint",
        "schema_spec",
        "api_contract",
        "files",
        "test_report",
        "repair_tickets",
    }
    assert set(result["files"]) == {"frontend_proposal.md", "backend_proposal.md"}
    assert result["test_report"].status == "passed"
    assert result["repair_tickets"] == []
    assert result["iteration"] == 0

    # director (2) -> architect (3) -> two workers, and no repair call.
    assert fake_llm.call_names()[:5] == [
        "ProductSpec",
        "TaskGraph",
        "BlueprintSpec",
        "SchemaSpec",
        "APIContract",
    ]
    assert fake_llm.call_names()[5:] == ["text", "text"]


def test_failing_qa_loops_through_repair_then_stops(
    runner, fake_llm, failing_report, monkeypatch
):

    monkeypatch.setattr(runner, "run_tests", lambda: failing_report)

    result = runner.build_workshop_graph().invoke(
        {"user_request": REQUEST, "iteration": 0}
    )

    assert result["test_report"].status == "failed"
    assert result["iteration"] == 3
    assert [ticket.issue_id for ticket in result["repair_tickets"]] == ["BUG-1"]
    assert "repair_BUG-1.md" in result["files"]

    # Worker proposals survive the repair node's files update.
    assert {"frontend_proposal.md", "backend_proposal.md"} <= set(result["files"])

    # 2 worker calls + 3 repair attempts.
    assert fake_llm.call_names().count("text") == 5


def test_qa_recovers_after_one_repair(
    runner, fake_llm, failing_report, passing_report, monkeypatch
):

    reports = iter([failing_report, passing_report])
    monkeypatch.setattr(runner, "run_tests", lambda: next(reports))

    result = runner.build_workshop_graph().invoke(
        {"user_request": REQUEST, "iteration": 0}
    )

    assert result["test_report"].status == "passed"
    assert result["iteration"] == 1
    assert result["repair_tickets"] == []


def test_missing_frontend_task_skips_workers(
    runner, fake_llm, passing_report, monkeypatch
):

    fake_llm.outputs[TaskGraph] = TaskGraph(
        tasks=[Task(id="T1", owner="backend", description="Build the task API")]
    )
    monkeypatch.setattr(runner, "run_tests", lambda: passing_report)

    result = runner.build_workshop_graph().invoke(
        {"user_request": REQUEST, "iteration": 0}
    )

    assert set(result["files"]) == {"worker_warning.md"}
    assert "text" not in fake_llm.call_names()


def test_route_after_qa(passing_report, failing_report):

    assert route_after_qa({}) == "repair"
    assert route_after_qa({"test_report": passing_report}) == "end"
    assert route_after_qa({"test_report": failing_report, "iteration": 2}) == "repair"
    assert route_after_qa({"test_report": failing_report, "iteration": 3}) == "end"


def test_run_tests_reports_real_pytest_result(venv_on_path):

    report = run_tests()

    assert report.status == "passed", report.failures


def test_run_tests_without_pytest_on_path(monkeypatch):
    """`python run_vibecoder/...` via a venv interpreter that is not activated."""

    monkeypatch.setenv("PATH", "/usr/bin:/bin")

    report = run_tests()

    assert report.status == "passed", report.failures


def test_agents_load_env_from_vibecoder_folder():
    """README: `.env` lives in vibecoder/, and base.py loads it for the agents."""

    env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
    env["PYTHONPATH"] = str(VIBECODER_ROOT.parent)

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import os, vibecoder.src.agents.base;"
            "print(bool(os.getenv('OPENAI_API_KEY')))",
        ],
        capture_output=True,
        text=True,
        env=env,
        cwd=VIBECODER_ROOT,
    )

    assert result.stdout.strip() == "True", result.stderr[-500:]
