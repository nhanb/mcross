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

        self.bind("<Control-a>", self._on_ctrl_a)

    def _on_ctrl_a(self, ev):
        self.select_range(0, "end")
        self.icursor("end")
        return "break"
