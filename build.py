#!/usr/bin/env python3
"""Build the ENABLE Lab website.

Reads the YAML files in content/, renders the Jinja2 templates in templates/,
copies static/ and writes a complete static website to _site/.

    python build.py            # production build (pretty URLs, e.g. /people/)
    python build.py --local    # links end in index.html so you can open
                               # _site/index.html straight from your disk

GitHub Actions runs this script on every push (see .github/workflows/).
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import os
import re
import shutil
import sys
from email.utils import format_datetime
from pathlib import Path

import yaml
from jinja2 import ChainableUndefined, Environment, FileSystemLoader
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "_site"

TYPE_LABELS = {"chapter": "Book chapter", "journal": "Journal article", "conference": "Conference paper"}


class BuildError(Exception):
    """A problem in the content files, reported in plain language."""


# ----------------------------------------------------------------- loading
def load(name: str):
    path = CONTENT / f"{name}.yml"
    try:
        with path.open(encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:
        raise BuildError(
            f"content/{name}.yml could not be read. This usually means a "
            f"missing space after a colon, a tab instead of spaces, or an "
            f"unquoted colon inside text. Details:\n{exc}"
        ) from exc


def slugify(text: str) -> str:
    text = re.sub(r"\(.*?\)", "", text.lower())
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def initials(name: str) -> str:
    name = re.sub(r"\(.*?\)|,.*$", "", name)
    parts = [p for p in name.split() if p[0].isalpha()]
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()


# ------------------------------------------------------------ publications
def split_authors(authors: str) -> list[str]:
    s = authors.replace(", and ", ", ").replace(" and ", ", ").replace(" & ", ", ")
    return [a.strip() for a in s.split(",") if a.strip()]


def highlight_authors(authors: str, names: list[str]) -> Markup:
    out = []
    for a in split_authors(authors):
        plain = a.replace("*", "").strip()
        star = "*" in a
        text = html.escape(plain) + ('<span class="corr" title="Corresponding author">*</span>' if star else "")
        if plain in names:
            text = f'<strong class="lab-author">{text}</strong>'
        out.append(text)
    if len(out) > 1:
        return Markup(", ".join(out[:-1]) + (", and " if len(out) > 2 else " and ") + out[-1])
    return Markup(out[0] if out else "")


def bibtex(p: dict) -> str:
    kind = {"journal": "article", "conference": "inproceedings", "chapter": "incollection"}[p["type"]]
    first = split_authors(p["authors"])[0].replace("*", "").split()[-1]
    key = f"{slugify(first)}{p['year']}{slugify(p['title']).split('-')[0]}"
    authors = " and ".join(a.replace("*", "").strip() for a in split_authors(p["authors"]) if a != "et al.")
    venue_field = {"article": "journal", "inproceedings": "booktitle", "incollection": "booktitle"}[kind]
    fields = [("title", "{" + p["title"] + "}"), ("author", authors), (venue_field, p["venue"]), ("year", str(p["year"]))]
    for f in ("volume", "issue", "pages", "publisher", "doi"):
        if p.get(f):
            fields.append(("number" if f == "issue" else f, str(p[f]).replace("–", "--")))
    if p.get("url") and not p.get("doi"):
        fields.append(("url", p["url"]))
    if p.get("status") == "accepted":
        fields.append(("note", "Accepted"))
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields)
    return f"@{kind}{{{key},\n{body}\n}}"


def prepare_publications(pubs: dict, highlights: list[str]) -> list[dict]:
    items = []
    for section, ptype in (("chapters", "chapter"), ("journals", "journal"), ("conferences", "conference")):
        for p in pubs.get(section) or []:
            for field in ("id", "authors", "title", "venue", "year"):
                if not p.get(field):
                    raise BuildError(f"A publication in '{section}' is missing '{field}': {p}")
            p = dict(p)
            p["type"] = ptype
            p["type_label"] = TYPE_LABELS[ptype]
            p["authors_html"] = highlight_authors(p["authors"], highlights)
            p["link"] = f"https://doi.org/{p['doi']}" if p.get("doi") else p.get("url")
            parts = []
            if p.get("volume"):
                parts.append(f"vol. {p['volume']}" + (f", no. {p['issue']}" if p.get("issue") else ""))
            if p.get("pages"):
                parts.append(("pp. " if "–" in str(p["pages"]) else "") + str(p["pages"]))
            p["details"] = ", ".join(parts)
            p["bibtex"] = bibtex(p)
            p["projects"] = []
            items.append(p)
    ids = [p["id"] for p in items]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise BuildError(f"Publication IDs must be unique. Repeated: {', '.join(sorted(dupes))}")
    return items


# ---------------------------------------------------------------- building
def build(local: bool = False) -> Path:
    site = load("site")
    news = load("news") or []
    people = load("people")
    projects_data = load("projects")
    pubs_data = load("publications")
    teaching = load("teaching")
    outreach = load("outreach")

    site_url = (os.environ.get("SITE_URL") or site.get("url", "")).rstrip("/")
    site["url"] = site_url
    built_at = dt.datetime.now(dt.timezone.utc)

    pubs = prepare_publications(pubs_data, people.get("author_highlights", []))
    pub_by_id = {p["id"]: p for p in pubs}

    projects = projects_data.get("projects") or []
    themes = [a["name"] for a in site.get("research_areas", [])]
    for proj in projects:
        if not proj.get("slug"):
            proj["slug"] = slugify(proj["title"])
        if proj.get("theme") and proj["theme"] not in themes:
            raise BuildError(f"Project '{proj['title']}' has theme '{proj['theme']}', which is not one of: {', '.join(themes)}")
        proj["pubs"] = []
        for pid in proj.get("publications") or []:
            if pid not in pub_by_id:
                raise BuildError(f"Project '{proj['slug']}' lists publication '{pid}', which is not in publications.yml")
            proj["pubs"].append(pub_by_id[pid])
            pub_by_id[pid]["projects"].append({"slug": proj["slug"], "title": proj.get("short_title", proj["title"])})
        proj["pubs"].sort(key=lambda p: (-int(p["year"]), "BJC".index(p["id"][0])))

    for item in news:
        d = item["date"]
        if isinstance(d, str):
            d = dt.date.fromisoformat(d)
        item["date"] = d
        if item.get("pub") and item["pub"] not in pub_by_id:
            raise BuildError(f"A news item links to publication '{item['pub']}', which is not in publications.yml")
    news.sort(key=lambda n: n["date"], reverse=True)

    for ev in outreach.get("events", []):
        y, m = str(ev["date"]).split("-")[:2]
        ev["label"] = dt.date(int(y), int(m), 1).strftime("%B %Y")
        ev["year"] = int(y)

    for group in people.get("groups", []):
        for m in group["members"]:
            m["initials"] = initials(m["name"])
            m["slug"] = slugify(m["name"])
    people["pi"]["initials"] = initials(people["pi"]["name"])

    current_count = sum(len(g["members"]) for g in people.get("groups", [])) + 1
    stats = {
        "publications": len(pubs),
        "journals": sum(p["type"] == "journal" for p in pubs),
        "projects": len(projects),
        "members": current_count,
        "alumni": len(people.get("alumni", [])),
        "outreach": len(outreach.get("events", [])),
    }

    terms = []
    for c in teaching.get("courses", []):
        for t in c["terms"]:
            season, year = t["term"].split()
            terms.append({"term": t["term"], "code": c["code"], "title": c["title"], "institution": c["institution"],
                          "enrollment": t.get("enrollment"), "sort": (int(year), {"Spring": 1, "Summer": 2, "Fall": 3}.get(season, 0))})
    terms.sort(key=lambda t: t["sort"], reverse=True)

    # ---- page definitions: (output path, template, title, description, extra context)
    pages = [
        ("index.html", "index.html", None, site["description"], {}),
        ("research/index.html", "research.html", "Research", "Research projects of the ENABLE Lab in wearable robotics, neuromuscular sensing, FES and personalized control.", {}),
        ("people/index.html", "people.html", "People", "Principal investigator, students and alumni of the ENABLE Lab.", {}),
        ("publications/index.html", "publications.html", "Publications", "Journal articles, conference papers and book chapters from the ENABLE Lab.", {}),
        ("teaching/index.html", "teaching.html", "Teaching", "Courses taught by Dr. Qiang Zhang at The University of Alabama.", {}),
        ("outreach/index.html", "outreach.html", "Education & Outreach", "K-12 outreach, student research and community engagement by the ENABLE Lab.", {}),
        ("news/index.html", "news.html", "News", "News, awards, grants and new papers from the ENABLE Lab.", {}),
        ("join/index.html", "join.html", "Join Us", "Open positions and research opportunities in the ENABLE Lab.", {}),
        ("contact/index.html", "contact.html", "Contact", "How to reach and visit the ENABLE Lab at The University of Alabama.", {}),
        ("404.html", "404.html", "Page not found", "Page not found.", {}),
    ]
    for proj in projects:
        pages.append((f"research/{proj['slug']}/index.html", "project.html", proj.get("short_title", proj["title"]),
                      proj.get("summary", ""), {"project": proj}))

    # ---- output
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)
    (OUT / ".nojekyll").write_text("")

    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=True, undefined=ChainableUndefined,
                      trim_blocks=True, lstrip_blocks=True)
    env.filters["slugify"] = slugify
    env.filters["date_long"] = lambda d: f"{d:%B} {d.day}, {d.year}"
    env.filters["date_short"] = lambda d: f"{d:%b} {d.day}"

    for out_path, template, title, description, extra in pages:
        depth = out_path.count("/")
        root = "../" * depth if depth else "./"
        if out_path == "404.html":
            root = (site_url + "/") if site_url and not local else "./"

        def url(path: str = "", _root=root) -> str:
            if path.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                return path
            if local and (path == "" or path.endswith("/")):
                path += "index.html"
            return _root + path

        def img(src: str, _url=url) -> str:
            """Use a local copy in static/images/ when one exists, else the original URL."""
            if not src:
                return ""
            if src.startswith(("http://", "https://")):
                name = src.rsplit("/", 1)[-1]
                if (STATIC / "images" / name).exists():
                    return _url("images/" + name)
                return src
            return _url(src)

        def abs_img(src: str, _img=img) -> str:
            u = _img(src)
            return u if u.startswith("http") else f"{site_url}/images/{u.rsplit('/', 1)[-1]}"

        canonical_path = "" if out_path == "index.html" else out_path.replace("index.html", "")
        ctx = dict(
            site=site, news=news, people=people, projects=projects, research=projects_data, pubs=pubs,
            pubs_intro=pubs_data.get("intro", ""), teaching=teaching, terms=terms, outreach=outreach, stats=stats,
            page_title=title, page_description=description, current=out_path.split("/")[0].replace(".html", ""),
            url=url, img=img, abs_img=abs_img, canonical=f"{site_url}/{canonical_path}", built=built_at,
            year=built_at.year, pub_by_id=pub_by_id, themes=themes, **extra,
        )
        html_out = env.get_template(template).render(**ctx)
        dest = OUT / out_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_out, encoding="utf-8")

    # ---- sitemap, robots, RSS
    urls = [p[0].replace("index.html", "") for p in pages if p[0] != "404.html"]
    today = built_at.date().isoformat()
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{html.escape(site_url)}/{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
        + "</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n", encoding="utf-8")
    items = []
    for n in news[:30]:
        when = dt.datetime.combine(n["date"], dt.time(12), dt.timezone.utc)
        link = f"{site_url}/news/#{n['date'].isoformat()}"
        items.append(f"  <item><title>{html.escape(n['category'])}: {html.escape(n['text'][:90])}</title>"
                     f"<link>{link}</link><guid isPermaLink=\"false\">{n['date'].isoformat()}-{slugify(n['text'])[:40]}</guid>"
                     f"<pubDate>{format_datetime(when)}</pubDate><description>{html.escape(n['text'])}</description></item>\n")
    (OUT / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
        f"  <title>{html.escape(site['short_name'])} news</title><link>{site_url}/news/</link>\n"
        f"  <description>{html.escape(site['description'])}</description>\n" + "".join(items) + "</channel></rss>\n",
        encoding="utf-8")
    return OUT


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--local", action="store_true", help="link to index.html files so the site works from disk")
    args = ap.parse_args()
    try:
        out = build(local=args.local)
    except BuildError as exc:
        print(f"\nBUILD FAILED\n{exc}\n", file=sys.stderr)
        return 1
    n = sum(1 for _ in out.rglob("*.html"))
    print(f"Built {n} pages into {out.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
