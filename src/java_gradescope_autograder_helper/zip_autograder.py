import os
import zipfile
from pathlib import Path

from .helpers import ConfigurationError


def zip_autograder() -> None:
    """
    Zip the contents of the autograder/source/ directory and save the zip file
    in the directory in which the script is executed from

    Raises:
        ConfigurationError: If the source directory does not exist.
    """

    source_dir: Path = Path.cwd() / "autograder" / "source"
    if not source_dir.exists():
        raise ConfigurationError(
            f'Could not find source directory "{source_dir}" when zipping the autograder. You must be outside of the /autograder directory to zip it properly.'
        )

    zip_name = "gradescope_autograder.zip"
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Skip __pycache__ directories
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

    print(f'Zipped autograder in "{zip_name}".')
