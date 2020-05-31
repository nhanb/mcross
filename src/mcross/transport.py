import re
import ssl
from urllib.parse import urlparse

import curio

MAX_RESP_HEADER_BYTES = 2 + 1 + 1024 + 2  # <STATUS><whitespace><META><CR><LF>
MAX_RESP_BODY_BYTES = 1024 * 1024 * 5
MAX_REDIRECTS = 3
MAX_REQUEST_SECONDS = 30


class Response:
    __slots__ = ("status", "meta", "body", "url")

    def __init__(self, status: str, meta: str, url, body: bytes = None):
        self.status = status
        self.meta = meta
        self.body = body
        self.url = url

    def __repr__(self):
        return f"Response(status={repr(self.status)}, meta={repr(self.meta)})"


def _parse_resp_header(header, pattern=re.compile(r"^(\d\d)\s+(.{,1024})\r\n$")):
    match = pattern.match(header)
    assert match is not None, f"Malformed response header: {header}"
    status = match.group(1)
    meta = match.group(2)
    return status, meta


# TODO: GeminiUrl's context-aware parse() method probably doesn't belong
# in a "transport" module.


class UnsupportedProtocolError(Exception):
    pass


class NonAbsoluteUrlWithoutContextError(Exception):
    pass


class GeminiUrl:
    PROTOCOL = "gemini"
    __slots__ = ("host", "port", "path")
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
        if current_path == "":
            current_path = "/"
        return GeminiUrl(current_url.host, current_url.port, current_path + text)

    @staticmethod
    def parse_absolute_url(text):
        # TODO: urlparse doesn't seem that foolproof. Revisit later.
        parsed = urlparse(text)
        return GeminiUrl(parsed.hostname, parsed.port or 1965, parsed.path)


async def raw_get(url: GeminiUrl):
    # TODO: actually implement TOFU for TLS!
    # Right now it just accepts whatever
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    sock = await curio.open_connection(
        url.host, url.port, ssl=context, server_hostname=url.host
    )

    async with sock:
        await sock.sendall(f"gemini://{url.host}{url.path}\r\n".encode())
        header = b""
        remainder = b""
        while True:
            header += await sock.recv(4096)
            if b"\r\n" in header:
                idx = header.find(b"\r\n")
                remainder = header[(idx + 2) :]
                header = header[: (idx + 2)]
                break
            elif len(header) > MAX_RESP_HEADER_BYTES:
                break

        status, meta = _parse_resp_header(header.decode())
        resp = Response(status=status, meta=meta, url=url)

        if status.startswith("2"):
            body = remainder
            msg = await sock.recv(4096)
            body += msg
            while msg and len(body) <= MAX_RESP_BODY_BYTES:
                msg = await sock.recv(4096)
                body += msg
            resp.body = body

        return resp


async def get(url: GeminiUrl, redirect_count=0):
    resp = await curio.timeout_after(MAX_REQUEST_SECONDS, raw_get, url)
    if resp.status.startswith("3") and redirect_count < MAX_REDIRECTS:
        redirect_count += 1
        new_url = GeminiUrl.parse_absolute_url(resp.meta)
        print(f"Redirecting to {new_url}, count={redirect_count}")
        return await get(new_url, redirect_count)
    return resp
