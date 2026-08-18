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