import importlib.resources
import re
import subprocess
from pathlib import Path

from ..helpers import ConfigurationError


def get_files_to_check(dir: str, regex: str) -> list[str]:
    files = []
    regex = re.compile(regex)
    for file in Path(dir).rglob("*"):
        if file.is_file() and regex.match(file.name):
            files.append(file.name)

    return files


def run_checkstyle(java_file: str, config_path: str | None) -> tuple[str, str]:
    # Get the absolute paths to the checkstyle jar and config in the package.
    with (
        importlib.resources.path(
            "java_gradescope_autograder_helper.checkstyle",
            "checkstyle-10.21.2-all.jar",
        ) as jar_path,
        importlib.resources.path(
            "java_gradescope_autograder_helper.checkstyle",
            "bowdoin_checks.xml",
        ) as default_config_path,
    ):
        config_path = Path(config_path) if config_path else default_config_path
        cmd = [
            "java",
            "-jar",
            str(jar_path),
            "-c",
            str(config_path),
            java_file,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        print("my checkstyle stdout", result.stdout)
        print("my checkstyle stderr", result.stderr)

        if (
            "Audit done." not in result.stdout
            and "Audit done." not in result.stderr
        ):
            raise ConfigurationError(
                f"Checkstyle failed ({result.returncode}):\n{' '.join(cmd)}\n\nOutput:\n\n{result.stdout}\n\nError:\n\n{result.stderr}"
            )

        return result.stdout, result.stderr


def get_total_errors(out: str) -> int:
    match = re.fullmatch(r"Checkstyle ends with (\d+) errors\.", out)
    return int(match.group(1)) if match else 0


def default_evaluation(
    out: str, err: str, total_errors: int
) -> tuple[float, str]:
    score_percentage = 1 - (total_errors * 0.1)
    score_percentage = 0 if score_percentage < 0 else score_percentage
    return score_percentage, f"Style violations found: {total_errors}."
