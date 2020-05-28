McRoss is a minimal and usable [gemini://](https://gemini.circumlunar.space/)
browser written in python and tkinter, meaning it Just Works (tm) on any
self-respecting desktop OS: Linux, Windows, Mac OS, and maybe the BSDs?
Never tried one of those.

It currently looks like this:

![](https://junk.imnhan.com/mcross.png)

Or check out the demo video: https://junk.imnhan.com/mcross.mp4

Surfing plaintext and gemini content is already working well.
See feature checklist below for more details.


# Installation

```sh
pip install mcross
mcross
```

Better distribution methods to be explored later.
Maybe it's finally time to try nuitka?


# Development

Deps:

- python3.7+
- idlelib (it's supposed to be in the standard lib but Ubuntu for example
  splits it into a separate package)
- curio - for async I/O so that it doesn't block the UI.

To get started:

```sh
pyenv install 3.7.7
pyenv virtualenv 3.7.7 mcross
pyenv activate
poetry install
mcross

# to publish, first bump version in pyproject.toml then
poetry publish --build
```


# Feature checklist

- [x] back-forward buttons
- [x] handle redirects
- [x] non-blocking I/O using curio
- [x] more visual indicators: waiting cursor, status bar
- [x] parse gemini's advanced line types
- [ ] TOFU TLS (right now it accepts whatever)
- [ ] properly handle mime types (gemini/plaintext/binary)
- [ ] configurable document styling
- [ ] human-friendly distribution

Long term high-level goals:

## Easy for end users to install

If the words `cargo build` exists in the installation guide for your G U I
application then I'm sorry it's not software made for people to _use_.

## What-you-see-is-what-you-write

A rendered text/gemini viewport should preserve its original text content.
This way once you've read a gemini page on the browser, you already know how to
write one. No "View Source" necessary.

## Responsive & pleasant to use

The Castor browser doesn't have visual indicators at all, for example, when
clicking on a link it just appears to do nothing until the new page is
completely loaded. That is A Bad Thing (tm).

## Lightweight

In terms of both disk space & memory/cpu usage.
The python/tkinter combo already puts us at a pretty good starting point.

# Server bugs/surprises

## Forces gemini:// in request

Spec says protocol part is optional, but if I omit that one the server will
respond with `53 No proxying to other hosts!`.

## Newline

Spec says a newline should be \r\n but the server running
gemini.circumlunar.space just uses \n every time.
