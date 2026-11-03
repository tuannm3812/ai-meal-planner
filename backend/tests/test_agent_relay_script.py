"""The agent relay must stop for the owner however long the newest entry is.

Codex, 2026-11-02 (P2): the stop check piped the entry into ``grep -q`` under
``pipefail``. On an entry of tens of KiB, grep exited at an early "Needs Mike"
before tail finished writing, tail died of SIGPIPE, the pipeline counted as
"no match" and the next agent ran. These run the real script in a scratch repo
with a stub agent that must never be called.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "agent_relay.sh"


@pytest.mark.skipif(shutil.which("git") is None, reason="needs git")
@pytest.mark.parametrize("filler_lines", [0, 4000], ids=["short", "about-140-KiB"])
def test_an_entry_that_needs_mike_stops_the_relay(tmp_path: Path, filler_lines: int) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "docs").mkdir()
    filler = "".join(f"Line {n} of a long review entry.\n" for n in range(filler_lines))
    (tmp_path / "docs" / "5_agent_log.md").write_text(
        "# Log\n\n## 2026-11-02 — Claude — a long entry\n\nNeeds Mike: approve this.\n\n" + filler,
        encoding="utf-8",
    )
    ran = tmp_path / "agent-ran"
    stub = tmp_path / "stub-agent.sh"
    stub.write_text(f"#!/bin/sh\ntouch '{ran}'\n", encoding="utf-8")
    stub.chmod(0o755)

    completed = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=tmp_path,
        env={**os.environ, "START_NOW": "1", "CODEX_CMD": str(stub), "CLAUDE_CMD": str(stub)},
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stderr
    assert 'Stopped: the newest entry says "Needs Mike".' in completed.stdout
    assert not ran.exists()
