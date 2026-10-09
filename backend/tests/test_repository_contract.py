"""One behavioural contract, run against every storage backend.

Both backends must satisfy this identically. When they diverge, this is the
file that says which one is wrong.
"""

from pathlib import Path
from typing import Any

import pytest

from backend.app.repositories.json_store import (
    MealFeedbackRepository,
    MealPlanRepository,
    UserProfileRepository,
)
from backend.app.repositories.sql import (
    SqlMealFeedbackRepository,
    SqlMealPlanRepository,
    SqlUserProfileRepository,
    build_engine,
)

BACKENDS = ["json", "sqlite"]


@pytest.fixture(params=BACKENDS)
def profile_store(request: pytest.FixtureRequest, tmp_path: Path) -> Any:
    if request.param == "json":
        return UserProfileRepository(tmp_path)
    return SqlUserProfileRepository(build_engine(tmp_path / "t.db"))


@pytest.fixture(params=BACKENDS)
def plan_store(request: pytest.FixtureRequest, tmp_path: Path) -> Any:
    if request.param == "json":
        return MealPlanRepository(tmp_path)
    return SqlMealPlanRepository(build_engine(tmp_path / "t.db"))


@pytest.fixture(params=BACKENDS)
def feedback_store(request: pytest.FixtureRequest, tmp_path: Path) -> Any:
    if request.param == "json":
        return MealFeedbackRepository(tmp_path)
    return SqlMealFeedbackRepository(build_engine(tmp_path / "t.db"))


def test_profile_returns_the_default_for_an_unknown_user(profile_store: Any) -> None:
    """The default profile is the normal path, not an error case."""
    profile = profile_store.fetch_user_profile("nobody_at_all")
    assert profile["age"] == 28
    assert profile["gender"] == "m"
    assert profile["weight"] == 80.0
    assert profile["height"] == 180.0
    assert profile["workout_level"] == 1.55
    assert "dietary_restrictions" in profile


def test_plan_save_returns_none(plan_store: Any) -> None:
    assert plan_store.save({"request": {"user_id": "u1"}}, client_id="local") is None


def test_plans_come_back_newest_first(plan_store: Any) -> None:
    for i in range(3):
        plan_store.save({"request": {"user_id": "u1"}, "n": i}, client_id="local")
    items = plan_store.list_for_user("u1", client_id="local")
    assert [item["n"] for item in items] == [2, 1, 0]


def test_plans_respect_the_limit(plan_store: Any) -> None:
    for i in range(5):
        plan_store.save({"request": {"user_id": "u1"}, "n": i}, client_id="local")
    assert [item["n"] for item in plan_store.list_for_user("u1", limit=2, client_id="local")] == [
        4,
        3,
    ]


def test_plans_are_isolated_per_user(plan_store: Any) -> None:
    plan_store.save({"request": {"user_id": "u1"}, "n": 1}, client_id="local")
    plan_store.save({"request": {"user_id": "u2"}, "n": 2}, client_id="local")
    assert [item["n"] for item in plan_store.list_for_user("u1", client_id="local")] == [1]
    assert [item["n"] for item in plan_store.list_for_user("u2", client_id="local")] == [2]


def test_plans_for_an_unknown_user_are_empty(plan_store: Any) -> None:
    assert plan_store.list_for_user("nobody", client_id="local") == []


def test_plan_records_carry_saved_at(plan_store: Any) -> None:
    plan_store.save({"request": {"user_id": "u1"}}, client_id="local")
    assert "saved_at" in plan_store.list_for_user("u1", client_id="local")[0]


def test_plan_payloads_survive_nesting(plan_store: Any) -> None:
    """History rows are whole API responses; nesting must round-trip."""
    payload = {"request": {"user_id": "u1"}, "meal_plan": {"ingredients": [{"g": 100}]}}
    plan_store.save(payload, client_id="local")
    assert (
        plan_store.list_for_user("u1", client_id="local")[0]["meal_plan"]["ingredients"][0]["g"]
        == 100
    )


def test_feedback_save_returns_the_record(feedback_store: Any) -> None:
    record = feedback_store.save(
        {"user_id": "u1", "meal_name": "X", "liked": True}, client_id="local"
    )
    assert record["meal_name"] == "X"
    assert "saved_at" in record


