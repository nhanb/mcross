McRoss is a WIP [gemini://](https://gemini.circumlunar.space/) browser
written in python and tkinter.

It currently looks like this:

![](https://p.caophim.net/87.png)

Happy-path surfing and link-visiting already works.
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
- [ ] separate I/O thread to avoid blocking GUI
- [ ] more visual indicators - maybe a status bar at the bottom
- [x] parse gemini's advanced line types
- [ ] configurable document styling
- [ ] configurable TLS to accomodate self-signed sites?

Long term high-level goals:

- Should be easy for end users to install. If the word `rustup` exists in the
  installation guide for your G U I application then I'm sorry it's not
  software made for people to _use_.
- Should be responsive & pleasant to use. The Castor browser doesn't have
  visual indicators at all, for example, when clicking on a link it just
  appears to do nothing until the new page is completely loaded.
- The viewport should be rendered so that its content can be copied and still
  remain equivalent, valid gemini markup. Abolish the content creator vs
  consoomer divide!
- Lightweight, in terms of both disk space & memory/cpu usage. It's completely
  unoptimized at the moment but tkinter and zero-dependency python gives us a
  fairly good starting point imo.

# Server bugs/surprises

## Forces gemini:// in request

Spec says protocol part is optional, but if I omit that one the server will
respond with `53 No proxying to other hosts!`.

## Newline

Spec says a newline should be \r\n but the server running
gemini.circumlunar.space just uses \n every time.
