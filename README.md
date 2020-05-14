McCross is a WIP [gemini://](https://gemini.circumlunar.space/) browser
written in python and tkinter.

It's developed against gemini://gemini.circumlunar.space/ because apparently
that's the only server with a valid, CA-approved TLS cert.

It currently looks like this:

![](https://p.caophim.net/84.png)

Happy-path fetching and rendering already works.
Clicking on links isn't implemented yet though.
I'm still figuring out stuff as I go.

# Installation

```sh
pip install mccross
mccross
```

# Deps

- python3.7+
- idlelib (it's supposed to be in the standard lib but Ubuntu for example
  splits it into a separate package)

# Server bugs/surprises

## Forces gemini:// in request

Spec says protocol part is optional, but if I omit that one the server will
respond with `53 No proxying to other hosts!`.

## Newline

Spec says a newline should be \r\n but the server running
gemini.circumlunar.space just uses \n every time.
