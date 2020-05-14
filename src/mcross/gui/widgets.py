from idlelib.redirector import WidgetRedirector
from tkinter import Text


# Can't just use a Text widget with state='disabled' because that would
# also disable Ctrl+C / Ctrl+V.
# Further low-level reading:
# https://wiki.tcl-lang.org/page/Read%2Donly+text+widget
class ReadOnlyText(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")
