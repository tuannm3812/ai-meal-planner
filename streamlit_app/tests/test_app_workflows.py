"""Covers the four workflows the frozen harness never clicks.

test_app_harness.py is a byte-identical regression fixture (see its own docstring)
and only exercises "Generate meal". Every click handler in the views wraps its body
in `try/except Exception: render_api_error(exc)`, so a broken `config.<field>` or a
mistyped API path inside "Predict expenditure", "Load history", "Load saved meals"
or "Submit feedback" would raise, get swallowed into an `st.error` box, and stay
invisible to every other CI signal. These tests assert on rendered values - never
just "no exception" - and always assert there is no error box, quoting its text so
a failure is legible.
"""

from pathlib import Path
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

# AppTest.from_file resolves a relative path against the *calling* file, not the
# pytest invocation's cwd - see test_app_harness.py for the full explanation.
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

    No widget in the app sets a key=, so label lookup is the only stable way to
    address a widget. See test_app_harness.py's `_by_label` for the full rationale.

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


def _errors(app: AppTest) -> list[str]:
    """Collect rendered `st.error` box text, for use in assertion messages."""
    return [str(item.value) for item in app.error]


def test_predict_expenditure_renders_the_calorie_metrics(app: AppTest) -> None:
    """The Calories tab's only workflow: predict, no server required."""
    _by_label(app.button, "Predict expenditure").click().run(timeout=TIMEOUT)

    assert not _errors(app), f"Predict expenditure raised: {_errors(app)}"
    metrics = {item.label: item.value for item in app.metric}
    for expected in ("Daily expenditure", "Meal budget", "Confidence"):
        assert expected in metrics, f"missing metric: {expected}; saw {metrics}"


def test_history_and_saved_meals_load_empty_on_a_fresh_store(app: AppTest) -> None:
    """Both History tab loaders, against the tmp_path store conftest provides."""
    _by_label(app.button, "Load history").click().run(timeout=TIMEOUT)
    assert not _errors(app), f"Load history raised: {_errors(app)}"
    records = _by_label(app.metric, "Records")
    assert records.value == "0", f"expected an empty store, got {records.value!r}"

    _by_label(app.button, "Load saved meals").click().run(timeout=TIMEOUT)
    assert not _errors(app), f"Load saved meals raised: {_errors(app)}"
    saved = _by_label(app.metric, "Saved")
    assert saved.value == "0", f"expected an empty store, got {saved.value!r}"


def test_generating_saving_and_reloading_a_meal_updates_history(app: AppTest) -> None:
    """Generate -> tick Save meal -> submit feedback -> both loaders now show 1.

    This is the one place a save actually reaches disk (via
    conftest's tmp_path-redirected DEMO_DATA_DIR), so it is also the only test
    that can prove the History tab's two loaders see a record that was just
    written, not merely that they render cleanly against an empty store.
    """
    _by_label(app.button, "Generate meal").click().run(timeout=TIMEOUT)
    assert not _errors(app), f"Generate meal raised: {_errors(app)}"

    _by_label(app.checkbox, "Save meal").check().run(timeout=TIMEOUT)
    _by_label(app.button, "Submit feedback").click().run(timeout=TIMEOUT)
    assert not _errors(app), f"Submit feedback raised: {_errors(app)}"
    successes = {str(item.value) for item in app.success}
    assert "Feedback saved" in successes, f"no 'Feedback saved' box; saw {successes}"

    _by_label(app.button, "Load history").click().run(timeout=TIMEOUT)
    assert not _errors(app), f"Load history raised: {_errors(app)}"
    records = _by_label(app.metric, "Records")
    assert records.value == "1", f"expected the saved meal to show up, got {records.value!r}"

    _by_label(app.button, "Load saved meals").click().run(timeout=TIMEOUT)
    assert not _errors(app), f"Load saved meals raised: {_errors(app)}"
    saved = _by_label(app.metric, "Saved")
    assert saved.value == "1", f"expected the saved meal to show up, got {saved.value!r}"
