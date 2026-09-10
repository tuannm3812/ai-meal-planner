"""The guard that keeps the suite off the network."""

import socket

import pytest

# Captured at collection time, before any test's autouse fixtures run, so this
# is the interpreter's real, unpatched method - the thing to compare against
# to prove a test was NOT patched, without ever dialing out.
_REAL_SOCKET_CONNECT = socket.socket.connect


def test_a_real_network_call_fails_the_test() -> None:
    """Any test reaching the internet must fail loudly, not silently succeed.

    The spec requires no network access in CI. Without this, a misconfigured
    API key would turn unit tests into flaky integration tests.
    """
    from urllib.request import urlopen

    with pytest.raises(RuntimeError, match="network access"):
        urlopen("https://example.invalid/should-never-be-called", timeout=1)


def test_a_raw_socket_connection_fails_the_test() -> None:
    """A bare socket to an IP must be blocked too, not just urlopen.

    An earlier version of the guard patched only ``urlopen`` and
    ``socket.create_connection``, which left ``socket.connect`` to a literal IP
    wide open - no DNS lookup, no urllib, straight out to the network.
    """
    import socket

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.settimeout(1)
    with pytest.raises(RuntimeError, match="network access"):
        connection.connect(("93.184.216.34", 80))


def test_create_connection_fails_the_test() -> None:
    """The primitive most HTTP client libraries build on must be blocked."""
    import socket

    with pytest.raises(RuntimeError, match="network access"):
        socket.create_connection(("93.184.216.34", 80), timeout=1)


def test_connect_ex_fails_the_test() -> None:
    """``connect_ex`` is a separate C-level entry point from ``connect``.

    Some libraries use it directly (it returns an errno instead of raising),
    so the guard must patch it too rather than relying on callers to go
    through ``connect``. A literal IP is used, not a hostname, because DNS
    resolution fails in ``getaddrinfo`` before ``connect_ex`` is ever reached
    and would test the wrong thing.
    """
    import socket

    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.settimeout(1)
    with pytest.raises(RuntimeError, match="network access"):
        connection.connect_ex(("93.184.216.34", 80))


@pytest.mark.allow_network
def test_allow_network_marker_opts_out_of_the_guard() -> None:
    """The ``allow_network`` marker must actually disable the patch.

    This makes no real network call - that would make the suite flaky and
    slow. It only proves the guard's own opt-out path ran: with the marker
    applied, ``_block_network`` returns before calling ``monkeypatch.setattr``,
    so ``socket.socket.connect`` must still be the interpreter's real,
    unpatched method rather than the guard's ``_blocked`` sentinel.
    """
    assert socket.socket.connect is _REAL_SOCKET_CONNECT
