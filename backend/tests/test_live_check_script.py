"""The G6 acceptance check must fail whenever its evidence is incomplete.

Codex, 2026-10-10 (P2 on PR #17): `scripts/live_check.sh` required the
*union* of instance ids across the four history routes to reach
EXPECT_INSTANCES, counted a missing id as an instance, and never required it
of the anonymous sample. A deployment where one route was only ever seen on one
instance still passed. Codex's follow-up: no request had a time limit, so a
stalled response held the check open instead of failing it. Its verification
(P2 on 90164d6): curl's exit status was discarded, so a transfer that timed out
or was cut short after a correct status, id and JSON code still counted.

These tests run the real script against a local HTTP fixture that plays a
hosted deployment and attributes each response to a chosen instance. No Docker
or GCP is needed. Seeing N ids proves the sampled instances answered, not that
there are no others.
"""

import json
import os
import shutil
import socketserver
import subprocess
import threading
import time
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "live_check.sh"
KEY, OLD_KEY = "current-key", "revoked-key"
CHECKS = ["meal-plans", "meal-feedback", "saved-meals", "post-feedback", "anonymous", "revoked"]


def _check_of(method: str, path: str, key: str | None) -> str:
    """Which of the script's checks a request belongs to."""
    if path == "/health":
        return "health"
    if path == "/generate-meal-plan":
        return "generate"
    if key is None:
        return "anonymous"
    if key == OLD_KEY:
        return "revoked"
    if method == "POST" and path == "/meal-feedback":
        return "post-feedback"
    return path.split("/")[1]


def _answer(check: str) -> tuple[int, dict[str, object]]:
    """What a correct hosted deployment returns."""
    if check == "health":
        return 200, {"environment": "production", "services": {"hosted_mode": True}}
    if check == "generate":
        return 200, {"status": "success"}
    if check in {"anonymous", "revoked"}:
        return 401, {"code": "missing_or_invalid_api_key"}
    return 501, {"code": "history_disabled_stateless"}


@contextmanager
def _deployment(behaviour: dict[str, str], default: str = "both") -> Iterator[str]:
    """Serve a hosted deployment; `behaviour` maps a check to how it is answered.

    - both: alternate instances a and b (every response correct);
    - only-a / only-b: always that instance;
    - missing: alternate instance a and no X-Instance-Id at all;
    - stall: alternate a and b, but every third answer takes 5 seconds;
    - drop: alternate a and b, but every third request is closed unanswered;
    - late-stall / truncate: alternate a and b, but every third answer sends its
      status, id and complete JSON while promising ten more bytes, then stalls
      (late-stall) or closes the connection (truncate).

    Stalling every third request leaves both instances among the rest, so a
    check that left the stalled ones out of its sample would still see two.
    """
    seen: Counter[str] = Counter()
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def _serve(self) -> None:
            length = int(self.headers.get("Content-Length") or 0)
            self.rfile.read(length)
            check = _check_of(self.command, self.path, self.headers.get("X-API-Key"))
            with lock:
                n = seen[check]
                seen[check] += 1
            mode = behaviour.get(check, default)
            second, third = n % 2 == 1, n % 3 == 2
            if mode == "drop" and third:
                self.close_connection = True
                return
            if mode == "stall" and third:
                time.sleep(5)
            instance = {"only-a": "a", "only-b": "b"}.get(mode, "b" if second else "a")
            if mode == "missing" and second:
                instance = None
            status, body = _answer(check)
            payload = json.dumps(body).encode()
            short = mode in {"late-stall", "truncate"} and third
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload) + (10 if short else 0)))
                if instance:
                    self.send_header("X-Instance-Id", f"instance-{instance}")
                self.end_headers()
                self.wfile.write(payload)
                if short:
                    self.wfile.flush()
                    if mode == "late-stall":
                        time.sleep(5)
                    self.close_connection = True
            except (BrokenPipeError, ConnectionResetError):
                pass  # the client gave up: that is what a stall test expects

        do_GET = do_POST = _serve

        def log_message(self, *_: object) -> None:
            pass

    # Not http.server's HTTPServer: its server_bind does a reverse-DNS lookup
    # (socket.getfqdn) that can take over 30 seconds, and nothing here needs it.
    server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def _live_check(
    url: str, *, revocation: bool = True, **extra_env: str
) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "MEAL_PLANNER_KEY": KEY,
        "OLD_KEY": OLD_KEY if revocation else "",
        "EXPECT_INSTANCES": "2",
        "REQUESTS": "4",
        "REQUEST_TIMEOUT": "2",
        **extra_env,
    }
    return subprocess.run(
        ["bash", str(SCRIPT), url], env=env, capture_output=True, text=True, timeout=60
    )


