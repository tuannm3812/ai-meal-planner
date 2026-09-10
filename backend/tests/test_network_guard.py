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
