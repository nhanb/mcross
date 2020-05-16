from ssl import SSLCertVerificationError
from tkinter import Tk, messagebox

from ..transport import (
    GeminiUrl,
    NonAbsoluteUrlWithoutContextError,
    UnsupportedProtocolError,
    get,
)
from .model import Model
from .view import View


class Controller:
    def __init__(self):
        self.root = Tk()
        self.model = Model()
        self.view = View(self.root, self.model)
        self.view.go_callback = self.go_callback
        self.view.link_click_callback = self.link_click_callback
        self.view.back_callback = self.back_callback
        self.view.forward_callback = self.forward_callback

    def run(self):
        self.root.title("McRoss Browser")
        self.root.geometry("800x600")
        self.root.mainloop()

    def go_callback(self, url: str):
        # TODO more visual indications

        url = GeminiUrl.parse_absolute_url(url)
        self.visit_link(url)

    def link_click_callback(self, raw_url):
        # FIXME ugh
        try:
            url = GeminiUrl.parse(raw_url, self.model.history.get_current_url())
            self.visit_link(url)
        except NonAbsoluteUrlWithoutContextError:
            messagebox.showwarning(
                "Ambiguous link",
                "Cannot visit relative urls without a current_url context",
            )
        except UnsupportedProtocolError as e:
            messagebox.showinfo(
                "Unsupported protocol", f"{e} links are unsupported (yet?)"
            )
        except SSLCertVerificationError:
            messagebox.showerror(
                "Invalid server certificate",
                "Server is NOT using a valid CA-approved TLS certificate.",
            )

    def visit_link(self, url: GeminiUrl):
        resp = self.load_page(url)
        self.model.history.visit(resp.url)
        self.view.render_page()

    def back_callback(self):
        self.model.history.go_back()
        self.load_page(self.model.history.get_current_url())
        self.view.render_page()

    def forward_callback(self):
        self.model.history.go_forward()
        self.load_page(self.model.history.get_current_url())
        self.view.render_page()

    def load_page(self, url: GeminiUrl):
        print("Requesting", url)
        resp = get(url)
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
        return resp
