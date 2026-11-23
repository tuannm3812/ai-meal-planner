"""DEC-43: Firebase ID tokens are checked offline against injected certificates."""

import time
from typing import Any

import pytest
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from google.auth import crypt, jwt

from backend.app.core.firebase_auth import FirebaseTokenVerifier

PROJECT = "demo-project"


def _key_pair() -> tuple[bytes, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private, public.decode()


PRIVATE, PUBLIC = _key_pair()
OTHER_PRIVATE, _ = _key_pair()


def _token(*, kid: str = "k1", private: bytes = PRIVATE, **claims: Any) -> str:
    now = int(time.time())
    payload = {
        "iss": f"https://securetoken.google.com/{PROJECT}",
        "aud": PROJECT,
        "sub": "uid-123",
        "iat": now,
        "exp": now + 3600,
        **claims,
    }
    signer = crypt.RSASigner.from_string(private, key_id=kid)
    return jwt.encode(signer, payload).decode()


class _Certs:
    def __init__(self, *sets: dict[str, str]) -> None:
        self.sets = list(sets)
        self.calls = 0

    def __call__(self) -> dict[str, str]:
        self.calls += 1
        return self.sets[min(self.calls, len(self.sets)) - 1]


def _verifier(certs: _Certs | None = None, clock: Any = time.time) -> FirebaseTokenVerifier:
    return FirebaseTokenVerifier(PROJECT, fetch_certs=certs or _Certs({"k1": PUBLIC}), clock=clock)


def test_a_valid_token_resolves_to_its_uid() -> None:
    assert _verifier().verify(_token()) == "uid-123"


@pytest.mark.parametrize(
    "token",
    [
        None,
        "",
        "not-a-jwt",
        _token(aud="another-project"),
        _token(iss="https://securetoken.google.com/another-project"),
        _token(exp=int(time.time()) - 3600, iat=int(time.time()) - 7200),
        _token(sub=""),
        _token(sub="x" * 129),
        _token(private=OTHER_PRIVATE),
        _token(kid="unknown"),
    ],
    ids=[
        "missing",
        "empty",
        "malformed",
        "wrong-audience",
        "wrong-issuer",
        "expired",
        "empty-subject",
        "long-subject",
        "forged-signature",
        "unknown-key",
    ],
)
def test_an_invalid_token_is_refused(token: str | None) -> None:
    assert _verifier().verify(token) is None


def test_certificates_are_cached_between_tokens() -> None:
    certs = _Certs({"k1": PUBLIC})
    verifier = _verifier(certs)

    verifier.verify(_token())
    verifier.verify(_token())

    assert certs.calls == 1


def test_a_rotated_key_triggers_one_refetch() -> None:
    certs = _Certs({"old": PUBLIC}, {"k1": PUBLIC})
    verifier = _verifier(certs)
    verifier.verify(_token(kid="old"))

    assert verifier.verify(_token(kid="k1")) == "uid-123"
    assert certs.calls == 2


def test_the_cache_expires_after_an_hour() -> None:
    now = [1000.0]
    certs = _Certs({"k1": PUBLIC})
    verifier = _verifier(certs, clock=lambda: now[0])
    verifier.verify(_token())

    now[0] += 3600
    verifier.verify(_token())

    assert certs.calls == 2


def test_unreachable_certificates_refuse_rather_than_raise() -> None:
    def _down() -> dict[str, str]:
        raise requests.ConnectionError("offline")

    assert FirebaseTokenVerifier(PROJECT, fetch_certs=_down).verify(_token()) is None


def test_a_project_id_is_required() -> None:
    with pytest.raises(ValueError, match="project ID"):
        FirebaseTokenVerifier("  ")


def test_certificates_are_fetched_from_googles_securetoken_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend.app.core import firebase_auth

    seen: dict[str, Any] = {}

    class _Response:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, str]:
            return {"k1": PUBLIC}

    def _get(url: str, timeout: float) -> _Response:
        seen.update(url=url, timeout=timeout)
        return _Response()

    monkeypatch.setattr(firebase_auth.requests, "get", _get)

    assert firebase_auth.fetch_firebase_certs() == {"k1": PUBLIC}
    assert seen["url"] == firebase_auth.FIREBASE_CERTS_URL
    assert seen["timeout"] == 5


def test_a_certificate_response_that_is_not_an_object_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from backend.app.core import firebase_auth

    class _Response:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> list[str]:
            return ["nope"]

    monkeypatch.setattr(firebase_auth.requests, "get", lambda url, timeout: _Response())

    with pytest.raises(ValueError, match="not an object"):
        firebase_auth.fetch_firebase_certs()
