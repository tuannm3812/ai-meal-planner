"""Regression harness for the Streamlit app.

These assertions are written against the 685-line app.py BEFORE it is split, so
they describe observable behaviour rather than structure. Phase 4b must keep
every one of them passing unchanged - that is the evidence the decomposition
changed nothing a user sees.
"""

from pathlib import Path
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

# AppTest.from_file resolves a relative path against the *calling* file, not the
# pytest invocation's cwd - "streamlit_app/app.py" would look for
# streamlit_app/tests/streamlit_app/app.py and raise FileNotFoundError. An
# absolute path sidesteps that resolution rule entirely.
APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = 90


@pytest.fixture(name="app")
def _app(monkeypatch: pytest.MonkeyPatch) -> AppTest:
    """Run the app in demo mode, so no API server is required.

    Args:
        monkeypatch: Used to force demo mode via the environment.

    Returns:
        A run AppTest instance.
    """
    monkeypatch.setenv("STREAMLIT_DEMO_MODE", "1")
    harness = AppTest.from_file(APP, default_timeout=TIMEOUT)
    harness.run()
    return harness


def _by_label(elements: Any, label: str) -> Any:
    """Find a rendered widget by its visible label.

    No widget in app.py sets a key=, so AppTest's key lookup is unavailable and
    index lookup would silently shift if a widget is ever reordered. Labels are
    what a user actually sees, so they are what these tests address.

    Args:
        elements: An AppTest element sequence, e.g. app.button.
        label: The exact visible label.

    Returns:
        The matching element.

    Raises:
        AssertionError: If no element carries that label.
    """
    for element in elements:
        if element.label == label:
            return element
    raise AssertionError(f"no element labelled {label!r}; saw {[e.label for e in elements]}")


def test_the_app_runs_without_raising(app: AppTest) -> None:
    """A script exception here means the app is broken for every user."""
    assert not app.exception, [str(item.value) for item in app.exception]


def test_the_three_tabs_exist(app: AppTest) -> None:
    assert len(app.tabs) == 3


def test_the_expected_subheaders_render(app: AppTest) -> None:
    """Pins the section headings a user navigates by."""
    rendered = {item.value for item in app.subheader}
    for expected in {
        "Request",
        "Response",
        "Calorie Expenditure",
        "Meal History",
        "Saved Meals",
        "Run Mode",
    }:
        assert expected in rendered, f"missing subheader: {expected}"


def test_the_four_action_buttons_exist(app: AppTest) -> None:
    """One per workflow: meal plan, calories, history, saved meals."""
    labels = {item.label for item in app.button}
    for expected in {
        "Generate meal",
        "Predict expenditure",
        "Load history",
        "Load saved meals",
    }:
        assert expected in labels, f"missing button: {expected}"


def test_the_expected_text_inputs_exist(app: AppTest) -> None:
    labels = {item.label for item in app.text_input}
    for expected in {"Craving or meal goal", "Location", "User ID"}:
        assert expected in labels, f"missing text input: {expected}"


def test_demo_mode_is_genuinely_active(app: AppTest) -> None:
    """Pins that the fixture's STREAMLIT_DEMO_MODE env var actually flips the toggle.

    Every other test in this module runs against the `app` fixture and only ever
    observes symptoms of demo mode being on (no exception, no error box, a
    successful generation) - none of them would notice if the sidebar's
    `Run Mode` toggle silently stopped reading STREAMLIT_DEMO_MODE and defaulted
    to off, because with a real FastAPI server absent the other tests would then
    fail for an unrelated reason (a ConnectionError) or, worse, pass against a
    server that happens to be running on the test machine. Asserting the toggle's
    own value is the one check that is unambiguous either way.
    """
    demo_toggle = _by_label(app.toggle, "Self-contained Streamlit demo")
    assert demo_toggle.value is True, "demo mode is not active; STREAMLIT_DEMO_MODE wiring broke"


def test_generating_a_meal_in_demo_mode_produces_a_response(app: AppTest) -> None:
    """The end-to-end demo workflow, with no API server running.

    This is spec section 9's "done when" clause: the deployed Streamlit demo must
    still work with no backend. If the decomposition breaks the wiring between
    the sidebar's config and the views, this is the test that catches it.

    Every interactive branch in app.py is wrapped in its own
    `try: ... except Exception as exc: render_api_error(exc)`, so a bug inside
    the click handler (a NameError, a dropped config field) never reaches
    `app.exception` - it is swallowed into an `st.error(...)` box instead. So
    the meaningful assertions here are on rendered *values*, not on the crash
    signal: no error box, a success box that is new since the initial render
    (the sidebar always renders its own success boxes, click or no click), and
    the four nutrition metrics actually present with a non-zero calorie count.
    The old "Response" subheader assertion is gone - `st.subheader("Response")`
    renders unconditionally regardless of tab, click, or outcome, so it asserted
    nothing.
    """
    success_before_click = {str(item.value) for item in app.success}

    _by_label(app.text_input, "Craving or meal goal").set_value("high-protein burger")
    _by_label(app.button, "Generate meal").click().run(timeout=TIMEOUT)

    assert not app.exception, [str(item.value) for item in app.exception]

    errors = [str(item.value) for item in app.error]
    assert not errors, f"an error box rendered instead of a meal plan: {errors}"

    new_success_boxes = {str(item.value) for item in app.success} - success_before_click
    assert new_success_boxes, (
        "no success box appeared after clicking Generate meal (the sidebar's own "
        "success boxes render on every run and don't count)"
    )

    metrics = {item.label: item.value for item in app.metric}
    for expected in ("Calories", "Protein", "Carbs", "Fat"):
        assert expected in metrics, f"missing nutrition metric: {expected}; saw {metrics}"
    calories = metrics["Calories"]
    assert float(calories) > 0, f"Calories metric was not positive: {calories}"
