from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


COMMAND_OUTPUT_LIMIT = 60_000
DEFAULT_TIMEOUT_SECONDS = float(os.environ.get("AI_DEBUGGER_COMMAND_TIMEOUT_SECONDS", "25"))
SUPPORTED_PREFIXES = (
    ("pytest",),
    ("python", "-m", "pytest"),
    ("python3", "-m", "pytest"),
    ("python", "-m", "unittest"),
    ("python3", "-m", "unittest"),
    ("python", "manage.py", "test"),
    ("python3", "manage.py", "test"),
    ("npm", "test"),
    ("npm", "run", "test"),
    ("pnpm", "test"),
    ("yarn", "test"),
    ("mvn", "test"),
    ("go", "test"),
    ("cargo", "test"),
    ("bundle", "exec", "rspec"),
)
TRUTHY_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class CommandCapture:
    command: str = ""
    attempted: bool = False
    ran: bool = False
    output: str = ""
    exit_code: int | None = None
    timed_out: bool = False
    error_message: str = ""

    @property
    def has_output(self) -> bool:
        return bool(self.output.strip())

    @property
    def display_output(self) -> str:
        return self.output or self.error_message


def capture_repro_command(repo_root: Path | None, repro_command: str) -> CommandCapture:
    command = repro_command.strip()
    if not command:
        return CommandCapture()

    if not command_execution_enabled():
        return CommandCapture(
            command=command,
            attempted=True,
            error_message=(
                "Command execution is disabled on this deployment. Enable AI_DEBUGGER_ENABLE_COMMAND_EXECUTION=1 "
                "for trusted local or demo use."
            ),
        )

    if not repo_root:
        return CommandCapture(
            command=command,
            attempted=True,
            error_message="Add a repo ZIP or public GitHub URL before running a repro command.",
        )

    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return CommandCapture(
            command=command,
            attempted=True,
            error_message=f"Could not parse the repro command: {exc}",
        )

    if not argv:
        return CommandCapture(
            command=command,
            attempted=True,
            error_message="Enter a command such as pytest, python manage.py test, npm test, or mvn test.",
        )

    if not _is_supported_command(argv):
        return CommandCapture(
            command=command,
            attempted=True,
            error_message=(
                "For this MVP, command capture supports common test and build repro commands such as "
                "pytest, python manage.py test, npm test, and mvn test."
            ),
        )

    env = {
        **os.environ,
        "CI": "1",
        "FORCE_COLOR": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUNBUFFERED": "1",
        "TERM": "dumb",
    }

    try:
        completed = subprocess.run(
            argv,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            env=env,
        )
    except FileNotFoundError as exc:
        return CommandCapture(
            command=command,
            attempted=True,
            error_message=f"Command could not start because {exc.filename} is not available in PATH.",
        )
    except subprocess.TimeoutExpired as exc:
        return CommandCapture(
            command=command,
            attempted=True,
            ran=True,
            output=_format_output(command, exc.stdout, exc.stderr, None, timed_out=True),
            timed_out=True,
            error_message=f"Command timed out after {int(DEFAULT_TIMEOUT_SECONDS)} seconds.",
        )
    except OSError as exc:
        return CommandCapture(
            command=command,
            attempted=True,
            error_message=f"Command could not start: {exc}",
        )

    output = _format_output(
        command,
        completed.stdout,
        completed.stderr,
        completed.returncode,
        timed_out=False,
    )

    return CommandCapture(
        command=command,
        attempted=True,
        ran=True,
        output=output,
        exit_code=completed.returncode,
        error_message=(
            ""
            if output.strip()
            else "The command finished, but no stdout or stderr was captured for triage."
        ),
    )


def _is_supported_command(argv: list[str]) -> bool:
    return any(tuple(argv[: len(prefix)]) == prefix for prefix in SUPPORTED_PREFIXES)


def command_execution_enabled() -> bool:
    explicit = os.environ.get("AI_DEBUGGER_ENABLE_COMMAND_EXECUTION", "").lower()
    if explicit:
        return explicit in TRUTHY_VALUES
    return os.environ.get("DJANGO_DEBUG", "1").lower() in TRUTHY_VALUES


def _format_output(
    command: str,
    stdout: str | bytes | None,
    stderr: str | bytes | None,
    exit_code: int | None,
    *,
    timed_out: bool,
) -> str:
    stdout_text = _coerce_text(stdout).strip()
    stderr_text = _coerce_text(stderr).strip()

    parts = [f"$ {command}"]
    if timed_out:
        parts.append(f"Timed out after {int(DEFAULT_TIMEOUT_SECONDS)} seconds.")
    elif exit_code is not None:
        parts.append(f"Exit code: {exit_code}")

    if stdout_text:
        parts.extend(["", "stdout:", stdout_text])
    if stderr_text:
        parts.extend(["", "stderr:", stderr_text])
    if not stdout_text and not stderr_text:
        parts.extend(["", "No stdout or stderr was captured."])

    return _truncate_output("\n".join(parts).strip())


def _coerce_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return value


def _truncate_output(value: str) -> str:
    if len(value) <= COMMAND_OUTPUT_LIMIT:
        return value
    return value[: COMMAND_OUTPUT_LIMIT - 40].rstrip() + "\n\n[output truncated]"
