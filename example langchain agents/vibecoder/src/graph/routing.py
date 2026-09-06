"""
Conditional edge function deciding what happens after QA: end the workflow,
or loop back for another repair attempt (capped at 3 iterations).

Run: not run directly — passed to
     `builder.add_conditional_edges("qa", route_after_qa, ...)` if/when qa is
     wired into graph.py (it isn't yet).

Learn: LangGraph conditional edges — a plain function that reads state and
returns a string naming the next node, used to build loops like this
repair loop.
"""


def route_after_qa(state):

    test_report = state.get(
        "test_report"
    )

    if test_report is None:
        return "repair"

    if test_report.status == "passed":
        return "end"

    if state.get("iteration", 0) >= 3:
        return "end"

    return "repair"