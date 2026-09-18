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

    conftest.py prepends streamlit_app/ to sys.path, so `api`, `config` and
    `demo` shadow any same-named module for the whole pytest session. If a
    dependency ever ships one of these names, this fails loudly instead of the
    tests silently exercising the wrong module.
    """
    import api
    import config
    import demo

    for module in (api, config, demo):
        assert module.__file__ is not None
        assert Path(module.__file__).parent.name == "streamlit_app", module.__file__
