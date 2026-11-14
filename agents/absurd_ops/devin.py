"""Devin-backed editorial sessions.

The Daily Absurd's writing staff *is* Devin. Each quality role (satirical
writer, comedy editor, safety editor) spawns a bounded, non-interactive Devin
session (`devin -p`) pointed at a prompt file. Sessions write their output to
files inside the queue; agents read the files back. No external LLM keys are
required.
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from . import config


@dataclass
class DevinResult:
    ok: bool
    output_path: Path | None
    stdout: str
    error: str
    seconds: float


def run_session(
    prompt_path: Path,
    expect_file: Path,
    timeout: int | None = None,
    workdir: Path | None = None,
) -> DevinResult:
    """Run `devin -p --prompt-file prompt` and wait for `expect_file` to appear."""
    if not config.DEVIN_ENABLED:
        return DevinResult(False, None, "", "devin disabled via ABSURD_DEVIN_ENABLED=0", 0)

    if expect_file.exists():
        expect_file.unlink()

    cmd = [
        config.DEVIN_BIN,
        "-p",
        "--prompt-file",
        str(prompt_path),
        "--permission-mode",
        config.DEVIN_PERMISSION_MODE,
    ]
    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(workdir or config.REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout or config.DEVIN_TIMEOUT_SECONDS,
        )
        elapsed = time.time() - start
        stdout = (proc.stdout or "") + (proc.stderr or "")
        if expect_file.exists():
            return DevinResult(True, expect_file, stdout, "", elapsed)
        return DevinResult(
            False, None, stdout[-4000:],
            f"session finished (rc={proc.returncode}) but did not produce {expect_file}",
            elapsed,
        )
    except subprocess.TimeoutExpired:
        return DevinResult(False, None, "", "devin session timed out", time.time() - start)
    except FileNotFoundError:
        return DevinResult(False, None, "", "devin binary not found", time.time() - start)


def read_json_output(path: Path) -> dict | None:
    """Read a JSON object from a file Devin produced; tolerate prose wrapping."""
    try:
        text = path.read_text()
    except OSError:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return None
    return None
