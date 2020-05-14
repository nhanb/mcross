from tkinter import Tk

from .. import transport
from .model import Model
from .view import View


class Controller:
    def __init__(self):
        self.root = Tk()
        self.model = Model()
        self.view = View(self.root, self.model)
        self.view.go_callback = self.go_callback

    def run(self):
        self.root.title("McRoss Browser")
        self.root.geometry("800x600")
        self.root.mainloop()

    def go_callback(self, url: str):
        # TODO more visual indications
        # TODO url validation

        print("Requesting", url)
        resp = transport.get(url)
        print("Received", resp)

        if resp.status.startswith("2"):
            self.model.update_content(resp.body.decode())
        else:
            self.model.update_content(
                "\n".join(
                    [
                        "Error:",
                        f"{resp.status} {resp.meta}",
                        resp.body.decode() if resp.body else "",
                    ]
                )
            )

        self.view.render_page()
