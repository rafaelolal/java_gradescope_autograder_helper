import argparse
import json
import sys
from pathlib import Path
from typing import Callable

from .checkstyle.checkstyle import get_files_to_check, run_checkstyle
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
    Write results to a JSON file.
    """

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
    Validates the tests module by ensuring that it contains a properly configured TESTS variable.

    Raises:
        ConfigurationError: If TESTS is not found in tests_module, is not a list, or any test configuration
                            does not conform to the expected structure.
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
        ConfigurationError: If the 'ENTRY_POINT' variable is missing, is not a string,
                            or if it contains a path separator (i.e., is not merely a file name).
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


def check_style(tests_module):
    """
    Checks the Java source files for style violations using CheckStyle.

    If style checking is not enabled (i.e., CHECK_STYLE is False), the function returns None.
    """

    check_style = getattr(tests_module, "CHECK_STYLE", False)
    if not check_style:
        return

    check_style_configuration = getattr(
        tests_module, "CHECK_STYLE_CONFIGURATION", None
    )
    if check_style_configuration is not None:
        check_style_configuration = find_absolute_path(
            check_style_configuration
        )

    check_style_regex = getattr(tests_module, "CHECK_STYLE_REGEX", r".*\.java")
    files_to_check = get_files_to_check(
        ABSOLUTE_SUBMISSION_DIR, check_style_regex
    )

    violations = 0
    for file in files_to_check:
        output = run_checkstyle(
            str(Path(ABSOLUTE_SUBMISSION_DIR) / file),
            check_style_configuration,
        )
        violations += output

    return {
        "name": "Style",
        "score": 0,
        "max_score": 0,
        "output": f"Style violations: {violations}",
        "visibility": "visible",
        "status": "passed" if violations == 0 else "failed",
    }


def main():
    # Setting up CLI
    parser = argparse.ArgumentParser(
        description="Helper tool for Gradescope autograder setup for Java projects."
    )
    parser.add_argument(
        "path",
        help="Path to Python file with all tests and configurations.",
    )
    args = parser.parse_args()

    try:
        # Loading tests module
        path = find_absolute_path(args.path, cwd=ABSOLUTE_SOURCE_DIR)
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

        # Compile Java
        classpath = getattr(tests_module, "CLASSPATH", None)
        if classpath is not None:
            classpath = find_absolute_path(classpath)

        compile_java(reference_file_path, classpath)
        compile_java(submission_file_path, classpath)

        # Run tests
        # Specification: https://gradescope-autograders.readthedocs.io/en/latest/specs/
        final_json = {
            "execution_time": None,
            "tests": None,
        }

        final_json["execution_time"], final_json["tests"] = run_tests(
            tests, reference_file_path, submission_file_path
        )

        # Check style
        # Documentation: https://checkstyle.sourceforge.io/cmdline.html
        style_results = check_style(tests_module)
        if style_results:
            final_json["tests"].append(style_results)

        write_results(final_json)

    except ConfigurationError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
