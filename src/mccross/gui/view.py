import sys
from tkinter import Text, Tk, font, ttk

from ..document import GeminiNode, LinkNode, PreformattedNode, TextNode
from .model import Model
from .widgets import ReadOnlyText


def pick_font(names):
    available = font.families()
    picked = None
    for name in names:
        if name in available:
            picked = name
            break

    if not picked:
        picked = "TkTextFont"

    print("Picked font:", picked)
    return picked


class View:
    model: Model
    address_bar: ttk.Entry
    go_button: ttk.Button
    viewport: ttk.Frame
    text: Text

    go_callback = None

    def __init__(self, root: Tk, model: Model):
        self.model = model

        # first row - address bar + button
        row1 = ttk.Frame(root)
        row1.pack(fill="x")

        # second row - web viewport
        row2 = ttk.Frame(root)
        row2.pack(fill="both", expand=True)

        # Address bar prefix
        address_prefix = ttk.Label(row1, text="gemini://")
        address_prefix.pack(side="left")

        # Address bar
        address_bar = ttk.Entry(row1)
        address_bar.insert(0, "gemini.circumlunar.space/")
        self.address_bar = address_bar
        address_bar.pack(side="left", fill="both", expand=True, padx=3, pady=3)
        address_bar.bind("<Return>", self._on_go)
        address_bar.bind("<KP_Enter>", self._on_go)
        address_bar.focus_set()

        # Go button
        go_button = ttk.Button(row1, text="go", command=self._on_go)
        self.go_button = go_button
        go_button.pack(side="left", pady=3)

        # Web viewport
        viewport = ttk.Frame(row2)
        self.viewport = viewport
        viewport.pack(fill="both", expand=True)

        # Viewport content: just do text for now
        text = ReadOnlyText(viewport)
        self.text = text
        self.render_page()
        text_font = pick_font(
            [
                "Charis SIL",
                "Source Serif Pro",
                "Cambria",
                "Georgia",
                "DejaVu Serif",
                "Times New Roman",
                "Times",
            ]
        )
        mono_font = pick_font(["Ubuntu Mono", "Consolas", "Courier"])
        text.config(
            font=(text_font, 13), bg="#fff8dc", fg="black", padx=5, pady=5,
        )
        text.tag_config("link", foreground="blue", underline=1)
        text.tag_config(
            "pre",
            font=(mono_font, 13),
            # background="#ffe4c4",
            # selectbackground=text.cget("selectbackground"),
        )
        text.pack(side="left", fill="both", expand=True)

        text_scrollbar = ttk.Scrollbar(viewport, command=text.yview)
        text["yscrollcommand"] = text_scrollbar.set
        text_scrollbar.pack(side="left", fill="y")

        style = ttk.Style()
        if sys.platform == "win32":
            style.theme_use("vista")
        elif sys.platform == "darwin":
            style.theme_use("aqua")
        else:
            style.theme_use("clam")

    def _on_go(self, ev=None):
        if self.go_callback is not None:
            self.go_callback("gemini://" + self.address_bar.get())

    def render_page(self):
        self.text.delete("1.0", "end")

        if not self.model.gemini_nodes:
            self.text.insert("end", self.model.plaintext)
        else:
            for node in self.model.gemini_nodes:
                render_node(node, self.text)


def render_node(node: GeminiNode, widget: Text):
    nodetype = type(node)
    if nodetype is TextNode:
        widget.insert("end", node.text + "\n")
    elif nodetype is LinkNode:
        widget.insert("end", "=> ")
        widget.insert("end", f"{node.url}", ("link",))
        if node.name:
            widget.insert("end", f" {node.name}")
        widget.insert("end", "\n")
    elif nodetype is PreformattedNode:
        widget.insert("end", f"```\n{node.text}\n```\n", ("pre",))
    else:
        widget.insert("end", node.text + "\n")
