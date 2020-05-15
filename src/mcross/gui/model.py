from typing import List

from .. import document
from ..transport import GeminiUrl

DEMO_TEXT = """\
# Welcome to McRoss Browser

## List

* おぼえていますか　目と目が会った時を
* Do you remember? The time when our eyes first met?
* おぼえていますか　手と手触れ会った時
* Do you remember? The time when our hands first touched?

## Links

=> gemini://gemini.circumlunar.space/	Gemini homepage
=> gemini://gus.guru/     Gemini Universal Search engine
=> gemini://gemini.conman.org/test/torture/ 	Gemini client torture test

=> relative/ Relative link
=> /relative/ Relative link starting with "/"
=> https://lists.orbitalfox.eu/listinfo/gemini?foo=bar HTTP link

## Codes

```
[tool.poetry]
name = "mcross"
version = "0.1.0"
description = "Do you remember www?"
authors = ["nhanb <hi@imnhan.com>"]
license = "MIT"
```
"""


class History:
    h: List[GeminiUrl]
    current_index: int

    def __init__(self):
        self.h = []
        self.current_index = None

    def visit(self, url: GeminiUrl):
        # remove forward history first:
        if self.current_index is not None:
            self.h = self.h[: self.current_index + 1]
        self.h.append(url)
        self.current_index = len(self.h) - 1

    def go_back(self):
        if self.can_go_back():
            self.current_index -= 1

    def go_forward(self):
        if self.can_go_forward():
            self.current_index += 1

    def can_go_back(self):
        return self.current_index not in [None, 0]

    def can_go_forward(self):
        return self.current_index is not None and self.current_index < len(self.h) - 1

    def get_current_url(self):
        try:
            return self.h[self.current_index]
        except (IndexError, TypeError):
            return None


class Model:
    plaintext = ""
    gemini_nodes = None
    history: History

    def __init__(self):
        self.history = History()
        self.update_content(DEMO_TEXT)

    def update_content(self, plaintext):
        self.plaintext = plaintext
        self.gemini_nodes = []
        try:
            self.gemini_nodes = document.parse(plaintext)
        except Exception:
            print("Invalid gemini document!")
