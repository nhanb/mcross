import traceback
from ssl import SSLCertVerificationError
from tkinter import TclError, Tk, messagebox

import curio

from ..transport import (
    GeminiUrl,
    NonAbsoluteUrlWithoutContextError,
    UnsupportedProtocolError,
    get,
)
from .model import Model
from .view import WAITING_CURSOR, View


class Controller:
    def __init__(self):
        self.root = Tk()
        self.model = Model()
        self.view = View(self.root, self.model)
        self.root.title("McRoss Browser")
        self.root.geometry("800x600")

        # Coroutine magic follows:

        self.pending_coros = []

        def schedule_as_coro(func):
            def do_schedule(*args):
                task = curio.spawn(
                    self.show_waiting_cursor_during_task(func, *args), daemon=True
                )
                self.pending_coros.append(task)

            return do_schedule

        self.view.go_callback = schedule_as_coro(self.go_callback)
        self.view.link_click_callback = schedule_as_coro(self.link_click_callback)
        self.view.back_callback = schedule_as_coro(self.back_callback)
        self.view.forward_callback = schedule_as_coro(self.forward_callback)

    def run(self):
        # Instead of running tkinter's root.mainloop() directly,
        # we rely on curio's event loop instead.
        # The main() coroutine does these things in an infinite loop:
        #   - do tk's necessary GUI with root.update()
        #   - run pending coroutines if there's any. This is used to run callbacks
        #     triggered by the view.
        #   - sleep a little so we don't loop root.update() too quickly.
        async def main():
            try:
                while True:
                    self.root.update()
                    for coroutine in self.pending_coros:
                        await coroutine
                    self.pending_coros = []
                    await curio.sleep(0.05)  # 50ms
            except TclError as e:
                if "application has been destroyed" not in str(e):
                    raise

        curio.run(main)

    async def show_waiting_cursor_during_task(self, func, *args):
        self.view.text.config(cursor=WAITING_CURSOR)
        self.root.config(cursor=WAITING_CURSOR)
        self.view.allow_changing_cursor = False

        try:
            await func(*args)
        except Exception:
            # a catch-all here so that our show_waiting...() coroutine can be yielded
            traceback.print_exc()

        # reset cursor to default values
        self.view.text.config(cursor="xterm")
        self.root.config(cursor="arrow")
        self.view.allow_changing_cursor = True

    async def go_callback(self, url: str):
        url = GeminiUrl.parse_absolute_url(url)
        await self.visit_link(url)

    async def link_click_callback(self, raw_url):
        try:
            url = GeminiUrl.parse(raw_url, self.model.history.get_current_url())
            await self.visit_link(url)
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

    async def visit_link(self, url: GeminiUrl):
        resp = await self.load_page(url)
        self.model.history.visit(resp.url)
        self.view.render_page()

    async def back_callback(self):
        self.model.history.go_back()
        await self.load_page(self.model.history.get_current_url())
        self.view.render_page()

    async def forward_callback(self):
        self.model.history.go_forward()
        await self.load_page(self.model.history.get_current_url())
        self.view.render_page()

    async def load_page(self, url: GeminiUrl):
        # print("Requesting", url)
        resp = await get(url)
        # print("Received", resp)

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
