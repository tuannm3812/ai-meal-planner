"""The guard that keeps the suite off the network."""

import pytest


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
