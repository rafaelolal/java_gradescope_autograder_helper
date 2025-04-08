import argparse
from os import environ
from sys import exit, stderr
from traceback import print_exc

from .helpers import ConfigurationError, load_env
from .init_autograder import init_autograder
from .run_autograder import run_autograder
from .zip_autograder import zip_autograder

load_env()
DEBUG = bool(int(environ.get("DEBUG", "0")))  # 1 for True, 0 for False


def main():
    """
    Main entry point for the CLI.

    Parses command-line arguments and executes the appropriate command.
    """

    if DEBUG:
        print("Debug mode is ON. Detailed error messages will be shown.")

    parser, args = setup_arg_parser()
    try:
        if args.command == "init":
            init_autograder()

        elif args.command == "run":
            run_autograder(args.path)

        elif args.command == "zip":
            zip_autograder()

        else:
            # No command provided, show help
            parser.print_help()

        exit(0)

    except ConfigurationError as e:
        if DEBUG:
            print_exc()

        print(str(e), file=stderr)
        exit(1)

    except Exception:
        print_exc()
        print("\n\n\n\n\n")
        print(
            "An unexpected error occurred. Please report to the package maintainers with the above error message and any details to reproduce the error.",
            file=stderr,
        )
        exit(1)


def setup_arg_parser():
    """
    Set up the argument parser for the command-line interface.

    Returns:
        argparse.Namespace: The parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Java Gradescope Autograder Helper - Tools for creating, running, and packaging Java autograders for Gradescope"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Init command
    subparsers.add_parser(
        "init", help="Initialize a new autograder with example files"
    )

    # Run command
    run_parser = subparsers.add_parser(
        "run", help="Run the autograder on a submission"
    )
    run_parser.add_argument(
        "path", help="Name of the autograder tests Python module to execute"
    )

    # Zip command
    subparsers.add_parser(
        "zip", help="Create a ZIP archive of the autograder source files"
    )

    return parser, parser.parse_args()


if __name__ == "__main__":
    main()
