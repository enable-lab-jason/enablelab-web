#!/usr/bin/env python3
"""Check the built site (_site/) for broken internal links and missing alt text.

Runs automatically in GitHub Actions after every build. External links are
not fetched (that would make every build slow and flaky); only links between
pages of this site, #anchors and local files are checked.
"""
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag

SITE = Path(__file__).resolve().parent.parent / "_site"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.no_alt = [], set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for attr in ("href", "src"):
            if a.get(attr) and tag != "link" or (tag == "link" and attr == "href" and a.get("rel") in ("stylesheet", "icon")):
                if a.get(attr):
                    self.links.append(a[attr])
        if tag == "img" and "alt" not in a:
            self.no_alt.append(a.get("src", "?"))


def main() -> int:
    if not SITE.exists():
        print("Run build.py first: _site/ does not exist.")
        return 1
    pages = {}
    for f in SITE.rglob("*.html"):
        p = Page()
        p.feed(f.read_text(encoding="utf-8"))
        pages[f] = p
    problems = []
    for f, p in pages.items():
        rel = f.relative_to(SITE)
        for src in p.no_alt:
            problems.append(f"{rel}: image without alt text: {src}")
        if rel.name == "404.html":
            continue  # uses absolute links to the live site
        for link in p.links:
            if link.startswith(("http://", "https://", "mailto:", "tel:", "data:", "//")):
                continue
            path, frag = urldefrag(link)
            target = f if not path else (f.parent / unquote(path)).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                problems.append(f"{rel}: broken link -> {link}")
                continue
            if frag and target.suffix == ".html":
                ids = pages[target].ids if target in pages else set()
                if frag not in ids:
                    problems.append(f"{rel}: link to missing anchor -> {link}")
    if problems:
        print("Link check found problems:\n  " + "\n  ".join(sorted(set(problems))))
        return 1
    print(f"Link check passed: {len(pages)} pages, no broken internal links, all images have alt text.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
