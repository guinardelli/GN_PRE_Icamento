"""Release readiness checks for GN_PRE_Icamento."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = ("app", "tests")
FORBIDDEN_PATTERNS = (
    "TODO",
    "FIXME",
    "HACK",
    "NotImplemented",
    "except Exception",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run release readiness checks.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when tracked generated artifacts or screenshots are present.",
    )
    args = parser.parse_args()

    failures: list[str] = []
    warnings: list[str] = []

    _check_python_version(failures)
    _run_command(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests"],
        "unit tests",
        failures,
    )
    _run_command(["git", "diff", "--check"], "git diff --check", failures)
    _check_long_python_lines(failures)
    _check_forbidden_patterns(failures)
    _check_tracked_artifacts(warnings)

    warnings_escalated = args.strict and bool(warnings)
    if warnings_escalated:
        failures.extend(warnings)

    _print_report(
        failures,
        warnings,
        strict=args.strict,
        warnings_escalated=warnings_escalated,
    )
    return 1 if failures else 0


def _check_python_version(failures: list[str]) -> None:
    if sys.version_info < (3, 11):
        failures.append("Python 3.11+ is required.")


def _run_command(command: list[str], label: str, failures: list[str]) -> None:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        details = (result.stdout + result.stderr).strip()
        failures.append(f"{label} failed:\n{details}")


def _check_long_python_lines(failures: list[str]) -> None:
    long_lines: list[str] = []
    for folder in SOURCE_DIRS:
        for path in (ROOT / folder).rglob("*.py"):
            for line_number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(),
                start=1,
            ):
                if len(line) > 99:
                    rel_path = path.relative_to(ROOT)
                    long_lines.append(f"{rel_path}:{line_number}:{len(line)}")

    if long_lines:
        failures.append("Python lines above 99 chars:\n" + "\n".join(long_lines))


def _check_forbidden_patterns(failures: list[str]) -> None:
    matches: list[str] = []
    for folder in SOURCE_DIRS:
        for path in (ROOT / folder).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in text:
                    rel_path = path.relative_to(ROOT)
                    matches.append(f"{rel_path}: {pattern}")

    if matches:
        failures.append("Forbidden source markers found:\n" + "\n".join(matches))


def _check_tracked_artifacts(warnings: list[str]) -> None:
    tracked_pyc = _git_ls_files("*.pyc")
    tracked_screenshots = _git_ls_files("screenshot_*.png")

    if tracked_pyc:
        warnings.append(
            f"{len(tracked_pyc)} tracked .pyc files remain:\n"
            + "\n".join(tracked_pyc)
        )
    if tracked_screenshots:
        warnings.append(
            f"{len(tracked_screenshots)} tracked screenshots require a decision:\n"
            + "\n".join(tracked_screenshots)
        )


def _git_ls_files(pattern: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", pattern],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def _print_report(
    failures: list[str],
    warnings: list[str],
    strict: bool,
    warnings_escalated: bool,
) -> None:
    print("Release check: GN_PRE_Icamento")
    print(f"Mode: {'strict' if strict else 'normal'}")
    print()

    if failures:
        print("FAILURES")
        for failure in failures:
            print(f"- {failure}")
    else:
        print("Failures: none")

    print()
    if warnings_escalated:
        print("Warnings: escalated to failures in strict mode")
    elif warnings:
        print("WARNINGS")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("Warnings: none")


if __name__ == "__main__":
    raise SystemExit(main())
