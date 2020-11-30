def run():
    from . import conf
    from .gui.controller import Controller

    conf.init()

    # Actually start the program
    c = Controller()
    c.run()


def info():
    from pprint import pprint

    from . import conf

    conf.init()

    print("Config file:", conf.CONFIG_FILE)
    print("Config:")
    pprint(conf._conf)
