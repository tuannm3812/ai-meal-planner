"""A signed-in user's own account: profile, and deleting everything (DEC-43).

These routes act only for the token's uid. An API-key client has no account,
so it gets 403 here; a deployment without Firestore gets 501.
"""

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from backend.app.api.auth import FeedbackWrite, HistoryRead
from backend.app.api.errors import AUTH_ERRORS, error_responses
from backend.app.core.auth import Principal
from backend.app.core.container import Container, ContainerDep
from backend.app.core.exceptions import AccountsUnavailable, InsufficientScope, ProfileNotFound
from backend.app.repositories.base import AccountStore
from backend.app.schemas.requests import AccountProfileRequest
from backend.app.schemas.responses import AccountDeletedResponse, AccountResponse

router = APIRouter()


def _account(container: Container, principal: Principal) -> tuple[AccountStore, str]:
    """Return the account store and the caller's uid, or refuse.

    Args:
        container: The application's dependency container.
        principal: The authenticated caller.

    Returns:
        The store and the uid.

    Raises:
        InsufficientScope: The caller is an API-key client, not a signed-in user.
        AccountsUnavailable: Storage is not Firestore.
    """
    if principal.user_id is None:
        raise InsufficientScope(f"client {principal.client_id!r} has no account")
    store = container.user_profiles
    if not isinstance(store, AccountStore):
        raise AccountsUnavailable("account route without an account store")
    return store, principal.user_id


@router.get(
    "/me/profile",
    response_model=AccountResponse,
    responses=error_responses(*AUTH_ERRORS, ProfileNotFound, AccountsUnavailable),
)
async def get_my_profile(container: ContainerDep, principal: HistoryRead) -> AccountResponse:
    """Return the signed-in user's saved profile and shopping location.

    Args:
        container: The application's dependency container.
        principal: The signed-in user.

    Returns:
        The saved profile.

    Raises:
        ProfileNotFound: 404 when the account has never saved one.
    """
    store, uid = _account(container, principal)
    record = await run_in_threadpool(store.get_account, uid, client_id=principal.client_id)
    if record is None:
        raise ProfileNotFound("account has no saved profile")
    return AccountResponse(**record)


@router.put(
    "/me/profile",
    response_model=AccountResponse,
    responses=error_responses(*AUTH_ERRORS, AccountsUnavailable),
)
async def put_my_profile(
    request: AccountProfileRequest, container: ContainerDep, principal: FeedbackWrite
) -> AccountResponse:
    """Save the signed-in user's profile and shopping location, replacing any before.

    Args:
        request: The profile fields and location.
        container: The application's dependency container.
        principal: The signed-in user.

    Returns:
        The saved profile.
    """
    store, uid = _account(container, principal)
    record = await run_in_threadpool(
        store.save_account,
        uid,
        request.profile.model_dump(),
        request.location,
        client_id=principal.client_id,
    )
    return AccountResponse(**record)


@router.delete(
    "/me",
    response_model=AccountDeletedResponse,
    responses=error_responses(*AUTH_ERRORS, AccountsUnavailable),
)
async def delete_me(container: ContainerDep, principal: FeedbackWrite) -> AccountDeletedResponse:
    """Delete everything the signed-in user stored: profile, plans and feedback.

    The browser then deletes the Firebase sign-in itself, so the API needs no
    admin rights over accounts.

    Args:
        container: The application's dependency container.
        principal: The signed-in user.

    Returns:
        How many plans and feedback records were deleted.
    """
    store, uid = _account(container, principal)
    deleted = await run_in_threadpool(store.delete_user, uid, client_id=principal.client_id)
    return AccountDeletedResponse(status="deleted", deleted=deleted)
