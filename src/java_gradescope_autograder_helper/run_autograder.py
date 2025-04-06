import json
from pathlib import Path
from typing import Any, Callable, cast

from .checkstyle.checkstyle import check_style
from .compiler import compile_java
from .helpers import (
    RESULTS_DIR,
    SOURCE_DIR,
    SUBMISSION_DIR,
    ConfigurationError,
    find_absolute_path,
)
from .loader import load_module
from .test_runner import run_tests


def run_autograder(tests_file_name: str) -> None:
    global SOURCE_DIR, SUBMISSION_DIR

    # Loading tests module
    absolute_source_path = find_absolute_path(SOURCE_DIR)
    absolute_tests_file_path = find_absolute_path(
        tests_file_name, cwd=absolute_source_path
    )
    tests_module = load_module(absolute_tests_file_path)

    entry_point_name = validate_entry_point(tests_module)

    # Compiling
    reference_entry_point_path = find_absolute_path(
        entry_point_name,
        absolute_source_path,
    )
    absolute_submission_dir = find_absolute_path(SUBMISSION_DIR)
    submission_entry_point_path = find_absolute_path(
        entry_point_name,
        absolute_submission_dir,
    )

    classpath = getattr(tests_module, "CLASSPATH", None)
    compile_java(reference_entry_point_path, classpath)
    compile_java(submission_entry_point_path, classpath)

    # Run tests
    # Specification: https://gradescope-autograders.readthedocs.io/en/latest/specs/
    final_json: dict[str, float | list[dict[str, Any]]] = {
        "execution_time": 0,
        "tests": [],
    }

    # Compile Java
    classpath = getattr(tests_module, "CLASSPATH", None)
    if classpath is not None:
        classpath = find_absolute_path(classpath)

    tests = validate_test_list(tests_module)
    execution_time, test_results = run_tests(
        tests,
        reference_entry_point_path,
        submission_entry_point_path,
    )
    final_json["execution_time"] = execution_time
    final_json["tests"] = test_results

    # Check style
    # Documentation: https://checkstyle.sourceforge.io/cmdline.html
    style_results = check_style(tests_module)
    if style_results:
        final_json["tests"].append(style_results)

    write_results(final_json)


def validate_test_list(
    tests_module: object,
) -> list[
    tuple[
        str,
        Callable[[str, str], tuple[float, str]],
        dict[str, Any],
    ]
    | tuple[str, dict[str, Any]],
]:
    """
    Validates the tests module by ensuring that it contains a properly
    configured TESTS variable.

    Raises:
        ConfigurationError: If TESTS is not found in tests_module, is not a
            list, or any test configuration does not conform to the expected
            structure.
    """

    tests = getattr(tests_module, "TESTS", None)
    if tests is None:
        raise ConfigurationError(
            "TESTS variable not in the tests configuration file."
        )

    if not isinstance(tests, (list, tuple)):
        raise ConfigurationError(
            "TESTS variable must be a list or tuple of test configurations."
        )

    tests = cast(
        list[Any],
        tests,
    )

    # Validate tests
    for test in tests:
        if not isinstance(test, (list, tuple)):
            raise ConfigurationError(
                "Invalid test configuration, must be a list or tuple"
            )

        test = cast(list[Any], test)
        args = None
        func = None
        kwargs = None
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

    return tests


def validate_entry_point(tests_module: object) -> str:
    """
    Validates the 'ENTRY_POINT' variable in the provided tests module.

    Raises:
        ConfigurationError: If the 'ENTRY_POINT' variable is missing, is not a
            string, or if it contains a path separator (i.e., is not merely a
            file name).
    """

    reference_file_name = getattr(tests_module, "ENTRY_POINT", None)
    if reference_file_name is None:
        raise ConfigurationError(
            "ENTRY_POINT variable not found in the tests module"
        )

    if not isinstance(reference_file_name, str):
        raise ConfigurationError("ENTRY_POINT variable must be a string")

    if "/" in reference_file_name:
        raise ConfigurationError(
            "ENTRY_POINT variable must be a file name, not a path"
        )

    return reference_file_name


def write_results(results: dict[str, Any]) -> None:
    """
    Write results to the results JSON file.
    """

    global RESULTS_DIR

    absolute_results_path = find_absolute_path(RESULTS_DIR)
    results_dir = Path(absolute_results_path)
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "results.json", "w") as results_file:
        json.dump(results, results_file)

    print(f'Results written to "{results_dir / "results.json"}".')
