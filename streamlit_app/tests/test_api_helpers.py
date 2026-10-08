"""Unit tests for the Streamlit app's stateless helpers."""

from pathlib import Path

import pytest
from api import parse_extra_items


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("a, b", ["a", "b"]),
        (" a ,, b ", ["a", "b"]),
        ("", []),
        ("   ", []),
    ],
)
def test_parse_extra_items_splits_trims_and_drops_blanks(raw: str, expected: list[str]) -> None:
    assert parse_extra_items(raw) == expected


def test_the_helper_modules_resolve_inside_streamlit_app() -> None:
    """Guard against the generic module names binding to something else.

    conftest.py prepends streamlit_app/ to sys.path, so `api`, `config`,
    `demo` and `views` shadow any same-named module for the whole pytest
    session. If a dependency ever ships one of these names, this fails
    loudly instead of the tests silently exercising the wrong module.

    `views` is a package, so its `__file__` is
    `streamlit_app/views/__init__.py` - one directory deeper than the flat
    modules - so its check looks at the grandparent directory instead of
    the parent.
    """
    import api
    import config
    import demo
    import views

    for module in (api, config, demo):
        assert module.__file__ is not None
        assert Path(module.__file__).parent.name == "streamlit_app", module.__file__

    assert views.__file__ is not None
    assert Path(views.__file__).parent.parent.name == "streamlit_app", views.__file__


@pytest.mark.parametrize(
    "polite", ["thank you", "thanks", "hello", "hi", "hey", "ok", "okay", "test"]
)
def test_is_meal_like_input_rejects_polite_only_input(polite: str) -> None:
    """These must not reach the API. Spec section 9 wrongly called this duplication."""
    from views.meal_plan import is_meal_like_input

    assert is_meal_like_input(polite) is False


@pytest.mark.parametrize("value", ["ab", " a ", ""])
def test_is_meal_like_input_rejects_anything_under_three_characters(value: str) -> None:
    from views.meal_plan import is_meal_like_input

    assert is_meal_like_input(value) is False


@pytest.mark.parametrize("value", ["burger", "high-protein burger", "pasta"])
def test_is_meal_like_input_accepts_a_real_craving(value: str) -> None:
    from views.meal_plan import is_meal_like_input

    assert is_meal_like_input(value) is True