def test_feedback_comes_back_newest_first(feedback_store: Any) -> None:
    for i in range(3):
        feedback_store.save({"user_id": "u1", "n": i}, client_id="local")
    assert [item["n"] for item in feedback_store.list_for_user("u1", client_id="local")] == [
        2,
        1,
        0,
    ]


def test_feedback_saved_only_filters(feedback_store: Any) -> None:
    feedback_store.save({"user_id": "u1", "n": 0, "saved": False}, client_id="local")
    feedback_store.save({"user_id": "u1", "n": 1, "saved": True}, client_id="local")
    saved = feedback_store.list_for_user("u1", saved_only=True, client_id="local")
    assert [item["n"] for item in saved] == [1]
    assert all(item["saved"] for item in saved)


def test_feedback_respects_the_limit(feedback_store: Any) -> None:
    for i in range(5):
        feedback_store.save({"user_id": "u1", "n": i}, client_id="local")
    assert [
        item["n"] for item in feedback_store.list_for_user("u1", limit=2, client_id="local")
    ] == [4, 3]


def test_feedback_is_isolated_per_user(feedback_store: Any) -> None:
    feedback_store.save({"user_id": "u1", "n": 1}, client_id="local")
    feedback_store.save({"user_id": "u2", "n": 2}, client_id="local")
    assert [item["n"] for item in feedback_store.list_for_user("u1", client_id="local")] == [1]


def test_feedback_saved_only_filters_before_applying_the_limit(feedback_store: Any) -> None:
    """The filter runs first, then the limit - not the other way round.

    With n=0..4 and saved=(n%2==0), filtering first then taking two gives
    [4, 2]. Slicing to two first and then filtering would give only [4]. A SQL
    backend that filtered in Python after an unconditional LIMIT would diverge
    here and nowhere else.
    """
    for i in range(5):
        feedback_store.save({"user_id": "u1", "n": i, "saved": i % 2 == 0}, client_id="local")
    result = feedback_store.list_for_user("u1", limit=2, saved_only=True, client_id="local")
    assert [item["n"] for item in result] == [4, 2]


def test_feedback_for_an_unknown_user_is_empty(feedback_store: Any) -> None:
    """No rows must mean an empty list, not None and not an exception."""
    assert feedback_store.list_for_user("nobody", client_id="local") == []


def test_limit_defaults_to_twenty(plan_store: Any) -> None:
    """The default is part of the contract; a backend must not pick its own."""
    for i in range(25):
        plan_store.save({"request": {"user_id": "u1"}, "n": i}, client_id="local")
    assert len(plan_store.list_for_user("u1", client_id="local")) == 20


def test_feedback_limit_defaults_to_twenty(feedback_store: Any) -> None:
    """The plan-store default is covered above; feedback must match it too."""
    for i in range(25):
        feedback_store.save({"user_id": "u1", "n": i}, client_id="local")
    assert len(feedback_store.list_for_user("u1", client_id="local")) == 20


@pytest.mark.parametrize("bad_request", [None, "not-a-dict", 42, [], {"no_user_id": True}], ids=str)
def test_a_malformed_request_field_never_poisons_reads(plan_store: Any, bad_request: Any) -> None:
    """A payload with an unusable `request` must not break other users' history.

    The JSON backend used to accept such a record and then raise on every
    subsequent list_for_user - for every user, not just the affected one. The SQL
    backend raised at write time instead. Both must now degrade the same way:
    store it, attribute it to no one, and leave good records readable.
    """
    plan_store.save({"request": {"user_id": "u1"}, "n": 1}, client_id="local")
    plan_store.save({"request": bad_request, "n": 2}, client_id="local")
    assert [item["n"] for item in plan_store.list_for_user("u1", client_id="local")] == [1]
    # The malformed record is attributed to no one rather than to some real user.
    assert [item["n"] for item in plan_store.list_for_user("", client_id="local")] == [2]


