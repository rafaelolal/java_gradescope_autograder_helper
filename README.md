# Java Gradescope Autograder Helper

More easily and quickly create and test Gradescope autograders for Java assignments. By leveraging a reference solution and standard output, there is no need to hardcode test cases. And, with a Python config file, you get the full benefits of writing tests in an easy-to-use coding language.

PyPi: https://pypi.org/manage/project/java-gradescope-autograder-helper/releases/

## Installation

`pip install java-gradescope-autograder-helper`

## Quick Start

1. Initialize the Gradescope environment locally: `autograder init .`
2. Put reference solution with a `main()` entry point and any other required files in `autograder/source/`
3. Edit `autograder/source/tests.py`
4. Put example student submission in `autograder/submission/`
5. Test by navigating to `/autograder` and running `./run_autograder`
6. Check results in `autograder/results/results.json`
7. Zip the contents inside `autograder/source/` and upload to Gradescope.

Note: you may need to give yourself execution permission on `run_autograder`
* **Mac**: `chmod +x run_autograder`

## Features

* No need to hardcode test cases, simply provide a reference solution.
* Independent of reference or student submission file structure, as long as it has the appropriate `main()` entry point.
* Easily test autograder locally.
* Create custom functions for more versatility when testing student output.
* Test student syntax with Checkstyle by providing a custom config. You can edit or extend the default config by downloading it at: https://github.com/rafaelolal/java_gradescope_autograder_helper/blob/main/src/java_gradescope_autograder_helper/checkstyle/bowdoin_checks.xml
* Create custom style evaluation functions.

## Usage Examples

A comprehensive example is available on every execution of `autograder init`. Additionally, all generated files contain small descriptions and references to their purpose in the original Gradescope documentation.

## Configuration

```py
# file: tests.py

# Classpath argument to pass to `javac` command when compiling reference and student code
CLASSPATH = str | None

# Config_file: a relative path from the `/autograder` folder since that is where Gradescope executes this file from
# eval_function: (checkstyle_stdout, total_style_violations) -> (grade_percentage, feedback) 
CHECKSTYLE = {
    "config_file": str | None,
    "file_regex": str | None,
    "max_score": int | None,
    "eval_function": Callable[[str, int], [float, str]] | None
}

# TESTS: a list of tuples that represent each test
# Gradescope arguments: https://gradescope-autograders.readthedocs.io/en/latest/specs/
# Custom grading function: (student_output, reference_output) -> (grade_percentage, feedback)
TESTS = [
    ("command line args", Callable[[str, str], [float, str]] | None, {"gradescope_arg1": "val1"}),
    ("command line args 2", {"gradescope_arg1": "val1"}),
]

```

## Examples

### Complete Example

https://github.com/rafaelolal/java_gradescope_autograder_helper/tree/main/src/java_gradescope_autograder_helper/examples

### Custom Grading Function

The below function expects a list of words separated by newline characters. Since it is not concerned with the ordering of the words, it does a disjoint set comparison. It then outputs 1 if there is no difference, meaning the student gets 100% of the max score, or 0% otherwise.

```py
def boggle_checker(student_out: str, reference_out: str) -> tuple[float, str]:
    student_set = set(student_out.split("\n"))
    reference_set = set(reference_out.split("\n"))

    # disjoint of the two sets
    diff = student_set ^ reference_set
    feedback = (
        f"{len(diff)} words are missing or incorrect."
        if len(diff) != 0
        else "Good job!"
    )
    score_percentage = 1 if len(diff) == 0 else 0

    return score_percentage, feedback
```

### Custom Checkstyle Evaluation Function

```py
# TODO
```