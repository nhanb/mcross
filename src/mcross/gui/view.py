import logging
import sys
from tkinter import Text, Tk, font, ttk

from ..document import (
    GeminiNode,
    H1Node,
    H2Node,
    H3Node,
    LinkNode,
    ListItemNode,
    PreformattedNode,
    TextNode,
)
from .model import Model
from .widgets import AltButton, McEntry, ReadOnlyText

# OS-specific values
if sys.platform == "win32":
    TTK_THEME = "vista"
    POINTER_CURSOR = "center_ptr"
    WAITING_CURSOR = "wait"
elif sys.platform == "darwin":
    TTK_THEME = "aqua"
    POINTER_CURSOR = "pointinghand"
    WAITING_CURSOR = "wait"
else:
    TTK_THEME = "clam"
    POINTER_CURSOR = "hand1"
    WAITING_CURSOR = "watch"


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


def register_status_bar_log_handler(status_bar: ttk.Label):
    class StatusBarHandler(logging.Handler):
        def emit(self, record):
            status_bar.config(text=self.format(record))

    logger = logging.getLogger("statusbar")
    logger.setLevel(logging.INFO)
    logger.addHandler(StatusBarHandler())


class View:
    model: Model
    address_bar: ttk.Entry
    go_btn: AltButton
    back_btn: AltButton
    forward_btn: AltButton
    text: Text
    status_bar: ttk.Label

    allow_changing_cursor = True

    go_callback = None
    link_click_callback = None
    back_callback = None
    forward_callback = None

    def __init__(self, root: Tk, model: Model, fonts=(None, None)):
        self.model = model

        # first row - address bar + buttons
        row1 = ttk.Frame(root)
        row1.pack(fill="x")

        # second row - web viewport
        row2 = ttk.Frame(root)
        row2.pack(fill="both", expand=True)

        # third row - status bar
        status_bar = ttk.Label(root)
        self.status_bar = status_bar
        status_bar.config(justify="right")
        status_bar.pack(fill="x")
        register_status_bar_log_handler(status_bar)

        # Back/Forward buttons
        back_btn = AltButton(
            row1,
            text="◀",
            width=3,
            command=lambda: self.back_callback(),
            root=root,
            alt_char_index=0,
            alt_key="Left",
        )
        forward_btn = AltButton(
            row1,
            text="▶",
            width=3,
            command=lambda: self.forward_callback(),
            root=root,
            alt_char_index=0,
            alt_key="Right",
        )
        back_btn.pack(side="left", padx=2)
        forward_btn.pack(side="left", padx=2)
        self.back_btn = back_btn
        self.forward_btn = forward_btn

        # Address bar prefix
        address_prefix = ttk.Label(row1, text="gemini://")
        address_prefix.pack(side="left")

        # Address bar
        address_bar = McEntry(row1)
        self.address_bar = address_bar
        address_bar.pack(side="left", fill="both", expand=True, pady=3)
        address_bar.bind("<Return>", self._on_go)
        address_bar.bind("<KP_Enter>", self._on_go)
        address_bar.focus_set()

        def on_ctrl_l(ev):
            address_bar.focus()
            address_bar.select_all()

        root.bind("<Control-l>", on_ctrl_l)

        # Go button
        go_btn = AltButton(
            row1, text="Go", root=root, alt_char_index=0, command=self._on_go, width=5
        )
        self.go_btn = go_btn
        go_btn.pack(side="left", padx=2, pady=3)

        # Main viewport implemented as a Text widget.
        text = ReadOnlyText(row2, wrap="word")
        self.text = text
        self.render_page()
        if fonts[0] is None:
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
        else:
            text_font = fonts[0]

        if fonts[1] is None:
            mono_font = pick_font(
                [
                    "Ubuntu Mono",
                    "Consolas",
                    "Courier",
                    "TkFixedFont"
                ]
            )
        else:
            mono_font = fonts[1]

        text.config(
            font=(text_font, 13),
            bg="#fff8dc",
            fg="black",
            padx=5,
            pady=5,
            # hide blinking insertion cursor:
            insertontime=0,
            # prevent text widget from pushing scrollbar/status bar out of the window:
            width=1,
            height=1,
        )
        text.pack(side="left", fill="both", expand=True)
        text.tag_config("link", foreground="brown")
        text.tag_bind("link", "<Enter>", self._on_link_enter)
        text.tag_bind("link", "<Leave>", self._on_link_leave)
        text.tag_bind("link", "<Button-1>", self._on_link_click)
        text.tag_config("pre", font=(mono_font, 13))
        text.tag_config("listitem", foreground="#044604")

        base_heading_font = font.Font(font=text["font"])
        base_heading_font.config(weight="bold")
        h1_font = font.Font(font=base_heading_font)
        h1_font.config(size=h1_font["size"] + 8)
        text.tag_config("h1", font=h1_font)
        h2_font = font.Font(font=base_heading_font)
        h2_font.config(size=h2_font["size"] + 4)
        text.tag_config("h2", font=h2_font)
        h3_font = font.Font(font=base_heading_font)
        text.tag_config("h3", font=h3_font)

        text_scrollbar = ttk.Scrollbar(row2, command=text.yview)
        text["yscrollcommand"] = text_scrollbar.set
        text_scrollbar.pack(side="left", fill="y")

        style = ttk.Style()
        style.theme_use(TTK_THEME)

    def _on_go(self, ev=None):
        orig_url = self.address_bar.get()
        url = orig_url.strip()

        if url.startswith("gemini://"):
            url = url[9:]

        if not url:
            return

        if url != orig_url:
            self.address_bar.delete(0, "end")
            self.address_bar.insert(0, url)

        if self.go_callback is not None:
            self.go_callback("gemini://" + url)

    def _on_link_enter(self, ev):
        if self.allow_changing_cursor:
            self.text.config(cursor=POINTER_CURSOR)

    def _on_link_leave(self, ev):
        if self.allow_changing_cursor:
            self.text.config(cursor="xterm")

    def _on_link_click(self, ev):
        raw_url = get_content_from_tag_click_event(ev)
        self.link_click_callback(raw_url)

    def render_page(self):
        # Enable/Disable forward/back buttons according to history
        self.back_btn.config(
            state="normal" if self.model.history.can_go_back() else "disabled"
        )
        self.forward_btn.config(
            state="normal" if self.model.history.can_go_forward() else "disabled"
        )

        # Update url in address bar
        current_url = self.model.history.get_current_url()
        if current_url is not None:
            self.address_bar.delete(0, "end")
            self.address_bar.insert(0, current_url.without_protocol())

        # Update viewport
        self.text.delete("1.0", "end")
        if not self.model.gemini_nodes:
            self.text.insert("end", self.model.plaintext)
        else:
            for node in self.model.gemini_nodes:
                render_node(node, self.text)
            # delete final trailing newline:
            self.text.delete("insert-1c", "insert")


def render_node(node: GeminiNode, widget: Text):
    nodetype = type(node)
    if nodetype is TextNode:
        widget.insert("end", node.text)
    elif nodetype is LinkNode:
        widget.insert("end", "=> ")
        widget.insert("end", node.url, ("link",))
        if node.name:
            widget.insert("end", f" {node.name}")
    elif nodetype is PreformattedNode:
        widget.insert("end", f"```\n{node.text}\n```", ("pre",))
    elif nodetype is ListItemNode:
        widget.insert("end", node.text, ("listitem",))
    elif nodetype is H1Node:
        widget.insert("end", node.text, ("h1",))
    elif nodetype is H2Node:
        widget.insert("end", node.text, ("h2",))
    elif nodetype is H3Node:
        widget.insert("end", node.text, ("h3",))
    else:
        widget.insert("end", node.text)

    widget.insert("end", "\n")


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
