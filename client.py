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


def get(absolute_url="gemini://gemini.circumlunar.space/"):
    url = parse_absolute_url(absolute_url)
    port = url.port or 1965

    context = ssl.create_default_context()
    with socket.create_connection((url.netloc, port)) as sock:
        with context.wrap_socket(sock, server_hostname=url.netloc) as ssock:
            ssock.send(f"gemini://{url.netloc}{url.path}\r\n".encode())
            header = ssock.recv(MAX_RESP_HEADER_BYTES).decode()
            status, meta = _parse_resp_header(header)
            resp = Response(status=status, meta=meta)

            if status.startswith("2"):
                resp.body = ssock.recv(MAX_RESP_BODY_BYTES)

            return resp


def _parse_resp_header(header, pattern=re.compile(r"^(\d\d) (.{,1024})\r\n$")):
    match = pattern.match(header)
    assert match is not None, f"Malformed response header: {header}"
    status = match.group(1)
    meta = match.group(2)
    return status, meta


def parse_absolute_url(absolute_url):
    # TODO: this is not exactly safe. Do proper parsing later.
    assert absolute_url.startswith("gemini://"), f"Malformed url: {absolute_url}"
    parsed = urlparse(absolute_url)
    return parsed
