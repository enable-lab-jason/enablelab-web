# Put the ENABLE Lab website on GitHub and get its URL

You need about 20 minutes, a web browser and the file `enablelab-website.zip`. You don't need to install anything for Option A.

When you finish, the site will be live at:

```
https://YOUR-GITHUB-USERNAME.github.io/enablelab-website/
```

---

## Step 1. Create a GitHub account

If you don't have one, sign up at https://github.com/signup. Your username becomes part of the URL, so choose something professional, such as `qzhang-ua`.

*Optional:* create a free **organization** for the lab (your profile picture > **Your organizations** > **New organization** > Free), named for example `enable-lab-ua`. The site address then becomes `https://enable-lab-ua.github.io/enablelab-website/`, and students can be added as members without sharing your account.

## Step 2. Create an empty repository

1. Click **+** (top right) > **New repository**.
2. **Owner:** your account or the lab organization.
3. **Repository name:** `enablelab-website`
4. **Visibility: Public.** GitHub Pages is free for public repositories; private ones need a paid plan.
5. Leave "Add a README", ".gitignore" and "license" **unchecked**.
6. Click **Create repository**.

## Step 3. Upload the files

Unzip `enablelab-website.zip` on your computer. You'll get a folder called `enablelab-website`.

### Option A: in the browser (no software)

1. On your new repository page, click the link **uploading an existing file**.
2. Open the unzipped `enablelab-website` folder, select **everything inside it** (not the folder itself) and drag it onto the GitHub page.
   - **On a Mac:** the folder `.github` is hidden. In Finder, press **Cmd + Shift + .** (period) to show hidden files before selecting everything.
   - **On Windows:** `.github` is visible normally.
3. Wait until all files are listed, type a message such as `First version of the new website`, and click **Commit changes**.
4. Check that the repository now shows the folders `.github`, `content`, `scripts`, `static` and `templates`, plus `build.py`. **If `.github` is missing**, the site won't build; see "Missing .github folder" in Troubleshooting below.

### Option B: GitHub Desktop (recommended if you'll edit often)

1. Install GitHub Desktop from https://desktop.github.com and sign in.
2. **File > Clone repository** > choose `enablelab-website` > Clone.
3. Copy everything from the unzipped folder, hidden `.github` included, into the cloned folder.
4. In GitHub Desktop, type a summary, then click **Commit to main** and **Push origin**.

### Option C: command line

```bash
cd enablelab-website
git init -b main
git add .
git commit -m "First version of the new website"
git remote add origin https://github.com/YOUR-USERNAME/enablelab-website.git
git push -u origin main
```

## Step 4. Turn on GitHub Pages

1. In the repository, open **Settings** > **Pages** (left sidebar).
2. Under **Build and deployment** > **Source**, choose **GitHub Actions**.

That's the only setting needed. Don't choose "Deploy from a branch".

## Step 5. Build the site and get the URL

1. Open the **Actions** tab.
2. Click **Build and deploy website** in the left list, then click **Run workflow** > **Run workflow**. (Your upload may already have started a run. If it failed because Pages wasn't on yet, just run it again.)
3. Wait 1–2 minutes for a green check mark.
4. Click the finished run. The **deploy** box shows your site's link. It's also shown under **Settings > Pages**: "Your site is live at …"

**Your URL:** `https://YOUR-USERNAME.github.io/enablelab-website/`

## Step 6. Copy the images into the repository (once)

The new site first displays photos straight from the old sites.ua.edu site. To keep its own copies:

1. **Actions** > **Import images from old site** > **Run workflow**.
2. When it finishes, run **Build and deploy website** once more (Step 5).

The site now uses its own copies and keeps working if the old site is removed.

## Step 7. Edit content from now on

All text lives in the `content/` folder:

| To change… | Edit this file |
|---|---|
| News items | `content/news.yml` (add new items at the top) |
| Members, alumni, headshots | `content/people.yml` |
| Papers | `content/publications.yml` |
| Projects, descriptions, figures | `content/projects.yml` |
| Courses | `content/teaching.yml` |
| Outreach events | `content/outreach.yml` |
| Mission, contact, funders, open positions | `content/site.yml` |

**To edit in the browser:** open the file on GitHub, click the **pencil icon**, make the change, and click **Commit changes**. The site updates by itself in about 2 minutes.

**To add a photo:** open `static/images/`, choose **Add file > Upload files**, upload `jane-doe.jpg`, then write `photo: images/jane-doe.jpg` in `people.yml`.

**Formatting rules for the .yml files:**
- Use spaces, not tabs, and keep the same indentation as the lines around your edit.
- Put text in "quotes" if it contains a colon (`:`).
- If you make a mistake, the build stops with a plain-English message on the Actions tab, and the live site stays as it was. Fix the file and commit again.

## Step 8 (optional). Use a UA web address

To serve the site at an address like `enablelab.ua.edu`:

1. Ask UA OIT to create a **CNAME** DNS record pointing `enablelab.ua.edu` to `YOUR-USERNAME.github.io`.
2. In **Settings > Pages > Custom domain**, enter `enablelab.ua.edu`, click **Save**, and tick **Enforce HTTPS** once it's available.
3. Run **Build and deploy website** again. Links, the sitemap and the feed switch to the new address automatically.

Also, update the old sites.ua.edu site: add a notice linking to the new address, or ask the site administrator to set up a redirect.

## Troubleshooting

| Problem | Fix |
|---|---|
| **Missing .github folder** after a browser upload | On the repository page, click **Add file > Create new file**. Type the name `.github/workflows/deploy.yml` (the slashes create folders), paste the contents of that file from the unzipped folder, and commit. Repeat for `.github/workflows/import-images.yml`. |
| Actions tab says workflows are disabled | Click **I understand my workflows, go ahead and enable them**. |
| Build fails at "Look up the site address" | Pages isn't set to **GitHub Actions** yet (Step 4). Set it, then run the workflow again. |
| Build fails at "Build the site" | Open the failed step. The message names the file and the problem (for example a missing space after a colon). |
| Image import fails with a permission error | **Settings > Actions > General > Workflow permissions**: choose **Read and write permissions**, save, and run it again. |
| Page shows the old version | Wait 2 minutes and refresh with Ctrl + F5 (Cmd + Shift + R on a Mac). |
| 404 at the URL | Make sure the link ends in `/enablelab-website/` and the last deploy run is green. |

## Preview on your own computer (optional)

With Python 3 installed:

```bash
pip install -r requirements.txt
python build.py --local
```

Then open `_site/index.html` in your browser.