@pytest.mark.parametrize(
    ("bad_payload", "expected_owner"),
    [
        ({"user_id": None, "n": 2}, ""),
        ({"user_id": 42, "n": 2}, "42"),
        ({"n": 2}, ""),
    ],
    ids=["none", "int", "missing_key"],
)
def test_a_malformed_feedback_user_id_never_poisons_reads(
    feedback_store: Any, bad_payload: dict[str, Any], expected_owner: str
) -> None:
    """Both backends must attribute a malformed feedback user_id the same way.

    Mirrors test_a_malformed_request_field_never_poisons_reads above. The SQL
    backend always coerced user_id with str(...); the JSON backend compared
    the raw stored value. A None or missing user_id must land on no one
    (""), and a non-string id like an int must be attributed under its
    string form - identically on both backends.
    """
    feedback_store.save({"user_id": "u1", "n": 1}, client_id="local")
    feedback_store.save(bad_payload, client_id="local")
    assert [item["n"] for item in feedback_store.list_for_user("u1", client_id="local")] == [1]
    assert [
        item["n"] for item in feedback_store.list_for_user(expected_owner, client_id="local")
    ] == [2]


# --- G4: client namespaces -------------------------------------------------------
# Every record belongs to the client application that wrote it. A user_id is only
# unique within one client, so a guessed user_id must never reach another
# client's records. These run against both backends.


def test_plans_are_isolated_per_client_even_for_the_same_user_id(plan_store: Any) -> None:
    plan_store.save({"request": {"user_id": "user_123"}, "n": "a"}, client_id="app-a")
    plan_store.save({"request": {"user_id": "user_123"}, "n": "b"}, client_id="app-b")

    assert [i["n"] for i in plan_store.list_for_user("user_123", client_id="app-a")] == ["a"]
    assert [i["n"] for i in plan_store.list_for_user("user_123", client_id="app-b")] == ["b"]
    assert plan_store.list_for_user("user_123", client_id="app-c") == []


def test_plan_records_carry_their_client_id(plan_store: Any) -> None:
    plan_store.save({"request": {"user_id": "u1"}}, client_id="app-a")

    assert plan_store.list_for_user("u1", client_id="app-a")[0]["client_id"] == "app-a"


def test_a_plan_is_found_by_request_id_only_within_its_client(plan_store: Any) -> None:
    plan_store.save({"request": {"user_id": "u1"}, "request_id": "req-1"}, client_id="app-a")

    found = plan_store.find_by_request_id("req-1", client_id="app-a")
    assert found is not None
    assert found["request_id"] == "req-1"
    assert plan_store.find_by_request_id("req-1", client_id="app-b") is None
    assert plan_store.find_by_request_id("req-unknown", client_id="app-a") is None


def test_feedback_is_isolated_per_client_even_for_the_same_user_id(feedback_store: Any) -> None:
    feedback_store.save({"user_id": "user_123", "n": "a", "saved": True}, client_id="app-a")
    feedback_store.save({"user_id": "user_123", "n": "b", "saved": True}, client_id="app-b")

    assert [i["n"] for i in feedback_store.list_for_user("user_123", client_id="app-a")] == ["a"]
    saved_b = feedback_store.list_for_user("user_123", saved_only=True, client_id="app-b")
    assert [i["n"] for i in saved_b] == ["b"]


def test_namespaced_calls_require_a_client_id(plan_store: Any, feedback_store: Any) -> None:
    """Forgetting the namespace must be a TypeError, never a silent default."""
    with pytest.raises(TypeError):
        plan_store.list_for_user("u1")
    with pytest.raises(TypeError):
        feedback_store.list_for_user("u1")


def test_legacy_json_records_without_a_client_id_belong_to_local(tmp_path: Path) -> None:
    """Records written before G4 stay readable in open local mode."""
    import json

    (tmp_path / "meal_history.json").write_text(
        json.dumps([{"request": {"user_id": "u1"}, "request_id": "old"}]), encoding="utf-8"
    )
    store = MealPlanRepository(tmp_path)

    assert [r["request_id"] for r in store.list_for_user("u1", client_id="local")] == ["old"]
    assert store.list_for_user("u1", client_id="app-a") == []


def test_an_old_sqlite_schema_is_refused_with_a_clear_message(tmp_path: Path) -> None:
    """create_all cannot add the client_id column, so a pre-G4 database must not load."""
    import sqlite3

    path = tmp_path / "old.db"
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE meal_plans (id INTEGER PRIMARY KEY, user_id TEXT, "
            "saved_at TEXT, payload JSON)"
        )

    with pytest.raises(RuntimeError, match=r"old\.db"):
        build_engine(path)
