import argparse

from . import __version__ as version


def parse_arguments():
    parser = argparse.ArgumentParser(description="CERN CMS Tracker studies.")

    parser.add_argument(
        "--version", action="version", version="%(prog)s {}".format(version)
    )

    return parser.parse_args()


def main():
    print("== Tracker studies version {} ==".format(version))


if __name__ == "__main__":
    main()
