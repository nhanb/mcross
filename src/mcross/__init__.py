import argparse

from .gui.controller import Controller


def run():

    # Parse CLI arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--textfont")
    argparser.add_argument("--monofont")
    args = argparser.parse_args()

    # Actually start the program
    c = Controller(args)
    c.run()
