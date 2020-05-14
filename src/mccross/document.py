import re

NEWLINE = "\n"
LINK_LINE_PATTERN = re.compile(r"^=>[ \t]+(\S+)([ \t]+(.+))?$")


class GeminiNode:
    text: str

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.text.__repr__()}"


class TextNode(GeminiNode):
    pass


class LinkNode(GeminiNode):
    url: str
    name: str

    def __init__(self, text, url, name):
        self.text = text
        self.url = url
        self.name = name

    def __repr__(self):
        result = f"{self.__class__.__name__}: {self.url.__repr__()}"
        if self.name:
            result += f" {self.name.__repr__()}"
        return result


class PreformattedNode(GeminiNode):
    pass


def parse(text):
    """
    Naive one-pass parser.
    """
    nodes = []
    preformatted = None

    for line in text.strip().split(NEWLINE):

        if line == "```":
            if preformatted is None:
                # start preformatted mode
                preformatted = ""
            else:
                nodes.append(PreformattedNode(preformatted))
                preformatted = None

        elif preformatted is not None:
            if len(preformatted) > 0:
                preformatted += "\n"
            preformatted += line

        elif line.startswith("=> "):
            match = LINK_LINE_PATTERN.match(line)
            if not match:
                nodes.append(TextNode(line))
                continue
            url = match.group(1)
            name = match.group(3)  # may be None
            nodes.append(LinkNode(text=line, url=url, name=name))

        else:
            nodes.append(TextNode(line))

    return nodes


def test():
    return parse(
        """# Project Gemini\n\n## Overview\n\nGemini is a new internet protocol which:\n\n* Is heavier than gopher\n* Is lighter than the web\n* Will not replace either\n* Strives for maximum power to weight ratio\n* Takes user privacy very seriously\n\n## Resources\n\n=> docs/\tGemini documentation\n=> software/\tGemini software\n=> servers/\tKnown Gemini servers\n=> gemini://gus.guru/\tGemini Universal Search engine\n=> https://lists.orbitalfox.eu/listinfo/gemini\tGemini mailing list\n=> https://portal.mozz.us/?url=gemini%3A%2F%2Fgemini.circumlunar.space%2F&fmt=fixed\tGemini-to-web proxy service\n=> https://proxy.vulpes.one/gemini/gemini.circumlunar.space\tAnother Gemini-to-web proxy service\n=> gemini://gemini.conman.org/test/torture/\tGemini client torture test\n\n## Geminispace aggregator (experimental!)\n\n=> capcom/\tCAPCOM\n\n## Free Gemini hosting\n\n=> users/\tUsers with Gemini content on this server\n```\nfooo\nbar\n```\nBye.\n"""
    )
