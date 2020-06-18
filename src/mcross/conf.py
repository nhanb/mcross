import argparse
import os
from collections import namedtuple
from pathlib import Path

import toml
from appdirs import user_config_dir

CONFIG_DIR = Path(user_config_dir("mcross", False))
CONFIG_FILE = CONFIG_DIR / "mcross.toml"

_conf = None

ConfDef = namedtuple("ConfDef", ["name", "short_name", "type", "default"])
# argparse's add_argument() will ensure name/short_name uniqueness for free
conf_definitions = [
    ConfDef("text-font", "f", str, "Source Serif Pro"),
    ConfDef("mono-font", "m", str, "Ubuntu Mono"),
    ConfDef("background-color", "b", str, "#fff8dc"),
    ConfDef("text-color", "t", str, "black"),
    ConfDef("link-color", "l", str, "brown"),
    ConfDef("list-item-color", "i", str, "#044604"),
]


def init():
    default_conf = load_default_conf()
    file_conf = load_conf_file()
    cli_conf = parse_conf_args()

    global _conf
    _conf = {**default_conf, **file_conf, **cli_conf}
    return _conf


def load_default_conf():
    return {confdef.name: confdef.default for confdef in conf_definitions}


def load_conf_file():
    if not CONFIG_DIR.is_dir():
        os.mkdir(CONFIG_DIR)

    if not CONFIG_FILE.is_file():
        return {}

    try:
        data = toml.load(CONFIG_FILE)
        return {
            confdef.name: data[confdef.name]
            for confdef in conf_definitions
            if confdef.name in data
        }
    except Exception as e:
        print("Unexpected error reading config file:", str(e))
        return {}


def parse_conf_args():
    argparser = argparse.ArgumentParser()
    for confdef in conf_definitions:
        argparser.add_argument(
            f"-{confdef.short_name}", f"--{confdef.name}", type=confdef.type,
        )
    args = argparser.parse_args()
    return {key.replace("_", "-"): val for key, val in vars(args).items() if val}


def get(key):
    return _conf[key]


if __name__ == "__main__":
    init()
    import pprint

    print("Final conf:")
    pprint.pprint(_conf)
