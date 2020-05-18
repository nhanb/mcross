import re

NEWLINE = "\n"
LINK_LINE_PATTERN = re.compile(r"^=>[ \t]+(\S+)([ \t]+(.+))?$")
HEADING_LINE_PATTERN = re.compile(r"^(#{1,3})\s+(.+)$")


class GeminiNode:
    __slots__ = ("text",)
    text: str

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.text.__repr__()}"


class TextNode(GeminiNode):
    pass


class ListItemNode(GeminiNode):
    pass


class H1Node(GeminiNode):
    pass


class H2Node(GeminiNode):
    pass


class H3Node(GeminiNode):
    pass


class LinkNode(GeminiNode):
    __slots__ = ("url", "name")
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

        elif line.startswith("*"):
            nodes.append(ListItemNode(line))

        elif line.startswith("#"):
            match = HEADING_LINE_PATTERN.match(line)
            if not match:
                nodes.append(TextNode(line))
                continue
            # heading_text = match.group(2)  # not used yet
            hashes = match.group(1)
            level = len(hashes)
            if level == 1:
                nodes.append(H1Node(line))
            elif level == 2:
                nodes.append(H2Node(line))
            elif level == 3:
                nodes.append(H3Node(line))

        else:
            nodes.append(TextNode(line))

    return nodes
