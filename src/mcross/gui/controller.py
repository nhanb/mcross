import logging
import threading
import time
import traceback
from ssl import SSLCertVerificationError
from tkinter import READABLE, Tk, messagebox

import curio

from ..transport import (
    MAX_REQUEST_SECONDS,
    GeminiUrl,
    NonAbsoluteUrlWithoutContextError,
    UnsupportedProtocolError,
    get,
)
from .model import Model
from .view import WAITING_CURSOR, View

statusbar_logger = logging.getLogger("statusbar")


class Controller:
    def __init__(self, args):
        self.root = Tk()
        self.root.alt_shortcuts = set()
        self.model = Model()
        self.view = View(self.root, self.model, fonts=(args.textfont, args.monofont))
        self.root.title("McRoss Browser")
        self.root.geometry("800x600")

        self.gui_ops = curio.UniversalQueue(withfd=True)
        self.coro_ops = curio.UniversalQueue()

        # Set up event handler for queued GUI updates
        self.root.createfilehandler(self.gui_ops, READABLE, self.process_gui_ops)

        # When in the middle of an action, this flag is set to False to prevent user
        # from clicking other random stuff:
        self.allow_user_interaction = True

        def put_coro_op(func):
            def inner(*args):
                if self.allow_user_interaction:
                    self.coro_ops.put(self.show_waiting_cursor_during_task(func, *args))

            return inner

        self.view.go_callback = put_coro_op(self.go_callback)
        self.view.link_click_callback = put_coro_op(self.link_click_callback)
        self.view.back_callback = put_coro_op(self.back_callback)
        self.view.forward_callback = put_coro_op(self.forward_callback)

    async def main(self):
        while True:
            coro = await self.coro_ops.get()
            await coro

    def run(self):
        threading.Thread(target=curio.run, args=(self.main,), daemon=True).start()
        self.root.mainloop()

    async def put_gui_op(self, func, *args, **kwargs):
        await self.gui_ops.put((func, args, kwargs))

    def process_gui_ops(self, file, mask):
        while not self.gui_ops.empty():
            func, args, kwargs = self.gui_ops.get()
            func(*args, **kwargs)

    async def show_waiting_cursor_during_task(self, func, *args):
        async def show():
            self.view.text.config(cursor=WAITING_CURSOR)
            self.root.config(cursor=WAITING_CURSOR)
            self.view.allow_changing_cursor = False

        async def hide():
            self.view.text.config(cursor="xterm")
            self.root.config(cursor="arrow")
            self.view.allow_changing_cursor = True

        await show()
        self.allow_user_interaction = False

        try:
            await func(*args)
        except Exception:
            # a catch-all here so that our show_waiting...() coroutine can be yielded
            traceback.print_exc()

        self.allow_user_interaction = True
        await hide()

    async def go_callback(self, url: str):
        url = GeminiUrl.parse_absolute_url(url)
        await self.visit_link(url)

    async def link_click_callback(self, raw_url):
        try:
            url = GeminiUrl.parse(raw_url, self.model.history.get_current_url())
            await self.visit_link(url)
        except NonAbsoluteUrlWithoutContextError:
            await self.put_gui_op(
                messagebox.showwarning,
                "Ambiguous link",
                "Cannot visit relative urls without a current_url context",
            )
        except UnsupportedProtocolError as e:
            await self.put_gui_op(
                messagebox.showinfo,
                "Unsupported protocol",
                f"{e} links are unsupported (yet?)",
            )
        except SSLCertVerificationError:
            await self.put_gui_op(
                messagebox.showerror,
                "Invalid server certificate",
                "Server is NOT using a valid CA-approved TLS certificate.",
            )

    async def visit_link(self, url: GeminiUrl):
        try:
            resp = await self.load_page(url)
            self.model.history.visit(resp.url)
            await self.put_gui_op(self.view.render_page)

        except curio.errors.TaskTimeout:
            await self.put_gui_op(
                statusbar_logger.info, f"Request timed out: {MAX_REQUEST_SECONDS}s",
            )
            await self.put_gui_op(
                messagebox.showwarning,
                "Request timed out",
                f"Request to {url.without_protocol()} took longer than {MAX_REQUEST_SECONDS}s",
            )

        except (ConnectionError, OSError) as e:
            await self.put_gui_op(statusbar_logger.info, str(e))
            raise

    async def back_callback(self):
        self.model.history.go_back()
        await self.load_page(self.model.history.get_current_url())
        await self.put_gui_op(self.view.render_page)

    async def forward_callback(self):
        self.model.history.go_forward()
        await self.load_page(self.model.history.get_current_url())
        self.view.render_page()

    async def load_page(self, url: GeminiUrl):
        await self.put_gui_op(statusbar_logger.info, f"Requesting {url}...")
        start = time.time()
        resp = await get(url)
        request_time = time.time() - start
        await self.put_gui_op(
            statusbar_logger.info,
            f"{resp.status} {resp.meta} (took {request_time:.2f}s)",
        )

        if resp.status.startswith("2"):
            await self.put_gui_op(self.model.update_content, resp.body.decode())
        else:
            await self.put_gui_op(
                self.model.update_content,
                "\n".join(
                    [
                        "Error:",
                        f"{resp.status} {resp.meta}",
                        resp.body.decode() if resp.body else "",
                    ]
                ),
            )
        return resp
