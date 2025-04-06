import shlex
from pathlib import Path
from subprocess import run
from typing import Any, Callable, cast

from .helpers import (
    ConfigurationError,
    time_limited_execution,
    timed_execution,
)


def run_tests(
    tests: list[
        tuple[str, dict[str, Any]]
        | tuple[
            str,
            Callable[[str, str], tuple[float, str]],
            dict[str, Any],
        ],
    ],
    reference_file_path: str,
    submission_file_path: str,
) -> tuple[float, list[dict[str, Any]]]:
    """
    Run tests on the student's Java submission using the reference solution
    implementation.

    Raises:
        ConfigurationError: If the reference solution fails to run for any
        test or the test configuration setup is invalid
    """

    results: list[dict[str, Any]] = []
    total_run_time = 0
    for i, test in enumerate(tests):
        args = None
        diff_func = None
        kwargs: dict[str, Any] = {}
        if len(test) == 3:
            args, diff_func, kwargs = test

        elif len(test) == 2:
            args, kwargs = test
            diff_func = None

        assert args is not None

        reference_output, reference_error, _ = run_java_code(
            reference_file_path, args
        )
        if reference_error:
            test_name = kwargs.get("name", "<no name>")
            raise ConfigurationError(
                f'The reference solution code failed to run on test ({i}) "{test_name}" with error:\n\n{reference_error}'
            )

        timeout = kwargs.get("timeout", None)
        student_output, student_error, execution_time = run_java_code(
            submission_file_path, args, timeout=timeout
        )
        total_run_time += execution_time

        result = compile_test_results(
            reference_output, student_output, student_error, diff_func, kwargs
        )
        results.append(result)

    return total_run_time, results


def compile_test_results(
    reference_output: str,
    student_output: str,
    student_error: str,
    diff_func: Callable[[str, str], tuple[float, str]] | None,
    kwargs: dict[str, Any],
) -> dict[str, Any]:
    """
    Compile test results for Gradescope autograders.
    """

    max_score = kwargs.get("max_score", 0)
    test_result = {
        "score": None,
        "max_score": max_score,
        "status": None,
        "name": kwargs.get("name"),
        "output": kwargs.get("output", ""),
        "visibility": kwargs.get("visibility", "visible"),
    }

    truncate_length = 140
    truncate_message = f"(... {truncate_length} chars)"
    test_result["output"] = cast(str, test_result["output"])
    if student_output:
        formatted_output = f"\n\nOutput:\n\n{student_output}"
        if len(formatted_output) > truncate_length - len(truncate_message):
            formatted_output = (
                formatted_output[:truncate_length] + truncate_message
            )
        test_result["output"] += formatted_output

    if student_error:
        test_result["output"] += f"\n\nError:\n\n{student_error}"

    if diff_func is None:
        score_percentage, feedback = default_diff_function(
            student_output, reference_output
        )
        if score_percentage == 1:
            test_result["status"] = "passed"
        else:
            test_result["status"] = "failed"

        test_result["score"] = score_percentage * max_score

    else:
        score_percentage, feedback = validate_custom_diff_func_output(
            diff_func, diff_func(student_output, reference_output)
        )
        if score_percentage == 1:
            custom_status = "passed"
        else:
            custom_status = "failed"

        test_result["status"] = custom_status
        test_result["score"] = score_percentage * max_score
        if feedback:
            test_result["output"] += f"\n\n{feedback}"

    return test_result


def run_java_code(
    path: str, command_line_args: str, timeout: int | None = None
) -> tuple[str, str, float]:
    """
    Run a Java program given a compiled class file path and a command line arguments string.
    """

    file_path = Path(path)
    cwd = file_path.parent
    file_name = file_path.stem
    cmd = ["java", file_name] + shlex.split(command_line_args.strip())

    timed_run = timed_execution(time_limited_execution(timeout)(run))
    result, execution_time = timed_run(cmd, capture_output=True, cwd=cwd)
    if isinstance(result, TimeoutError):
        return "", str(result), execution_time

    # Decode outputs to get string results.
    stdout = result.stdout.decode("utf-8")
    stderr = result.stderr.decode("utf-8")
    return stdout, stderr, execution_time


def validate_custom_diff_func_output(
    func: Callable[[str, str], tuple[float, str]], output: Any
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

    output = cast(list[Any], output)
    if len(output) != 2:
        raise ConfigurationError(
            f"The diff function {func} must return exactly 2 elements."
        )

    score, feedback = output
    if not (0 <= score and score <= 1):
        raise ConfigurationError(
            f"The diff function {func} must return a score percentage between 0 and 1 inclusive."
        )

    if not isinstance(feedback, str):
        raise ConfigurationError(
            f"The diff function {func} must return feedback as a string."
        )

    return score, feedback


def default_diff_function(
    student_output: str, reference_output: str
) -> tuple[float, str]:
    if student_output == reference_output:
        return 1.0, "Outputs match exactly."
    else:
        return 0.0, "Outputs do not match."
