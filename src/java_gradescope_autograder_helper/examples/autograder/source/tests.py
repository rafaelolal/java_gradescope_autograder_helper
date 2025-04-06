from typing import Any, Callable

# Documentation: https://github.com/rafaelolal/java_gradescope_autograder_helper

# Usually, this is the only file you need to edit.
# This file contains the configuration for the autograder.
# The autograder will run the tests defined in the TESTS variable and
# compare the student output to the reference output.
# The autograder will then output the results in the format expected by
# Gradescope.
# The autograder will also run a style check on the student code if the
# CHECK_STYLE variable is defined.

# To simulate the Gradescope environment, ensure you are at `/autograder` and
# run the script `autograder run tests.py`.
# When uploading this to Gradescope, zip the contents of the
# `/autograder/source` directory with `autograder zip` while in the bsase
# directory outside of `/autograder`.


# Custom diff functions go here:
# The purpose of diff functions is to provide a more complex comparison
# between the student output and the reference output beyond simple string
# comparison.
# All diff functions must have the signature of the below example:
def check_for_secret(
    student_out: str, reference_out: str
) -> tuple[float, str]:
    score_percentage = 0.7
    feedback = "Did you include the secret phrase in your output?"
    # student included the secret phrase
    if "banana split" in student_out.lower():
        score_percentage = 1
        feedback = "Good Job!"

    # score_percentage is a float between 0 and 1 that represents the
    # percentage of the score the student should get.
    return score_percentage, feedback


CLASSPATH: str | None = None
# ENTRY_POINT should not be a path, but just the name of the file containing
# the main method.
ENTRY_POINT: str = "Main.java"

# Comment this variable out if you do not want to use check style.
# config_file: a relative path from the `/autograder` folder since that is
# where Gradescope executes this file from.
# file_regex: a regex pattern to match the files that shoud be style checked,
# which will usually be something like r"(File1|File2)\.java".
# max_score: the maximum score for the style check.
# eval_function: TODO
CHECK_STYLE: dict[str, Any] = {
    "config_file": None,
    "file_regex": r"Main\.java",
    "max_score": 10,
    "eval_function": None,
}


# TESTS is probably the most important part of this file. It is a list of tuples
# with this structure:
# (command_line_args, (optional)diff_function, gradescope_kwargs)
# command_line_args: a string that will be passed to the main method of the
# reference and student code.
# diff_function: a function that will be used to compare the student output to
# the reference output. If not provided, a simple string comparison will be
# used.
# gradescope_kwargs: a dictionary with the following keys: https://gradescope-autograders.readthedocs.io/en/latest/specs/#output-format
# The only keys you will probably ever need are: "max_score", "name", "number",
# "visiblity".
# Keep in mind that the scores must match whatever you set in Gradescope.
# Additional package-only kwargs:
# "timeout": int,  # Optional timeout in whole seconds for the test case.
TESTS: list[
    tuple[str, dict[str, Any]]
    | tuple[str, Callable[[str, str], tuple[float, str]], dict[str, Any]]
] = [
    (
        "greet secret",
        check_for_secret,
        {"max_score": 10, "name": "Check Secret"},
    ),
    ("add 1 2", {"max_score": 10, "name": "Evaluate 1+2", "timeout": 2}),
    (
        "add 3 4",
        {"max_score": 10, "name": "Evaluate 3+4", "visibility": "hidden"},
    ),
    ("add 5 6", {"max_score": 10, "name": "Evaluate 5+6"}),
]
