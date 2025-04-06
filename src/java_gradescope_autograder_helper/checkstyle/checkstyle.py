import importlib.resources
import re
from pathlib import Path
from subprocess import run
from typing import Any, cast

from ..helpers import (
    SUBMISSION_DIR,
    ConfigurationError,
    find_absolute_path,
)


def check_style(tests_module: object) -> dict[str, Any] | None:
    """
    Checks the Java source files for style violations using CheckStyle.
    """

    check_style = validate_checkstyle_config(tests_module)
    if check_style is None:
        return None

    checks_config_file = check_style.get("config_file", None)
    if checks_config_file is not None:
        config_file_str = cast(str, checks_config_file)
        checks_config_file = find_absolute_path(config_file_str)

    check_style_regex = check_style.get("file_regex", r".*\.java")

    absolute_submission_path = find_absolute_path(SUBMISSION_DIR)
    files_to_check = get_files_to_check(
        absolute_submission_path, check_style_regex
    )

    violations = 0
    for file in files_to_check:
        _, stderr = run_checkstyle(
            find_absolute_path(file, cwd=absolute_submission_path),
            checks_config_file,
        )
        violations += get_total_errors(stderr)

    score_percentage, feedback = default_evaluation("", "", violations)
    max_score = check_style.get("max_score", 0)

    return {
        "name": "Style",
        "score": max_score * score_percentage,
        "max_score": max_score,
        "output": feedback,
        "visibility": "visible",
        "status": "passed" if violations == 0 else "failed",
    }


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
        config_path = config_path or str(default_config_path)
        cmd = [
            "java",
            "-jar",
            str(jar_path),
            "-c",
            config_path,
            java_file,
        ]
        result = run(cmd, capture_output=True)
        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")

        # Checkstyle stderr contains the number of errors found and I believe
        # the error code is also sometimes the number of errors found, so
        # I have to check if it was unsuccessful by doing this.
        if "Audit done." not in stdout:
            raise ConfigurationError(
                f"Checkstyle failed ({result.returncode}):\n{' '.join(cmd)}\n\nOutput:\n\n{result.stdout}\n\nError:\n\n{result.stderr}"
            )

        return stdout, stderr


def default_evaluation(
    out: str, err: str, total_errors: int
) -> tuple[float, str]:
    score_percentage = 1 - (total_errors * 0.1)
    score_percentage = 0 if score_percentage < 0 else score_percentage
    return score_percentage, f"Style violations found: {total_errors}."


def get_total_errors(err: str) -> int:
    match = re.search(r"Checkstyle ends with (\d+) errors\.", err)
    return int(match.group(1)) if match else 0


def get_files_to_check(dir: str, regex: str) -> list[str]:
    files: list[str] = []
    pattern = re.compile(regex)
    for file in Path(dir).rglob("*"):
        if file.is_file() and pattern.match(file.name):
            files.append(file.name)

    return files


def validate_checkstyle_config(
    tests_module: object,
) -> dict[str, Any] | None:
    # CHECK_STYLE = {
    #     "config_file": None,
    #     "file_regex": r"(BoggleBoard|Recursion)\.java",
    #     "max_score": 0,
    #     "eval_function": None,
    # }

    config = getattr(tests_module, "CHECK_STYLE", None)
    if config is None:
        return None

    if not isinstance(config, dict):
        raise ConfigurationError('"CHECK_STYLE" must be a dictionary')

    style_config: dict[str, Any] = config
    config_file = style_config.get("config_file", None)
    if config_file is not None and not isinstance(config_file, str):
        raise ConfigurationError('"CHECK_STYLE.config_file" must be a string')

    file_regex = style_config.get("file_regex", None)
    if file_regex is not None and not isinstance(file_regex, str):
        raise ConfigurationError('"CHECK_STYLE.file_regex" must be a string')

    max_score = style_config.get("max_score", None)
    if max_score is not None and not isinstance(max_score, int):
        raise ConfigurationError('"CHECK_STYLE.max_score" must be an integer')

    eval_function = style_config.get("eval_function", None)
    if eval_function is not None and not callable(eval_function):
        raise ConfigurationError(
            '"CHECK_STYLE.eval_function" must be a callable function'
        )

    return style_config
