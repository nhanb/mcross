McRoss is a minimal and usable [gemini://](https://gemini.circumlunar.space/)
browser written in python and tkinter, meaning it Just Works (tm) on any
self-respecting desktop OS: Linux, Windows, Mac OS, and maybe the BSDs?
Never tried one of those.

It currently looks like this:

![](https://junk.imnhan.com/mcross.png)

Surfing plaintext and gemini content is already working well. The catch is it
currently doesn't support downloading binary content and TOFU TLS verification.
See feature checklist below for more details.

See my [blog post][1] for the rationale behind this project.


# Installation

You need python 3.7 or higher. McRoss also uses `idlelib` which is supposed to
be included in the standard library but some linux distros split it into a
separate package which you'll need to install manually. I know at least [Ubuntu
and Void Linux][2] do this.

```sh
pip install mcross
mcross
```

Better distribution methods to be explored later.
Maybe it's finally time to try nuitka?

# Usage

Run `mcross -h` to get a full list of CLI arguments. The same arguments can
also be defined in a TOML config file: run `mcross-info` to know where this
file should be for your OS. For example, running mcross like this:

```sh
mcross --background-color pink -t "Ubuntu"
```

is the same as putting this in `$HOME/.config/mcross/mcross.toml` for linux:

```toml
background-color = "pink"
text-font = "Ubuntu"
```

The priority is CLI arg > config file > default.

Keyboard shortcuts:

- `Ctrl-l`: jump to address bar.
- Hold `Alt` to see possible button shortcuts underlined. This is what Qt calls
  [Accelerator Keys](https://doc.qt.io/qt-5/accelerators.html).


# Development

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

There are 2 McRoss-related mailing lists:

- [~nhanb/mcross-devel](https://lists.sr.ht/~nhanb/mcross-devel): discuss and
  submit your patches here
- [~nhanb/mcross-announce](https://lists.sr.ht/~nhanb/mcross-announce):
  low-volume announcement-only list

If you're not familiar with the mailing list workflow, check out
[git-send-email.io][3] and [mailing list etiquette][4]. [useplaintext.email][5]
also has useful plaintext setup tips for various email clients, though I don't
necessarily agree with its "plaintext or nothing" stance.


# Feature checklist

- [x] back-forward buttons
- [x] handle redirects
- [x] non-blocking I/O using curio
- [x] more visual indicators: waiting cursor, status bar
- [x] parse gemini's advanced line types
- [x] render `text/*` mime types with correct charset
- [ ] handle `binary/*` mime types
- [x] configurable document styling
- [ ] human-friendly distribution
- [ ] TOFU TLS (right now it always accepts self-signed certs)

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

# License

Copyright (C) 2020 Bùi Thành Nhân

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License version 3 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <https://www.gnu.org/licenses/>.

# Forks

McRoss development is... conservative and slow. If that bothers you, check out
[picross][6] which is a nice fork with more features (TOFU, tabs, among other
things).

[1]: https://hi.imnhan.com/posts/introducing-mcross-a-minimal-gemini-browser/
[2]: https://todo.sr.ht/~nhanb/mcross/3
[3]: https://git-send-email.io/
[4]: https://man.sr.ht/lists.sr.ht/etiquette.md
[5]: https://useplaintext.email/
[6]: https://git.sr.ht/~fkfd/picross
