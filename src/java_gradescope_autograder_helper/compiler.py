from pathlib import Path
from subprocess import run

from .helpers import ConfigurationError


def compile_java(entry_point_path: str, classpath: str | None) -> None:
    """
    Compiles all Java source files found recursively from the directory of
    the given entry point.

    Raises:
        Exception: If the compilation process fails, an Exception is raised
            with the corresponding error message from stderr.
    """

    cmd = ["javac"]
    if classpath:
        cmd.extend(["-cp", classpath])

    # Recursively find all .java files
    entry_point_dir = Path(entry_point_path).parent
    java_files = list(entry_point_dir.rglob("*.java"))
    cmd.extend([str(java_file) for java_file in java_files])

    try:
        result = run(cmd, capture_output=True, text=True, cwd=entry_point_dir)

        if result.returncode != 0:
            raise ConfigurationError(f"Compilation failed:\n{result.stderr}")

    except FileNotFoundError as e:
        if "javac" in str(e):
            raise ConfigurationError(
                "Java compiler (javac) not found. Please ensure you selected in Gradescope a base image variant with Java installed."
            )
