import os
from pathlib import Path


class ConfigurationError(Exception):
    """
    Raised when there is an error in the user's configuration.
    """

    pass


def find_absolute_path(search, cwd=None):
    """
    Searches for an absolute path ending with the specified string within a directory tree.

    Raises:
        ConfigurationError: If no file or directory ending with `search` is found in the specified directory tree, or if multiple matching instances are found.
    """

    if cwd is None:
        cwd = Path.cwd()

    instances = []
    for root, dirs, files in os.walk(cwd):
        for thing in dirs + files:
            absolute_thing_path = os.path.join(root, thing)
            if absolute_thing_path.endswith(search):
                instances.append(absolute_thing_path)

    if len(instances) == 1:
        return instances[0]

    if len(instances) > 1:
        raise ConfigurationError(
            f'Tried finding only one instance of the required file "{search}" in "{cwd}" but found multiple'
        )

    raise ConfigurationError(
        f'Tried finding the required file "{search}" in "{cwd}" but it was not there'
    )


# Gradescope autograder specifications: https://gradescope-autograders.readthedocs.io/en/latest/specs/
ABSOLUTE_SOURCE_DIR = find_absolute_path("/autograder/source")
ABSOLUTE_SUBMISSION_DIR = find_absolute_path("/autograder/submission")
ABSOLUTE_RESULTS_DIR = find_absolute_path("/autograder/results")
