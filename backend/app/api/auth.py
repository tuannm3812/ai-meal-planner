"""G4 request authentication: one FastAPI dependency per scope.

Each protected route declares the scope it needs, for example
``principal: PlansWrite``. The dependency resolves ``X-API-Key`` to a
Principal, checks the scope and applies the per-client rate limit. Routes then
use ``principal.client_id`` as the storage namespace, never a value the caller
can choose.
"""

from typing import Annotated

from fastapi import Depends, Header

from backend.app.core import telemetry
from backend.app.core.auth import Principal
from backend.app.core.container import ContainerDep
from backend.app.core.exceptions import (
    AuthenticationRequired,
    HistoryDisabled,
    InsufficientScope,
    RateLimited,
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
        x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    ) -> Principal:
        principal = container.auth.authenticate(x_api_key)
        if principal is None:
            raise AuthenticationRequired("missing or unknown X-API-Key")
        telemetry.annotate({"client_id": principal.client_id})
        if scope not in principal.scopes:
            raise InsufficientScope(f"client {principal.client_id!r} lacks scope {scope!r}")
        # Open local mode is a single developer; only keyed clients are limited.
        if container.auth.enforced:
            retry_after = container.rate_limiter.retry_after(principal.client_id)
            if retry_after is not None:
                raise RateLimited(f"client {principal.client_id!r} over limit", retry_after)
        return principal

    return _dependency


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
