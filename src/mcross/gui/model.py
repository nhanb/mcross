from .. import document

DEMO_TEXT = """\
# Welcome to McRoss Browser

## List

* おぼえていますか　目と目が会った時を
* Do you remember? The time when our eyes first met?
* おぼえていますか　手と手触れ会った時
* Do you remember? The time when our hands first touched?

## Codes

```
[tool.poetry]
name = "mcross"
version = "0.1.0"
description = "Do you remember www?"
authors = ["nhanb <hi@imnhan.com>"]
license = "MIT"
```

## Links

=> gemini.circumlunar.space/docs/	Gemini documentation
=> gemini://gemini.circumlunar.space/software/ Gemini software
=> gemini.circumlunar.space/servers/     Known Gemini servers
=> gemini://gus.guru/	Gemini Universal Search engine
=> https://lists.orbitalfox.eu/listinfo/gemini	Gemini mailing list
=> https://portal.mozz.us/?url=gemini%3A%2F%2Fgemini.circumlunar.space%2F&fmt=fixed	Gemini-to-web proxy service
=> https://proxy.vulpes.one/gemini/gemini.circumlunar.space	Another Gemini-to-web proxy service
=> gemini://gemini.conman.org/test/torture/	Gemini client torture test
"""


class Model:
    plaintext = ""
    gemini_nodes = None

    def __init__(self):
        self.update_content(DEMO_TEXT)

    def update_content(self, plaintext):
        self.plaintext = plaintext
        self.gemini_nodes = []
        try:
            self.gemini_nodes = document.parse(plaintext)
        except Exception:
            print("Invalid gemini document!")
