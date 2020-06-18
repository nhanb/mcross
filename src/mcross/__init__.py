def run():
    from . import conf
    from .gui.controller import Controller

    conf.init()

    # Actually start the program
    c = Controller()
    c.run()


def info():
    from . import conf
    from pprint import pprint

    conf.init()

    print("Config file:", conf.CONFIG_FILE)
    print("Config:")
    pprint(conf._conf)
