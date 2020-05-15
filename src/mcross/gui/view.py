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
        picked = names[-1]

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
                "TkTextFont",
            ]
        )
        mono_font = pick_font(["Ubuntu Mono", "Consolas", "Courier", "TkFixedFont"])
        text.config(
            font=(text_font, 13),
            bg="#fff8dc",
            fg="black",
            padx=5,
            pady=5,
            insertontime=0,  # hide blinking insertion cursor
        )
        text.tag_config("link", foreground="brown")
        text.tag_bind("link", "<Enter>", self._on_link_enter)
        text.tag_bind("link", "<Leave>", self._on_link_leave)
        text.tag_bind("link", "<Button-1>", self._on_link_click)
        text.tag_config("pre", font=(mono_font, 13))
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

    def _on_link_enter(self, ev):
        self.text.config(cursor="hand1")

    def _on_link_leave(self, ev):
        self.text.config(cursor="xterm")

    def _on_link_click(self, ev):
        raw_url = get_content_from_tag_click_event(ev)
        self.link_click_callback(raw_url)

    def render_page(self):
        # Update url in address bar
        if self.model.current_url is not None:
            self.address_bar.delete(0, "end")
            self.address_bar.insert(0, self.model.current_url.without_protocol())

        # Update viewport
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


def get_content_from_tag_click_event(event):
    # get the index of the mouse click
    index = event.widget.index("@%s,%s" % (event.x, event.y))

    # get the indices of all "link" tags
    tag_indices = list(event.widget.tag_ranges("link"))

    # iterate them pairwise (start and end index)
    for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
        # check if the tag matches the mouse click index
        if event.widget.compare(start, "<=", index) and event.widget.compare(
            index, "<", end
        ):
            # return string between tag start and end
            return event.widget.get(start, end)
