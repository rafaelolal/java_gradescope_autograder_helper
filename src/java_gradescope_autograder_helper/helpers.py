import os
import signal
from math import ceil
from pathlib import Path
from time import time
from typing import Any, Callable

# Gradescope autograder file structure: https://gradescope-autograders.readthedocs.io/en/latest/specs/#file-hierarchy
SOURCE_DIR = "/autograder/source"
SUBMISSION_DIR = "/autograder/submission"
RESULTS_DIR = "/autograder/results"


class ConfigurationError(Exception):
    """
    Raised when there is an error in the user's configuration.
    """

    pass


def find_absolute_path(search: str, cwd: str | None = None) -> str:
    """
    Searches for an absolute path ending with the specified string within a
    directory tree.

    Raises:
        ConfigurationError: If no file or directory ending with `search` is
            found in the specified directory tree, or if multiple matching
            instances are found.
    """

    if cwd is None:
        cwd = str(Path.cwd())

    instances: list[str] = []
    for root, dirs, files in os.walk(cwd):
        for thing in dirs + files:
            absolute_thing_path = os.path.join(root, thing)
            if absolute_thing_path.endswith(search):
                instances.append(absolute_thing_path)

    if len(instances) == 1:
        return instances[0]

    if len(instances) > 1:
        raise ConfigurationError(
            f'Tried finding only one instance of the required file "{search}" in "{cwd}" but found {len(instances)}.'
        )

    raise ConfigurationError(
        f'Tried finding the required file "{search}" in "{cwd}" but it was not there.'
    )


def timed_execution(
    func: Callable[..., Any],
) -> Callable[..., tuple[Any, float]]:
    def wrapper(*args: Any, **kwargs: Any) -> tuple[Any, float]:
        start = time()
        result = func(*args, **kwargs)
        end = time()
        execution_time = end - start
        return result, execution_time

    return wrapper


def time_limited_execution(seconds: int | None = None):
    def handler(signum: int, frame: Any):
        raise TimeoutError()

    def decorator(func: Callable[..., Any]):
        def wrapper(
            *args: Any, **kwargs: Any
        ) -> tuple[Any, float] | TimeoutError:
            if seconds is None:
                return func(*args, **kwargs)

            signal.signal(signal.SIGALRM, handler)
            signal.alarm(ceil(seconds))

            try:
                result = func(*args, **kwargs)

            except TimeoutError:
                return TimeoutError(
                    f"Time limit of {seconds} second(s) exceeded."
                )

            finally:
                signal.alarm(0)

            return result

        return wrapper

    return decorator