def test_a_deployment_seen_on_two_instances_for_every_check_passes() -> None:
    """The control: every check is answered correctly by both instances."""
    with _deployment({}) as url:
        result = _live_check(url)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "live check passed" in result.stdout
    for check in CHECKS:
        assert f"{check} -> " in result.stdout and "from 2 instance(s)" in result.stdout


@pytest.mark.parametrize("check", CHECKS)
def test_each_check_must_itself_reach_the_instance_count(check: str) -> None:
    """One check seen on one instance fails, however many the others saw."""
    with _deployment({check: "only-a"}) as url:
        result = _live_check(url)

    assert result.returncode != 0, result.stdout
    assert f"{check}: only 1 instance(s) answered" in result.stdout
    assert "live check passed" not in result.stdout


def test_codex_reproduction_split_across_routes_fails() -> None:
    """Codex's fixture: saved-meals only on b, everything else only on a.

    Run without OLD_KEY, as Codex ran it: the revoked check already required
    its own two instances, so it would mask the gap.
    """
    with _deployment({"saved-meals": "only-b"}, default="only-a") as url:
        result = _live_check(url, revocation=False)

    assert result.returncode != 0, result.stdout
    assert "live check passed" not in result.stdout


def test_a_response_without_an_instance_id_is_not_counted_as_one() -> None:
    """Instance a plus unattributed answers is one instance, not two."""
    with _deployment({"meal-plans": "missing"}, default="only-a") as url:
        result = _live_check(url, revocation=False)

    assert result.returncode != 0, result.stdout
    assert "meal-plans: only 1 instance(s) answered" in result.stdout


@pytest.mark.parametrize("mode", ["stall", "drop"])
def test_an_unanswered_request_fails_the_check(mode: str) -> None:
    """A stalled or dropped request fails the check; it is never waited out or skipped."""
    with _deployment({"meal-plans": mode}) as url:
        result = _live_check(url)

    assert result.returncode != 0, result.stdout
    assert "meal-plans: unexpected responses" in result.stdout
    assert "live check passed" not in result.stdout


@pytest.mark.parametrize("mode", ["late-stall", "truncate"])
def test_a_failed_transfer_fails_even_when_what_arrived_looks_right(mode: str) -> None:
    """Codex's reproduction: 501, the instance id and complete JSON arrive, then
    the transfer times out (curl exit 28) or is cut short (exit 18)."""
    with _deployment({"meal-plans": mode}) as url:
        result = _live_check(url)

    assert result.returncode != 0, result.stdout
    assert "meal-plans: unexpected responses" in result.stdout
    assert "curl-exit-" in result.stdout
    assert "live check passed" not in result.stdout


# Stands in for python3 on PATH: the first meal-plans probe to parse its result
# fails, as a probe can if anything in it errors under `set -e`.
FAKE_PYTHON3 = """#!/usr/bin/env bash
for arg in "$@"; do
  case "$arg" in
    */meal-plans.*) mkdir "$CRASH_ONCE" 2>/dev/null && exit 1 ;;
  esac
done
exec "$REAL_PYTHON3" "$@"
"""


def test_a_probe_that_dies_fails_the_check(tmp_path: Path) -> None:
    """A probe that exits without recording a line must not shrink the sample.

    The other three meal-plans answers still come from both instances, so only
    the probe's own exit status can reveal the loss.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "python3"
    fake.write_text(FAKE_PYTHON3)
    fake.chmod(0o755)
    real_python3 = shutil.which("python3")
    assert real_python3 is not None

    with _deployment({}) as url:
        result = _live_check(
            url,
            PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            REAL_PYTHON3=real_python3,
            CRASH_ONCE=str(tmp_path / "crashed"),
        )

    assert (tmp_path / "crashed").is_dir(), "precondition: one probe was made to fail"
    assert result.returncode != 0, result.stdout
    assert "meal-plans: 1 probe(s) did not finish" in result.stdout
    assert "live check passed" not in result.stdout
