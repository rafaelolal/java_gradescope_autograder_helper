import os
from pathlib import Path


class ConfigurationError(Exception):
    """Raised when there is an error in the user's configurations"""

    pass


def find_absolute_path(search, cwd=None):
    """Returns an absolute path ending in `search` in the directory `cwd`"""

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


ABSOLUTE_SOURCE_DIR = find_absolute_path("/autograder/source")
ABSOLUTE_SUBMISSION_DIR = find_absolute_path("/autograder/submission")
ABSOLUTE_RESULTS_DIR = find_absolute_path("/autograder/results")
