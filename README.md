McRoss is a WIP [gemini://](https://gemini.circumlunar.space/) browser
written in python and tkinter, meaning it Just Works (tm) on any
self-respecting desktop OS: Linux, Windows, Mac OS, maaaaybe the BSDs?
Never tried one of those.

It currently looks like this:

![](https://p.caophim.net/87.png)

Happy-path surfing already works.
The UX is still terrible though (see feature checklist below).
I'm still figuring out stuff as I go.


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
- [ ] handle redirects
- [ ] separate I/O thread to avoid blocking GUI
- [ ] more visual indicators - maybe a status bar at the bottom
- [x] parse gemini's advanced line types
- [ ] properly handle mime types (gemini/plaintext/binary)
- [ ] configurable document styling
- [ ] configurable TLS to accomodate self-signed sites?
- [ ] human-friendly distribution

Long term high-level goals:

## Easy for end users to install

If the word `rustup` exists in the installation guide for your G U I
application then I'm sorry it's not software made for people to _use_.

## Copy-friendly viewport

More specifically, its content when copied should still remain equivalent,
valid gemini markup. Abolish the content creator vs consoomer divide!

## Responsive & pleasant to use

The Castor browser doesn't have visual indicators at all, for example, when
clicking on a link it just appears to do nothing until the new page is
completely loaded. That is A Bad Thing (tm).

## Lightweight

In terms of both disk space & memory/cpu usage.
It's completely unoptimized at the moment but tkinter and zero-dependency
python gives us a fairly good starting point imo.


# Server bugs/surprises

## Forces gemini:// in request

Spec says protocol part is optional, but if I omit that one the server will
respond with `53 No proxying to other hosts!`.

## Newline

Spec says a newline should be \r\n but the server running
gemini.circumlunar.space just uses \n every time.
