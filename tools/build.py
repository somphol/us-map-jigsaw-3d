#!/usr/bin/env python3
"""Inline assets/mapdata.js into index.html between the build markers."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
DATA = ROOT / "assets" / "mapdata.js"
START = "/* MAP_DATA_START */"
END = "/* MAP_DATA_END */"


def main():
    html = HTML.read_text()
    data = DATA.read_text().strip()
    if START not in html or END not in html:
        raise SystemExit("build markers not found in index.html")
    head, rest = html.split(START, 1)
    _, tail = rest.split(END, 1)
    HTML.write_text(head + START + "\n" + data + "\n" + END + tail)
    print(f"inlined {len(data):,} bytes of map data into {HTML.name}")


if __name__ == "__main__":
    main()
