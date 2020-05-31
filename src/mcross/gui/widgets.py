from idlelib.redirector import WidgetRedirector
from tkinter import Text, ttk


# Can't just use a Text widget with state='disabled' because that would
# also disable Ctrl+C / Ctrl+V.
# Further low-level reading:
# https://wiki.tcl-lang.org/page/Read%2Donly+text+widget
class ReadOnlyText(Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")

        self.bind("<Control-a>", self._on_ctrl_a)

    def _on_ctrl_a(self, ev):
        self.tag_add("sel", "1.0", "end")
        return "break"


class McEntry(ttk.Entry):
    """
    Entry widget with reasonable defaults
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bind("<Control-a>", self.select_all)

    def select_all(self, ev=None):
        self.select_range(0, "end")
        self.icursor("end")
        return "break"


class AltButton(ttk.Button):
    """
    Like Button but also supports Alt-<Key> shortcut (like Qt's Accelerator Keys).
    Accepts 3 extra args:
    - root: The root tk instance.
    - alt_char_index: Character index to be underlined when Alt is held down.
    - alt_key (optional): Explicit key name to pass to bind().
      If alt_key is not provided then it will be inferred from alt_char_index.
    """

    def __init__(self, *args, root, alt_char_index, alt_key=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = root

        alt_key = alt_key or self["text"][alt_char_index].lower()
        assert alt_key not in root.alt_shortcuts, f"Duplicate shortcut for {alt_key}"
        root.alt_shortcuts.add(alt_key)

        root.bind("<Alt_L>", self._alt_down, add="+")
        root.bind("<KeyRelease-Alt_L>", self._alt_up, add="+")
        root.bind(f"<Alt-{alt_key}>", self._alt_button_down)
        root.bind(f"<Alt-KeyRelease-{alt_key}>", self._alt_button_up)

        self.alt_char_index = alt_char_index
        self.alt_key = alt_key

    def _alt_down(self, event):
        self.config(underline=self.alt_char_index)

    def _alt_up(self, event):
        self.config(underline=-1)

    def _alt_button_down(self, event):
        self.state(["pressed"])

    def _alt_button_up(self, event):
        self.invoke()
        self.state(["!pressed"])
