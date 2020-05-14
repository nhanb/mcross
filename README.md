![do you remember wwww?](https://p.caophim.net/81.webp)

McCross is a WIP [gemini://](https://gemini.circumlunar.space/) browser,
built in loving memory of a simpler, more innocent time.

Developed against gemini://gemini.circumlunar.space/ because apparently
it's the only one with a valid, CA-approved TLS cert.

It currently looks like this:

![](https://p.caophim.net/82.png)

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
