from .. import document

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


class Model:
    current_url = None
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
