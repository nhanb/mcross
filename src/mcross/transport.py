import re
import socket
import ssl
from urllib.parse import urlparse

MAX_RESP_HEADER_BYTES = 2 + 1 + 1024 + 2  # <STATUS><whitespace><META><CR><LF>
MAX_RESP_BODY_BYTES = 1024 * 1024 * 5


# Wanted to use a dataclass here but ofc it doesn't allow a slotted class to
# have fields with default values:
# https://stackoverflow.com/questions/50180735/how-can-dataclasses-be-made-to-work-better-with-slots
# Maaaaybe I should just use attrs and call it a day.
class Response:
    __slots__ = ("status", "meta", "body")

    def __init__(self, status: str, meta: str, body: bytes = None):
        self.status = status
        self.meta = meta
        self.body = body

    def __repr__(self):
        return f"Response(status={repr(self.status)}, meta={repr(self.meta)})"


def _parse_resp_header(header, pattern=re.compile(r"^(\d\d)\s+(.{,1024})\r\n$")):
    match = pattern.match(header)
    assert match is not None, f"Malformed response header: {header}"
    status = match.group(1)
    meta = match.group(2)
    return status, meta


def parse_absolute_url(absolute_url):
    assert absolute_url.startswith("gemini://"), f"Malformed url: {absolute_url}"
    parsed = urlparse(absolute_url)
    return parsed


# TODO: GeminiUrl's context-aware parse() method probably doesn't belong
# in a "transport" module.


class UnsupportedProtocolError(Exception):
    pass


class NonAbsoluteUrlWithoutContextError(Exception):
    pass


class GeminiUrl:
    PROTOCOL = "gemini"
    host: str
    port: int
    path: str

    def __init__(self, host, port, path):
        """
        You probably don't want to use this constructor directly.
        Use one of the parse methods instead.
        """
        self.host = host
        self.port = port
        self.path = path

    def __repr__(self):
        return f"{self.PROTOCOL}://{self.host}:{self.port}{self.path}"

    def without_protocol(self):
        if self.port == 1965:
            return f"{self.host}{self.path}"
        else:
            return f"{self.host}:{self.port}{self.path}"

    @classmethod
    def parse(cls, text, current_url):
        assert not re.search(r"\s", text), "Url should not contain any whitespace!"

        protocol = urlparse(text).scheme
        if protocol == cls.PROTOCOL:
            return cls.parse_absolute_url(text)

        if protocol:
            raise UnsupportedProtocolError(protocol)

        if current_url is None:
            raise NonAbsoluteUrlWithoutContextError(text)

        # relative url starting from top level
        if text.startswith("/"):
            return GeminiUrl(current_url.host, current_url.port, text)

        # just relative url:
        # trim stuff after the last `/` - for example:
        #   current url: gemini://example.com/foo/bar
        #   raw url text: yikes
        #   => parsed url: gemini://example.com/foo/yikes
        current_path = current_url.path[: current_url.path.rfind("/") + 1]
        return GeminiUrl(current_url.host, current_url.port, current_path + text)

    @staticmethod
    def parse_absolute_url(text):
        # TODO: urlparse doesn't seem that foolproof. Revisit later.
        parsed = urlparse(text)
        return GeminiUrl(parsed.hostname, parsed.port or 1965, parsed.path)


def get(url: GeminiUrl):
    context = ssl.create_default_context()
    with socket.create_connection((url.host, url.port)) as sock:
        with context.wrap_socket(sock, server_hostname=url.host) as ssock:
            ssock.send(f"gemini://{url.host}{url.path}\r\n".encode())
            header = ssock.recv(MAX_RESP_HEADER_BYTES).decode()
            status, meta = _parse_resp_header(header)
            resp = Response(status=status, meta=meta)

            if status.startswith("2"):
                resp.body = ssock.recv(MAX_RESP_BODY_BYTES)

            return resp
