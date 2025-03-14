import importlib.resources
import re
import subprocess
from pathlib import Path

from ..helpers import (
    ABSOLUTE_SUBMISSION_DIR,
    ConfigurationError,
    find_absolute_path,
)


def check_style(tests_module) -> dict[str, str | int] | None:
    """
    Checks the Java source files for style violations using CheckStyle.
    """

    check_style = validate_checkstyle_config(tests_module)
    if check_style is None:
        return None

    check_style_configuration = check_style.get("config_file", None)
    if check_style_configuration is not None:
        check_style_configuration = find_absolute_path(
            check_style_configuration
        )

    check_style_regex = check_style.get("file_regex", r".*\.java")
    files_to_check = get_files_to_check(
        ABSOLUTE_SUBMISSION_DIR, check_style_regex
    )

    violations = 0
    for file in files_to_check:
        stdout, stderr = run_checkstyle(
            find_absolute_path(file, cwd=ABSOLUTE_SUBMISSION_DIR),
            check_style_configuration,
        )
        total_errors = get_total_errors(stdout)
        violations += total_errors

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


def validate_checkstyle_config(tests_module) -> dict[str, str | int] | None:
    # CHECK_STYLE = {
    #     "config_file": None,
    #     "file_regex": r"(BoggleBoard|Recursion)\.java",
    #     "max_score": 0,
    #     "eval_function": None,
    # }

    check_style = getattr(tests_module, "CHECK_STYLE", None)
    if check_style is None:
        return None

    if not isinstance(check_style, dict):
        raise ConfigurationError('"CHECK_STYLE" must be a dictionary')

    config_file = check_style.get("config_file", None)
    if config_file is not None and not isinstance(config_file, str):
        raise ConfigurationError('"CHECK_STYLE.config_file" must be a string')

    file_regex = check_style.get("file_regex", None)
    if file_regex is not None and not isinstance(file_regex, str):
        raise ConfigurationError('"CHECK_STYLE.file_regex" must be a string')

    max_score = check_style.get("max_score", None)
    if max_score is not None and not isinstance(max_score, int):
        raise ConfigurationError('"CHECK_STYLE.max_score" must be an integer')

    eval_function = check_style.get("eval_function", None)
    if eval_function is not None and not callable(eval_function):
        raise ConfigurationError(
            '"CHECK_STYLE.eval_function" must be a callable function'
        )

    return check_style


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
