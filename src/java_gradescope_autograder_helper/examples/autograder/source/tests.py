# Documentation: https://github.com/rafaelolal/java_gradescope_autograder_helper

# Usually, this is the only file you need to edit.
# To simulate the Gradescope environment, ensure you are at /autograder and
# run the script `./run_autograder`.
# When uploading this to Gradescope, zip the contents of the
# `/autograder/source` directory.

# Custom diff functions go here:
def check_for_secret(
    student_out: str, reference_out: str
) -> tuple[float, str]:
    contains_secret = "banana split" in student_out.lower()
    feedback = (
        "Did you include the secret phrase in your output?"
        if not contains_secret
        else "Great Job!"
    )
    score_percentage = 1 if contains_secret else 0.7
    return score_percentage, feedback


CLASSPATH = None
ENTRY_POINT = "Main.java"

CHECK_STYLE = {
    "config_file": None,
    "file_regex": r"Main\.java",
    "max_score": 10,
    "eval_function": None,
}

# (input: str, optional diff_function, gradescope_kwargs: dict)
# Gradescope Kwargs specification: https://gradescope-autograders.readthedocs.io/en/latest/specs/#output-format

TESTS = [
    ("secret", check_for_secret, {"score": 10, "name": "Check Secret"}),
    ("1 2", {"score": 10, "name": "Evaluate 1+2"}),
    ("3 4", {"score": 10, "name": "Evaluate 3+4"}),
    ("5 6", {"score": 10, "name": "Evaluate 5+6"}),
]
