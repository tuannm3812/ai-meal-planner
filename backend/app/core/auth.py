"""G4 authentication: trusted-client API keys, principals and a rate limit.

Keys identify client *applications*, not end users. Each key record carries a
stable ``client_id``, and every stored record is namespaced by that id, never by
the key string, so rotating a key (a new key for the same ``client_id``) keeps
the namespace. Revocation is removing the record and redeploying.

Only SHA-256 hashes of keys are configured, so a leaked environment dump does
not leak usable keys. Generate one with::

    python -c "import hashlib,sys;print(hashlib.sha256(sys.argv[1].encode()).hexdigest())" KEY

With no keys configured the API runs in an explicit open local mode under the
``local`` principal, which is how the React dashboard works in development. In
production that is refused at startup (owner decision A1, 2026-10-10).
"""

import hashlib
import hmac
import json
import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

from .config import AppSettings

logger = logging.getLogger(__name__)

SCOPES = ("plans:write", "feedback:write", "history:read")
"""Every scope a key may hold; there is deliberately no admin scope."""

_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class Principal:
    """The authenticated client application.

    Attributes:
        client_id: The stable namespace every record is stored under.
        scopes: The operations this client may perform.
    """

    client_id: str
    scopes: frozenset[str]


LOCAL_PRINCIPAL = Principal(client_id="local", scopes=frozenset(SCOPES))
"""The single principal of open local mode, holding every scope."""


def hash_key(key: str) -> str:
    """Return the SHA-256 hex digest an API key is configured as.

    Args:
        key: The raw API key.

    Returns:
        Its lowercase SHA-256 hex digest.
    """
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ApiKeyRecord:
    """One configured key: whose it is and what it may do."""

    client_id: str
    key_sha256: str
    scopes: frozenset[str]


@dataclass(frozen=True)
class AuthConfig:
    """The configured key records, resolved once at startup."""

    records: tuple[ApiKeyRecord, ...] = field(default_factory=tuple)

    @property
    def enforced(self) -> bool:
        """Whether requests must present a key (any key is configured)."""
        return bool(self.records)

    @classmethod
    def from_settings(cls, settings: AppSettings) -> "AuthConfig":
        """Parse ``API_KEYS`` and apply the production guard.

        Args:
            settings: Resolved application settings.

        Returns:
            The auth configuration.

        Raises:
            ValueError: If ``API_KEYS`` is malformed. A typo must not yield an
                open or half-configured API.
            RuntimeError: If no keys are configured in production.
        """
        raw = settings.api_keys.strip()
        records = tuple(_parse_record(item) for item in _parse_list(raw)) if raw else ()
        # Decide on the parsed record count, never on the raw string: "[]", or a
        # list whose last key was just revoked, is as empty as "". Codex found
        # the earlier string check let production start open (P1, 2026-10-10).
        if not records:
            if settings.environment == "production":
                raise RuntimeError(
                    "API_KEYS has no key records in production. Refusing to start "
                    "an unauthenticated API; configure at least one key record."
                )
            logger.warning(
                "API_KEYS has no key records: running in open local mode. Every "
                "request is served unauthenticated in the single 'local' namespace."
            )
        return cls(records=records)

    def authenticate(self, presented: str | None) -> Principal | None:
        """Resolve a presented key to its principal.

        Args:
            presented: The ``X-API-Key`` header value, if any.

        Returns:
            The principal; ``LOCAL_PRINCIPAL`` in open local mode; or None when
            the key is missing or unknown.
        """
        if not self.enforced:
            return LOCAL_PRINCIPAL
        if not presented:
            return None
        digest = hash_key(presented)
        for record in self.records:
            if hmac.compare_digest(digest, record.key_sha256):
                return Principal(client_id=record.client_id, scopes=record.scopes)
        return None


def _parse_list(raw: str) -> list[Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"API_KEYS is not valid JSON: {exc.msg}") from exc
    if not isinstance(parsed, list):
        raise ValueError("API_KEYS must be a JSON list of key records.")
    return parsed


def _parse_record(item: Any) -> ApiKeyRecord:
    if not isinstance(item, dict):
        raise ValueError("Each API_KEYS entry must be an object.")
    client_id = item.get("client_id")
    key_sha256 = item.get("key_sha256")
    scopes = item.get("scopes")
    if not isinstance(client_id, str) or not client_id.strip():
        raise ValueError("Each API_KEYS entry needs a non-empty client_id.")
    if not isinstance(key_sha256, str) or not _SHA256_HEX.match(key_sha256):
        raise ValueError(f"API_KEYS entry {client_id!r} needs a 64-char hex key_sha256.")
    if not isinstance(scopes, list) or not set(scopes) <= set(SCOPES):
        raise ValueError(f"API_KEYS entry {client_id!r} has scopes outside {list(SCOPES)}.")
    return ApiKeyRecord(client_id=client_id, key_sha256=key_sha256, scopes=frozenset(scopes))


class RateLimiter:
    """A fixed one-minute window per client_id, held in this process only.

    It is per instance by construction: N instances allow up to N times the
    limit. That is the documented v1 behaviour, not an account-wide quota.
    """

    def __init__(self, limit_per_minute: int, clock: Callable[[], float] = time.monotonic):
        """Configure the limit.

        Args:
            limit_per_minute: Requests allowed per client per window.
            clock: Monotonic time source, injectable for tests.
        """
        self.limit = limit_per_minute
        self._clock = clock
        self._windows: dict[str, tuple[float, int]] = {}
        self._lock = Lock()

    def retry_after(self, client_id: str) -> float | None:
        """Count one request and say whether it must wait.

        Args:
            client_id: The requesting client.

        Returns:
            None when allowed, otherwise the seconds until the window resets.
        """
        now = self._clock()
        with self._lock:
            start, count = self._windows.get(client_id, (now, 0))
            if now - start >= 60:
                start, count = now, 0
            if count >= self.limit:
                return round(60 - (now - start), 3)
            self._windows[client_id] = (start, count + 1)
            return None
