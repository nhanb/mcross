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
from .widgets import ReadOnlyText

# OS-specific values
if sys.platform == "win32":
    TTK_THEME = "vista"
    POINTER_CURSOR = "center_ptr"
elif sys.platform == "darwin":
    TTK_THEME = "aqua"
    POINTER_CURSOR = "pointinghand"
else:
    TTK_THEME = "clam"
    POINTER_CURSOR = "hand1"


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
    go_btn: ttk.Button
    back_btn: ttk.Button
    forward_btn: ttk.Button
    text: Text

    go_callback = None
    link_click_callback = None
    back_callback = None
    forward_callback = None

    def __init__(self, root: Tk, model: Model):
        self.model = model

        # first row - address bar + buttons
        row1 = ttk.Frame(root)
        row1.pack(fill="x")

        # second row - web viewport
        row2 = ttk.Frame(root)
        row2.pack(fill="both", expand=True)

        # Back/Forward buttons
        back_btn = ttk.Button(
            row1, text="🡄", width=3, command=lambda: self.back_callback()
        )
        forward_btn = ttk.Button(
            row1, text="🡆", width=3, command=lambda: self.forward_callback()
        )
        back_btn.pack(side="left", padx=2)
        forward_btn.pack(side="left", padx=2)
        self.back_btn = back_btn
        self.forward_btn = forward_btn

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
        go_btn = ttk.Button(row1, text="三三ᕕ( ᐛ )ᕗ", command=self._on_go, width=10)
        self.go_btn = go_btn
        go_btn.pack(side="left", pady=3)

        # Main viewport implemented as a Text widget.
        text = ReadOnlyText(row2)
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
            # hide blinking insertion cursor:
            insertontime=0,
            # prevent verticle scrollbar from disappearing when window gets small:
            width=1,
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
        if self.go_callback is not None:
            self.go_callback("gemini://" + self.address_bar.get())

    def _on_link_enter(self, ev):
        self.text.config(cursor=POINTER_CURSOR)

    def _on_link_leave(self, ev):
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
