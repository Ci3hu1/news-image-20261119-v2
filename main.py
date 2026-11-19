#!/usr/bin/env python3
"""news-image-20261119-v2 entry point (make.fun bounty).

Pure standard library.  The poster is bundled as news.png (rendered by
render.py); this file verifies it by SHA-256 and copies the exact bytes to
the output path, so repeated runs are byte-identical.

Output path order (first that works):
  1. $MAKEFUN_OUTPUT_DIR/entry.png
  2. /output/entry.png
  3. output.png next to this file

Usage:
  python3 main.py           write entry.png to the first usable path
  python3 main.py --check   verify the bundled image, write nothing
"""
import hashlib
import os
import sys

EXPECTED_SHA256 = ("66ccb7a8c0bbbae868a1658700ca7681eea933a73d835e095b6a405021"
                   "05cd29")
IMAGE_NAME = "news.png"
IMAGE_SIZE = 62136


def _here():
    return os.path.dirname(os.path.abspath(__file__))


def bundled_bytes():
    path = os.path.join(_here(), IMAGE_NAME)
    with open(path, "rb") as f:
        return f.read()


def verify(data):
    """Check the bundled image: size + SHA-256. Raises ValueError."""
    if len(data) != IMAGE_SIZE:
        raise ValueError("bundled %s is %d bytes, expected %d"
                         % (IMAGE_NAME, len(data), IMAGE_SIZE))
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("bundled %s SHA-256 mismatch: %s"
                         % (IMAGE_NAME, digest))
    # PNG signature + 1024x1024 IHDR sanity check.
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("bundled %s is not a PNG" % IMAGE_NAME)
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (1024, 1024):
        raise ValueError("bundled %s is %dx%d, expected 1024x1024"
                         % (IMAGE_NAME, width, height))


def output_path():
    """First usable output path, in the required order."""
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        return os.path.join(env_dir, "entry.png")
    if os.path.isdir("/output"):
        return "/output/entry.png"
    return os.path.join(_here(), "output.png")


def write_entry():
    data = bundled_bytes()
    verify(data)
    dest = output_path()
    parent = os.path.dirname(dest)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    return dest, len(data)


def main(argv):
    if "--check" in argv:
        verify(bundled_bytes())
        print("check ok: %s %d bytes sha256 %s"
              % (IMAGE_NAME, IMAGE_SIZE, EXPECTED_SHA256))
        return 0
    dest, n = write_entry()
    print("wrote %s (%d bytes)" % (dest, n))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
