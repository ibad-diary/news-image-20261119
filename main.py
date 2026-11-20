#!/usr/bin/env python3
"""Round-2 entry for make.fun news-image-20261119.

The front page is pre-rendered by generate_image.py and shipped as
entry.png beside this file. This program only copies it into the
directory make.fun asks for, after checking it is a real PNG inside
the competition limits (at most 1 MiB, at most 1024x1024). It uses
nothing but the standard library and touches no network, so two runs
write exactly the same bytes.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "entry.png"
LIMIT_BYTES = 1024 * 1024
LIMIT_SIDE = 1024
MAGIC = b"\x89PNG\r\n\x1a\n"


def die(message):
    sys.stderr.write("main.py: %s\n" % message)
    sys.exit(1)


def main():
    src = os.path.join(HERE, NAME)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        with open(src, "rb") as handle:
            blob = handle.read()
    except OSError as exc:
        die("cannot read %s: %s" % (src, exc))
    if blob[:8] != MAGIC:
        die("%s is not a PNG file" % NAME)
    if len(blob) > LIMIT_BYTES:
        die("%s is %d bytes, over the 1 MiB limit" % (NAME, len(blob)))
    if len(blob) < 24 or blob[12:16] != b"IHDR":
        die("%s has no PNG header" % NAME)
    width, height = struct.unpack(">II", blob[16:24])
    if width > LIMIT_SIDE or height > LIMIT_SIDE:
        die("%s is %dx%d, over 1024x1024" % (NAME, width, height))
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, NAME)
    with open(dst, "wb") as handle:
        handle.write(blob)
    print("copied %s -> %s (%dx%d, %d bytes)"
          % (NAME, dst, width, height, len(blob)))


if __name__ == "__main__":
    main()
