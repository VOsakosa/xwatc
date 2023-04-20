"""
Created on 20.04.2023
"""
import argparse
import sys
from xwatc import anzeige, terminal

__author__ = "jasper"


def main(args: list[str] | None = None):
    """Parse die Argumente und starte Xwatc."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--terminal", "-t",
                        help="Run in Terminal instead of using a GUI.", action="store_true")
    parsed = parser.parse_args(args)
    if parsed.terminal:
        terminal.hauptmenu()
    else:
        anzeige.main()


if __name__ == '__main__':
    main()
