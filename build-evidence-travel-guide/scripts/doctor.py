#!/usr/bin/env python3
"""Read-only dependency check for the travel-guide workflow."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


COMMANDS = ("agent-reach", "opencli", "pdftoppm")
MODULES = ("pypdf", "reportlab", "PIL")
VERSION_ARGS = {
    "agent-reach": ("--version",),
    "opencli": ("--version",),
    "pdftoppm": ("-v",),
}


def find_command(command: str) -> str | None:
    if command == "pdftoppm":
        bundled = (
            Path(sys.executable).resolve().parents[1]
            / "native"
            / "poppler"
            / "Library"
            / "bin"
            / "pdftoppm.exe"
        )
        if bundled.exists():
            return str(bundled)
    found = shutil.which(command)
    if found:
        return found
    home = Path.home()
    candidates = []
    if command == "agent-reach":
        candidates = [
            home / ".agent-reach-venv" / "Scripts" / "agent-reach.exe",
            home / ".agent-reach-venv" / "bin" / "agent-reach",
        ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def command_version(command: str) -> dict[str, object]:
    path = find_command(command)
    result: dict[str, object] = {"found": bool(path), "path": path}
    if not path:
        return result
    try:
        completed = subprocess.run(
            [path, *VERSION_ARGS[command]],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        output = (completed.stdout or completed.stderr).strip().splitlines()
        result["version"] = output[0] if output else "unknown"
    except (OSError, subprocess.SubprocessError) as error:
        result["version_error"] = str(error)
    return result


def main() -> int:
    report = {
        "python": {"version": sys.version.split()[0], "executable": sys.executable},
        "commands": {name: command_version(name) for name in COMMANDS},
        "python_modules": {
            name: bool(importlib.util.find_spec(name)) for name in MODULES
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    required = ("pdftoppm",)
    missing_required = [name for name in required if not report["commands"][name]["found"]]
    missing_required += [
        name for name in MODULES if not report["python_modules"][name]
    ]
    if missing_required:
        print("Missing PDF dependencies: " + ", ".join(missing_required))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
