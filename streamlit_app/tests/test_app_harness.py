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


def test_generating_a_meal_in_demo_mode_produces_a_response(app: AppTest) -> None:
    """The end-to-end demo workflow, with no API server running.

    This is spec section 9's "done when" clause: the deployed Streamlit demo must
    still work with no backend. If the decomposition breaks the wiring between
    the sidebar's config and the views, this is the test that catches it.
    """
    _by_label(app.text_input, "Craving or meal goal").set_value("high-protein burger")
    _by_label(app.button, "Generate meal").click().run(timeout=TIMEOUT)
    assert not app.exception, [str(item.value) for item in app.exception]
    assert any("Response" == item.value for item in app.subheader)
