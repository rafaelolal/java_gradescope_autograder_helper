import json
from pathlib import Path
from typing import Callable

from .checkstyle.checkstyle import check_style
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

    print(f'Results written to "{results_dir / "results.json"}".')
