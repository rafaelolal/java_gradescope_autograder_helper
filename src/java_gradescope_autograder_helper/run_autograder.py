import json
from pathlib import Path
from typing import Callable

from .checkstyle.checkstyle import (
    default_evaluation,
    get_files_to_check,
    get_total_errors,
    run_checkstyle,
)
from .compiler import compile_java
from .helpers import (
    ABSOLUTE_RESULTS_DIR,
    ABSOLUTE_SOURCE_DIR,
    ABSOLUTE_SUBMISSION_DIR,
    ConfigurationError,
    find_absolute_path,
)
from .loader import load_module
from .test_runner import run_tests


def write_results(results: dict) -> None:
    """
    Write results to the results JSON file.
    """

    global ABSOLUTE_RESULTS_DIR

    ABSOLUTE_RESULTS_DIR = find_absolute_path(ABSOLUTE_RESULTS_DIR)
    results_dir = Path(ABSOLUTE_RESULTS_DIR)
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "results.json", "w") as results_file:
        json.dump(results, results_file)


def validate_tests_module(
    tests_module: object,
) -> list[
    list[
        tuple[
            str,
            Callable[[str, str], tuple[float, str]],
            dict[str, str | int],
        ]
        | tuple[str, dict[str, str | int]],
    ]
]:
    """
    Validates the tests module by ensuring that it contains a properly
    configured TESTS variable.

    Raises:
        ConfigurationError: If TESTS is not found in tests_module, is not a
            list, or any test configuration does not conform to the expected
            structure.
    """

    if not hasattr(tests_module, "TESTS"):
        raise ConfigurationError(
            "TESTS variable not found in the tests module"
        )

    tests = tests_module.TESTS
    # Validate tests
    for test in tests:
        if not isinstance(test, (list, tuple)):
            raise ConfigurationError(
                "Invalid test configuration, must be a list or tuple"
            )

        if len(test) == 3:
            args, func, kwargs = test

        elif len(test) == 2:
            args, kwargs = test
            func = None

        if not (
            isinstance(args, str)
            and isinstance(kwargs, dict)
            and (func is None or callable(func))
        ):
            raise ConfigurationError(
                "Invalid test configuration, must be (args, [optional diff_function], gradescope_kwargs)"
            )

    if not isinstance(tests, list):
        raise ConfigurationError("TESTS variable must be a list")

    return tests


def validate_entry_point(tests_module) -> str:
    """
    Validates the 'ENTRY_POINT' variable in the provided tests module.

    Raises:
        ConfigurationError: If the 'ENTRY_POINT' variable is missing, is not a
            string, or if it contains a path separator (i.e., is not merely a
            file name).
    """

    if not hasattr(tests_module, "ENTRY_POINT"):
        raise ConfigurationError(
            "ENTRY_POINT variable not found in the tests module"
        )

    reference_file_name = tests_module.ENTRY_POINT
    if not isinstance(reference_file_name, str):
        raise ConfigurationError("ENTRY_POINT variable must be a string")

    if "/" in reference_file_name:
        raise ConfigurationError(
            "ENTRY_POINT variable must be a file name, not a path"
        )

    return reference_file_name


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


def run_autograder(autograder_path: str) -> None:
    global ABSOLUTE_SOURCE_DIR
    global ABSOLUTE_SUBMISSION_DIR

    ABSOLUTE_SOURCE_DIR = find_absolute_path(ABSOLUTE_SOURCE_DIR)
    ABSOLUTE_SUBMISSION_DIR = find_absolute_path(ABSOLUTE_SUBMISSION_DIR)
    # Loading tests module
    path = find_absolute_path(autograder_path, cwd=ABSOLUTE_SOURCE_DIR)
    tests_module = load_module(path)

    tests = validate_tests_module(tests_module)
    reference_file_name = validate_entry_point(tests_module)

    # Compiling
    reference_file_path = find_absolute_path(
        reference_file_name,
        ABSOLUTE_SOURCE_DIR,
    )
    submission_file_path = find_absolute_path(
        reference_file_name,
        ABSOLUTE_SUBMISSION_DIR,
    )

    # Run tests
    # Specification: https://gradescope-autograders.readthedocs.io/en/latest/specs/
    final_json = {
        "execution_time": None,
        "tests": [],
    }

    # Check style
    # Documentation: https://checkstyle.sourceforge.io/cmdline.html
    style_results = check_style(tests_module)
    if style_results:
        final_json["tests"].append(style_results)

    # Compile Java
    classpath = getattr(tests_module, "CLASSPATH", None)
    if classpath is not None:
        classpath = find_absolute_path(classpath)

    compile_java(reference_file_path, classpath)
    compile_java(submission_file_path, classpath)

    final_json["execution_time"], final_json["tests"] = run_tests(
        tests, reference_file_path, submission_file_path
    )

    write_results(final_json)
