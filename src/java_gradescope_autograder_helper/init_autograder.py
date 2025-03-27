import shutil
from pathlib import Path

from .helpers import ConfigurationError


def init_autograder() -> None:
    """
    Initialize the autograder by copying the example autograder files from the
    source directory to the destination.

    The source directory is determined relative to this file's location at:
        <current_file_directory>/examples/autograder

    Raises:
        ConfigurationError: If the source autograder directory does not
            exist, or if the destination directory cannot be verified after
            creation.

    """
    source_dir = Path(__file__).parent / "examples" / "autograder"
    dest_dir = Path.cwd() / "autograder"
    dest_dir.mkdir(exist_ok=True, parents=True)

    if not source_dir.exists():
        raise ConfigurationError(
            f'Could not find source directory "{source_dir}" when initializing the autograder.'
        )

    if not dest_dir.exists():
        raise ConfigurationError(
            f"Could not find the destination directory {dest_dir} when initializing the autograder."
        )

    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
    print(f'Initialized autograder in "{dest_dir}".')
