"""G4 request authentication: one FastAPI dependency per scope.

Each protected route declares the scope it needs, for example
``principal: PlansWrite``. The dependency resolves ``X-API-Key`` to a
Principal, checks the scope and applies the per-client rate limit. Routes then
use ``principal.client_id`` as the storage namespace, never a value the caller
can choose.

A signed-in user (DEC-43) sends a Firebase ID token as ``Authorization: Bearer``
instead. It resolves to the ``accounts`` namespace with the token's uid as
``principal.user_id``, and routes then use that uid as the user, never the
``user_id`` the caller sent (``user_for``).
"""

from typing import Annotated, TypeVar

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from backend.app.core import telemetry
from backend.app.core.auth import ACCOUNTS_CLIENT_ID, SCOPES, Principal
from backend.app.core.container import ContainerDep
from backend.app.core.exceptions import (
    AuthenticationRequired,
    HistoryDisabled,
    InsufficientScope,
    RateLimited,
)

# auto_error=False: a missing key reaches the dependency as None, so the API's
# own 401 (missing_or_invalid_api_key) is still the response. It also makes
# X-API-Key a declared security scheme in the OpenAPI contract.
_API_KEY = APIKeyHeader(
    name="X-API-Key",
    scheme_name="ApiKeyAuth",
    description="A client application's API key (README §8.1).",
    auto_error=False,
)
_BodyT = TypeVar("_BodyT", bound=BaseModel)

_BEARER = HTTPBearer(
    scheme_name="FirebaseAuth",
    description="A signed-in user's Firebase ID token (DEC-43).",
    auto_error=False,
)


def require_scope(scope: str):  # noqa: ANN201 - returns a FastAPI dependency
    """Build the dependency that admits a request holding ``scope``.

    Args:
        scope: One of ``core.auth.SCOPES``.

    Returns:
        A dependency resolving to the authenticated Principal.
    """

    def _dependency(
        container: ContainerDep,
        x_api_key: Annotated[str | None, Security(_API_KEY)] = None,
        bearer: Annotated[HTTPAuthorizationCredentials | None, Security(_BEARER)] = None,
    ) -> Principal:
        if bearer is not None:
            if x_api_key:
                raise AuthenticationRequired("both X-API-Key and a bearer token were sent")
            principal = _account_principal(container, bearer.credentials)
        else:
            principal = container.auth.authenticate(x_api_key)
        if principal is None:
            raise AuthenticationRequired("missing or unknown X-API-Key or token")
        telemetry.annotate({"client_id": principal.client_id})
        if scope not in principal.scopes:
            raise InsufficientScope(f"client {principal.client_id!r} lacks scope {scope!r}")
        # Open local mode is a single developer; keyed clients and accounts are limited.
        if container.auth.enforced or principal.user_id:
            retry_after = container.rate_limiter.retry_after(principal.rate_key)
            if retry_after is not None:
                raise RateLimited(f"client {principal.client_id!r} over limit", retry_after)
        return principal

    return _dependency


def _account_principal(container: ContainerDep, token: str) -> Principal | None:
    """Resolve a bearer token to a signed-in user's principal, or None.

    Args:
        container: The application's dependency container.
        token: The bearer token's value.

    Returns:
        The account principal, or None when accounts are off or the token is
        not a valid Firebase ID token for this project.
    """
    verifier = container.token_verifier
    if verifier is None:
        return None
    uid = verifier.verify(token)
    if uid is None:
        return None
    return Principal(client_id=ACCOUNTS_CLIENT_ID, scopes=frozenset(SCOPES), user_id=uid)


def user_for(principal: Principal, requested: str) -> str:
    """Return the user a request acts for.

    An API-key client names its users itself, so ``requested`` stands. A
    signed-in user is always the token's uid: a body's ``user_id`` is replaced
    by it, and a path naming anyone else is refused.

    Args:
        principal: The authenticated caller.
        requested: The ``user_id`` the caller sent.

    Returns:
        The user id to read or write.

    Raises:
        InsufficientScope: When a signed-in user names another user.
    """
    if principal.user_id is None:
        return requested
    if requested != principal.user_id:
        raise InsufficientScope("a signed-in user named another user_id")
    return principal.user_id


def body_for(principal: Principal, request: _BodyT) -> _BodyT:
    """Return a request body acting for the caller's own user.

    A signed-in user's body ``user_id`` is replaced by the token's uid, so a
    stored record can only ever belong to the account that wrote it. An
    API-key client's body is returned unchanged.

    Args:
        principal: The authenticated caller.
        request: A request model with a ``user_id`` field.

    Returns:
        The request, or a copy carrying the uid.
    """
    if principal.user_id is None:
        return request
    return request.model_copy(update={"user_id": principal.user_id})


def _require_history_enabled(container: ContainerDep) -> None:
    """Refuse history and feedback on a hosted, stateless deployment (G6).

    Declare it *after* the principal, so authentication is checked first.

    Args:
        container: The application's dependency container.

    Raises:
        HistoryDisabled: When HOSTED_MODE is on.
    """
    if container.settings.hosted_mode:
        raise HistoryDisabled("history route called on a hosted deployment")


PlansWrite = Annotated[Principal, Depends(require_scope("plans:write"))]
FeedbackWrite = Annotated[Principal, Depends(require_scope("feedback:write"))]
HistoryRead = Annotated[Principal, Depends(require_scope("history:read"))]
HistoryEnabled = Annotated[None, Depends(_require_history_enabled)]
