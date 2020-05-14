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
