import subprocess
from pathlib import Path
from typing import Any, Callable

from .helpers import ConfigurationError


def validate_custom_diff_func_output(
    func: Callable[[str, str], tuple[float, str]], output: str
) -> tuple[float, str]:
    """
    Validate the output of a custom diff function.

    Raises:
        ConfigurationError: If output is not a sequence of exactly two elements,
                            if the score is not between 0 and 1 inclusive,
                            or if the feedback is not a string.
    """

    if not isinstance(output, (list, tuple)):
        raise ConfigurationError(
            f"The diff function {func} must return a tuple or list."
        )

    if len(output) != 2:
        raise ConfigurationError(
            f"The diff function {func} must return exactly 2 elements."
        )

    score, feedback = output
    if not (0 <= score <= 1):
        raise ConfigurationError(
            f"The diff function {func} must return a score between 0 and 1 inclusive."
        )

    if not isinstance(feedback, str):
        raise ConfigurationError(
            f"The diff function {func} must return feedback as a string."
        )

    return score, feedback


def run_java_code(path: str, command_line_args: str) -> tuple[str, str]:
    """
    Run a Java program given a compiled class file path and a command line arguments string.
    """

    file_path = Path(path)
    cwd = file_path.parent
    file_name = file_path.stem
    cmd = ["java", file_name] + command_line_args.strip().split()

    result = subprocess.run(cmd, capture_output=True, cwd=cwd)
    # Decode outputs to get string results.
    stdout = result.stdout.decode("utf-8")
    stderr = result.stderr.decode("utf-8")
    return stdout, stderr


def compile_test_results(
    reference_output: str,
    student_output: str,
    student_error: str,
    diff_func: tuple[float, str] | None,
    kwargs: dict[str, str | int],
) -> dict[str, str | int | None]:
    """
    Compile test results for Gradescope autograders.
    """

    max_score = kwargs.get("score", 1)
    test_result = {
        "score": None,
        "max_score": max_score,
        "status": None,
        "name": kwargs.get("name"),
        "output": kwargs.get("output", ""),
        "visibility": kwargs.get("visibility", "visible"),
    }

    if student_output:
        test_result["output"] += f"\n\nOutput:\n\n{student_output}"
    if student_error:
        test_result["output"] += f"\n\nError:\n\n{student_error}"

    if diff_func is None:
        passed = reference_output == student_output
        test_result["status"] = "passed" if passed else "fail"
        test_result["score"] = max_score if passed else 0
    else:
        score, feedback = validate_custom_diff_func_output(
            diff_func, diff_func(reference_output, student_output)
        )
        test_result["status"] = "passed"
        test_result["score"] = score * max_score
        test_result["output"] += f"\n\n{feedback}"

    return test_result


def run_tests(
    tests: list[
        tuple[
            str,
            Callable[[str, str], tuple[float, str]],
            dict[str, str | int],
        ]
        | tuple[str, dict[str, str | int]],
    ],
    reference_file_path: str,
    submission_file_path: str,
) -> tuple[int, list[dict[str, Any]]]:
    """
    Run tests on the student's Java submission using the reference implementation.

    Raises:
        ConfigurationError: If the reference solution fails to run for any test.
    """

    results = []
    total_run_time = 0
    for i, test in enumerate(tests):
        if len(test) == 3:
            args, diff_func, kwargs = test
        elif len(test) == 2:
            args, kwargs = test
            diff_func = None
        else:
            raise ConfigurationError("Invalid test configuration.")

        reference_output, reference_error = run_java_code(
            reference_file_path, args
        )
        if reference_error:
            test_name = kwargs.get("name", "<unknown>")
            raise ConfigurationError(
                f"The reference solution code failed to run on test {i}: {test_name}."
            )

        student_output, student_error = run_java_code(
            submission_file_path, args
        )

        result = compile_test_results(
            reference_output, student_output, student_error, diff_func, kwargs
        )
        results.append(result)

    return total_run_time, results
