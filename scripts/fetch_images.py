#!/usr/bin/env python3
"""Copy images and video from the old WordPress site into static/images/.

The content files point at the original files on sites.ua.edu. After this
script runs, build.py automatically uses the local copies instead, so the new
site keeps working even if the old site is removed. Existing files are skipped.

Run it from GitHub: Actions > "Import images from old site" > Run workflow.
Or on your own computer:  python scripts/fetch_images.py
"""
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "static" / "images"
PATTERN = re.compile(r"https://sites\.ua\.edu/enablelab/files/[^\s\"'}]+\.(?:jpe?g|png|gif|webp|svg|mp4)", re.I)
MAX_BYTES = 45 * 1024 * 1024  # GitHub warns above 50 MB per file and rejects above 100 MB


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    urls = set()
    for f in (ROOT / "content").glob("*.yml"):
        urls.update(PATTERN.findall(f.read_text(encoding="utf-8")))
    ok = skipped = failed = 0
    for url in sorted(urls):
        target = DEST / url.rsplit("/", 1)[-1]
        if target.exists():
            skipped += 1
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ENABLE-Lab-site-migration/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                size = int(resp.headers.get("Content-Length") or 0)
                if size > MAX_BYTES:
                    print(f"too large to store in GitHub ({size // 2**20} MB), left on old site: {url}")
                    failed += 1
                    continue
                data = resp.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                print(f"too large to store in GitHub, left on old site: {url}")
                failed += 1
                continue
            target.write_bytes(data)
            ok += 1
            print(f"saved {target.name} ({len(data) // 1024} KB)")
        except Exception as exc:  # report and keep going
            failed += 1
            print(f"could not download {url}: {exc}")
    print(f"\nDone: {ok} downloaded, {skipped} already present, {failed} not downloaded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
