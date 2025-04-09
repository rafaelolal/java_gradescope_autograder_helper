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

    try:
        dest_dir.mkdir(parents=True)
    except FileExistsError:
        raise ConfigurationError(
            f'Autograder environment "{dest_dir}" already exists.'
        )

    if not source_dir.exists():
        raise ConfigurationError(
            f'Could not find source directory "{source_dir}" when initializing the autograder. Please report this issue to the package maintainers.'
        )

    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
    print(f'Initialized autograder in "{dest_dir}".')
