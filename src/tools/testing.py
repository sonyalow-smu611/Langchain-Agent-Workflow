import subprocess

from src.schemas.testing import TestReport, TestFailure


def run_tests() -> TestReport:
    """
    Run the project's tests and return a structured report.
    """

    result = subprocess.run(
        ["pytest"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return TestReport(
            status="passed",
            tests_run=0,
            tests_passed=0,
            tests_failed=0,
            failures=[]
        )

    return TestReport(
        status="failed",
        tests_run=0,
        tests_passed=0,
        tests_failed=1,
        failures=[
            TestFailure(
                test_name="pytest",
                error=result.stdout + result.stderr
            )
        ]
    )