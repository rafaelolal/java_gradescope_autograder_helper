import subprocess
from pathlib import Path


def compile_java(entry_point_path: str, classpath: str | None) -> None:
    """
    Compiles all Java source files found recursively from the directory of the given entry point.

    Raises:
        Exception: If the compilation process fails, an Exception is raised with the corresponding error message from stderr.
    """

    cmd = ["javac"]
    if classpath:
        cmd.extend(["-cp", classpath])

    # Recursively find all .java files
    entry_point_dir = Path(entry_point_path).parent
    java_files = list(entry_point_dir.rglob("*.java"))
    cmd.extend([str(java_file) for java_file in java_files])

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=entry_point_dir
    )

    if result.returncode != 0:
        raise Exception(f"Compilation failed:\n{result.stderr}")
