# WIP

Developed against gemini://gemini.circumlunar.space/ because apparently
it's the only one if a valid TLS cert.

It currently looks like this: https://junk.imnhan.com/beans.mp4

# Deps

- python3.7+
- idlelib (it's supposed to be in the standard lib but Ubuntu for example
  splits it into a separate package)

# Server bugs/surprises

## Forces gemini:// in request

Spec says protocol part is optional, but if I omit that one the server will
respond with `53 No proxying to other hosts!`

```
<URL> is a UTF-8 encoded absolute URL, of maximum length 1024 bytes.
If the scheme of the URL is not specified, a scheme of gemini:// is
implied.
```
