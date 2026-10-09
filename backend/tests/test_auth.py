"""G4 auth core: key records, principals, open local mode and the rate limit.

Contract (portfolio log, 2026-10-07/08; owner decisions 2026-10-11): API keys
identify trusted client applications. A key record holds a stable client_id,
and namespaces bind to that id, never to the key string. With no keys
configured the API runs open under client_id "local", except in production,
where it refuses to start.
"""

import hashlib
import json

import pytest

from backend.app.core.auth import (
    LOCAL_PRINCIPAL,
    SCOPES,
    AuthConfig,
    RateLimiter,
    hash_key,
)
from backend.app.core.config import AppSettings


def _records(*entries: tuple[str, str, list[str]]) -> str:
    return json.dumps(
        [
            {"client_id": client_id, "key_sha256": hash_key(key), "scopes": scopes}
            for client_id, key, scopes in entries
        ]
    )


def _settings(api_keys: str = "", environment: str = "development") -> AppSettings:
    return AppSettings(_env_file=None, api_keys=api_keys, environment=environment)


def test_hash_key_is_sha256_hex() -> None:
    assert hash_key("secret") == hashlib.sha256(b"secret").hexdigest()


def test_no_keys_means_open_local_mode() -> None:
    auth = AuthConfig.from_settings(_settings())

    assert auth.enforced is False
    assert auth.authenticate(None) == LOCAL_PRINCIPAL
    assert auth.authenticate("anything") == LOCAL_PRINCIPAL
    assert LOCAL_PRINCIPAL.client_id == "local"
    assert LOCAL_PRINCIPAL.scopes == frozenset(SCOPES)


def test_production_without_keys_refuses_to_start() -> None:
    with pytest.raises(RuntimeError, match="API_KEYS"):
        AuthConfig.from_settings(_settings(environment="production"))


def test_a_configured_key_resolves_to_its_principal() -> None:
    auth = AuthConfig.from_settings(_settings(_records(("app-a", "key-a", ["plans:write"]))))

    principal = auth.authenticate("key-a")

    assert auth.enforced is True
    assert principal is not None
    assert principal.client_id == "app-a"
    assert principal.scopes == frozenset({"plans:write"})


@pytest.mark.parametrize("presented", [None, "", "wrong-key"])
def test_a_missing_or_unknown_key_is_rejected(presented: str | None) -> None:
    auth = AuthConfig.from_settings(_settings(_records(("app-a", "key-a", ["plans:write"]))))

    assert auth.authenticate(presented) is None


def test_rotation_keeps_the_client_namespace() -> None:
    """Two keys for one client_id: both resolve to the same principal id."""
    auth = AuthConfig.from_settings(
        _settings(
            _records(
                ("app-a", "old-key", ["history:read"]),
                ("app-a", "new-key", ["history:read"]),
            )
        )
    )

    assert auth.authenticate("old-key").client_id == "app-a"
    assert auth.authenticate("new-key").client_id == "app-a"


def test_a_removed_key_is_revoked() -> None:
    """Revocation is removal from the key list plus a redeploy (a new config)."""
    before = AuthConfig.from_settings(_settings(_records(("app-a", "old-key", ["plans:write"]))))
    after = AuthConfig.from_settings(_settings(_records(("app-a", "new-key", ["plans:write"]))))

    assert before.authenticate("old-key") is not None
    assert after.authenticate("old-key") is None


@pytest.mark.parametrize(
    "bad",
    [
        "not json",
        json.dumps({"client_id": "a"}),
        json.dumps([{"client_id": "", "key_sha256": "0" * 64, "scopes": []}]),
        json.dumps([{"client_id": "a", "key_sha256": "short", "scopes": []}]),
        json.dumps([{"client_id": "a", "key_sha256": "0" * 64, "scopes": ["admin"]}]),
        json.dumps([{"client_id": "a", "scopes": ["plans:write"]}]),
    ],
    ids=["not-json", "not-a-list", "empty-client", "bad-hash", "unknown-scope", "no-hash"],
)
def test_a_malformed_key_list_is_refused_at_startup(bad: str) -> None:
    """A typo must not silently produce an open or half-configured API."""
    with pytest.raises(ValueError):
        AuthConfig.from_settings(_settings(bad))


def test_the_rate_limit_is_a_per_client_fixed_window() -> None:
    clock = [100.0]
    limiter = RateLimiter(limit_per_minute=2, clock=lambda: clock[0])

    assert limiter.retry_after("app-a") is None
    assert limiter.retry_after("app-a") is None
    blocked = limiter.retry_after("app-a")
    assert blocked is not None
    assert 0 < blocked <= 60

    # Another client has its own budget.
    assert limiter.retry_after("app-b") is None

    # The window resets.
    clock[0] += 60
    assert limiter.retry_after("app-a") is None


def test_open_local_mode_warns_at_startup(caplog: pytest.LogCaptureFixture) -> None:
    """Owner decision A1: running unauthenticated must be visible in the logs."""
    with caplog.at_level("WARNING", logger="backend.app.core.auth"):
        AuthConfig.from_settings(_settings())

    assert any("open local mode" in record.message for record in caplog.records)


def test_a_keyed_configuration_does_not_warn(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level("WARNING", logger="backend.app.core.auth"):
        AuthConfig.from_settings(_settings(_records(("app-a", "key-a", ["plans:write"]))))

    assert not caplog.records
