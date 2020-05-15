McRoss is a WIP [gemini://](https://gemini.circumlunar.space/) browser
written in python and tkinter.

It's developed against gemini://gemini.circumlunar.space/ because apparently
that's the only server with a valid, CA-approved TLS cert.

It currently looks like this:

![](https://p.caophim.net/84.png)

Happy-path surfing and link-visiting already works.
The UX is still terrible though (no back-forward buttons, UI-blocking network
requests, etc.).
I'm still figuring out stuff as I go.

# Installation

```sh
pip install mcross
mcross
```

# Deps

- python3.7+
- idlelib (it's supposed to be in the standard lib but Ubuntu for example
  splits it into a separate package)

# Feature checklist

- [x] back-forward buttons
- [ ] separate I/O thread to avoid blocking GUI
- [ ] more visual indicators - maybe a status bar at the bottom
- [ ] parse gemini's advanced line types
- [ ] configurable document styling
- [ ] configurable TLS

# Server bugs/surprises

## Forces gemini:// in request

Spec says protocol part is optional, but if I omit that one the server will
respond with `53 No proxying to other hosts!`.

## Newline

Spec says a newline should be \r\n but the server running
gemini.circumlunar.space just uses \n every time.
