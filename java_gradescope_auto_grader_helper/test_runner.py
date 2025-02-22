import subprocess

from .helpers import ConfigurationError


def validate_custom_diff_func_output(
    func: object, output: any
) -> tuple[float, str]:
    if not isinstance(output, (list, tuple)):
        raise ConfigurationError(
            f"The diff function {func} must return a tuple or list"
        )

    if len(output) != 2:
        raise ConfigurationError(
            f"The diff function {func} must return a tuple or list of length 2"
        )

    score, feedback = output

    if score < 0 or score > 1:
        raise ConfigurationError(
            f"The diff function {func} must return a score between 0 and 1 inclusive"
        )

    if not isinstance(feedback, str):
        raise ConfigurationError(
            f"The diff function {func} must return Feedback from custom diff function must be a string"
        )

    return score, feedback


def run_java_code(path: str, command_line_args: str) -> tuple[str, str]:
    cp = path.split("/")[:-1]
    file_name = path.split("/")[-1].split(".")[0]
    cp = "/".join(cp)
    cmd = ["java", file_name] + command_line_args.split(" ")

    try:
        # Execute the command, capturing stdout and stderr
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            cwd=cp,
        )

        return result.stdout, ""

    except subprocess.CalledProcessError as e:
        return "", e.stderr


def run_tests(
    tests, reference_file_path, submission_file_path
) -> tuple[int, list[dict]]:
    """Run the tests on the student's code and return the runtime and results"""

    results = []
    for test in tests:
        if len(test) == 3:
            args, func, kwargs = test

        elif len(test) == 2:
            args, kwargs = test
            func = None

        # Specification: https://gradescope-autograders.readthedocs.io/en/latest/specs/
        test_result = {
            "score": None,
            "max_score": kwargs.get("score", 1),
            "status": None,
            "name": kwargs.get("name", ""),
            "output": None,
            "visibility": kwargs.get("visibility", "visible"),
        }

        reference_output, reference_error = run_java_code(
            reference_file_path, args
        )

        if reference_error:
            raise ConfigurationError(
                f"The reference solution code failed to run on test {test_result['name']}"
            )

        student_output, student_error = run_java_code(
            submission_file_path, args
        )

        if student_error:
            test_result["status"] = "error"
            test_result["output"] = student_error
            results.append(test_result)
            continue

        if func is None:
            passed = reference_output == student_output
            test_result["status"] = "passed" if passed else "fail"
            test_result["score"] = test_result["max_score"] if passed else 0

        else:
            # Run the test with the provided function
            output = func(reference_output, student_output)
            score, feedback = validate_custom_diff_func_output(func, output)
            test_result["status"] = "passed"
            test_result["score"] = score * test_result["max_score"]
            test_result["output"] = feedback

        results.append(test_result)

    return -1, results
