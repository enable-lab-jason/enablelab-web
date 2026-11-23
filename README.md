# ENABLE Lab website

Source for the website of the **Enhanced NeuroRobotics Autonomy and Biomechanical Engineering (ENABLE) Lab**, Department of Mechanical Engineering, The University of Alabama.

The site is generated from plain-text files in `content/` and published automatically with GitHub Pages whenever a change is committed to `main`.

- **First-time setup and getting the URL:** see [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Why it is built this way:** see [DECISIONS.md](DECISIONS.md)

## Editing content

| To change… | Edit |
|---|---|
| News | `content/news.yml` |
| People and alumni | `content/people.yml` |
| Publications | `content/publications.yml` |
| Research projects | `content/projects.yml` |
| Teaching | `content/teaching.yml` |
| Outreach | `content/outreach.yml` |
| Mission, contact, funders, Join us | `content/site.yml` |
| Photos | upload to `static/images/` |

Edit a file on GitHub (pencil icon), then commit. The **Build and deploy website** workflow rebuilds the site, checks for broken links and missing alt text, and publishes it in about two minutes. If a content file has a mistake, the build stops with a plain-language message and the live site is not changed.

## Folder map

```
content/      text and data for every page (edit these)
templates/    page layouts (HTML with Jinja2)
static/       CSS, JavaScript, favicon and images
scripts/      link checker and image importer
build.py      turns content + templates into the website (_site/)
.github/      GitHub Actions workflows (build/deploy, image import)
```

## Building locally (optional)

```bash
pip install -r requirements.txt
python build.py --local      # then open _site/index.html
python scripts/check_links.py
```

## Maintenance checklist

- **Each semester:** update `people.yml` (move graduates to `alumni` with years and positions) and the Join us positions in `site.yml`.
- **Each new paper:** add it to `publications.yml` and list its ID under the matching project in `projects.yml`.
- **Each event or award:** add it to `news.yml` and, for outreach, `outreach.yml`, with photo alt text describing who and what is shown.
