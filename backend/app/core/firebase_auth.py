"""Firebase ID token verification for signed-in users (DEC-43).

The React app signs in with Firebase Auth (Google, or anonymously on a first
hosted visit) and sends the ID token as ``Authorization: Bearer <token>``. This
module checks that token the way Firebase documents: an RS256 signature by one
of Google's published ``securetoken`` keys, the project as audience, the
project's issuer, an unexpired token and a non-empty subject. The subject is the
user's uid, which is all the API ever keeps of the account.

``google-auth`` does the cryptography. Its own ``verify_firebase_token`` fetches
the certificates on every call, so this class caches them for an hour and
refetches once when a token names a key it has not seen (Google rotates keys).
"""

import base64
import json
import logging
import time
from collections.abc import Callable, Mapping

import requests
from google.auth import exceptions as google_auth_exceptions
from google.auth import jwt

logger = logging.getLogger(__name__)

FIREBASE_CERTS_URL = (
    "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
)
CERT_CACHE_SECONDS = 3600
CLOCK_SKEW_SECONDS = 10
_MAX_UID_LENGTH = 128  # Firebase's own limit on a uid


def fetch_firebase_certs() -> dict[str, str]:
    """Download Google's current Firebase token-signing certificates.

    Returns:
        A mapping of key id to PEM certificate.
    """
    response = requests.get(FIREBASE_CERTS_URL, timeout=5)
    response.raise_for_status()
    certs = response.json()
    if not isinstance(certs, dict):
        raise ValueError("Firebase certificate response is not an object")
    return {str(kid): str(pem) for kid, pem in certs.items()}


class FirebaseTokenVerifier:
    """Resolves a Firebase ID token to the signed-in user's uid."""

    def __init__(
        self,
        project_id: str,
        *,
        fetch_certs: Callable[[], Mapping[str, str]] = fetch_firebase_certs,
        clock: Callable[[], float] = time.time,
    ) -> None:
        """Configure verification for one Firebase project.

        Args:
            project_id: The Firebase (GCP) project ID the tokens must be issued for.
            fetch_certs: Source of the signing certificates, injectable for tests.
            clock: Wall-clock time source for the certificate cache.
        """
        if not project_id.strip():
            raise ValueError("FirebaseTokenVerifier needs a project ID.")
        self.project_id = project_id
        self.issuer = f"https://securetoken.google.com/{project_id}"
        self._fetch_certs = fetch_certs
        self._clock = clock
        self._certs: dict[str, str] = {}
        self._fetched_at = float("-inf")

    def verify(self, token: str | None) -> str | None:
        """Return the uid a valid token was issued to.

        Args:
            token: The bearer token, if any.

        Returns:
            The uid, or None when the token is missing, malformed, forged,
            expired, for another project, or the certificates can't be fetched.
            Callers turn None into a 401; the reason is logged, never returned.
        """
        if not token:
            return None
        try:
            claims = self._decode(token)
        except (ValueError, google_auth_exceptions.GoogleAuthError) as exc:
            logger.info("Rejected a Firebase ID token: %s", type(exc).__name__)
            return None
        except requests.RequestException as exc:
            logger.warning("Could not fetch Firebase certificates: %s", type(exc).__name__)
            return None
        if claims.get("iss") != self.issuer:
            logger.info("Rejected a Firebase ID token: wrong issuer")
            return None
        uid = claims.get("sub")
        if not isinstance(uid, str) or not uid or len(uid) > _MAX_UID_LENGTH:
            logger.info("Rejected a Firebase ID token: bad subject")
            return None
        return uid

    def _decode(self, token: str) -> Mapping[str, object]:
        certs = self._current_certs(force=False)
        kid = _key_id(token)
        if kid is not None and kid not in certs:
            certs = self._current_certs(force=True)
        return jwt.decode(
            token,
            certs=certs,
            audience=self.project_id,
            clock_skew_in_seconds=CLOCK_SKEW_SECONDS,
        )

    def _current_certs(self, *, force: bool) -> dict[str, str]:
        now = self._clock()
        if force or not self._certs or now - self._fetched_at >= CERT_CACHE_SECONDS:
            self._certs = dict(self._fetch_certs())
            self._fetched_at = now
        return self._certs


def _key_id(token: str) -> str | None:
    """Read the unverified ``kid`` header, only to pick which certificate to try."""
    header = token.partition(".")[0]
    try:
        decoded = base64.urlsafe_b64decode(header + "=" * (-len(header) % 4))
        kid = json.loads(decoded).get("kid")
    except (ValueError, AttributeError):
        return None
    return kid if isinstance(kid, str) else None
