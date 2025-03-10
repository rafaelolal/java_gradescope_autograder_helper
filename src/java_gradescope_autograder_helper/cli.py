import argparse
import sys

from .helpers import ConfigurationError
from .init_autograder import init_autograder
from .run_autograder import run_autograder


def main():
    args = setup_arg_parser()

    if args.command == "init":
        init_autograder(args.path)
        sys.exit(0)

    # args.command == "run"
    try:
        run_autograder(args.path)

    except ConfigurationError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def setup_arg_parser():
    parser = argparse.ArgumentParser(
        description="Helper tool for Gradescope autograder setup for Java projects."
    )

    parser.add_argument(
        "command",
        choices=["run", "init"],
        help="Command to run the autograder or initialize the autograder structure.",
    )
    parser.add_argument(
        "path",
        help="Path to Python file with autograder tests or base directory for testing the autograder.",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
