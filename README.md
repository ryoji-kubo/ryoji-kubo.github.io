# Ryoji Kubo’s academic website

A small academic homepage for `ryoji-kubo.github.io`. Plain HTML and
CSS, system fonts, no JavaScript, no package installation, and no build step.

## Preview locally

From this repository, run:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory site
```

Open <http://127.0.0.1:8000>. Refresh after editing; stop the server with `Ctrl+C`.
Use the local server so browsers can load the shared SVG icons. Python is only a
development tool; the published website has no runtime dependencies.

## Edit the site

| Task | File |
| --- | --- |
| Edit your bio, research, papers, news, awards, teaching, service, or profile links | [`site/index.html`](site/index.html) |
| Edit powerlifting, the places map, or other personal notes | [`site/personal.html`](site/personal.html) |
| Adjust typography, colors, or spacing | [`site/styles.css`](site/styles.css) |
| Add a portrait, CV, or paper PDF | `site/assets/` |

Profile icons appear beneath the name and affiliation. Publications include
short summaries and venue/preprint labels. News, Awards, Teaching, and
Professional service use dated lists. A separate Personal page contains the
powerlifting note, OpenIPF link, and a world map of places lived for six months
or more. Singapore is marked as the current home.

## Check changes

```sh
python3 scripts/check_site.py
git diff --check
```

The offline check catches broken local HTML links, missing assets, duplicate IDs,
and basic document omissions. It does not validate external URLs or replace a
browser review. Check the page on desktop and mobile, with keyboard navigation,
and at 200% zoom after layout changes.

## Publish on GitHub Pages

1. In the repository’s **Settings → Pages → Build and deployment**, select
   **GitHub Actions** as the source. The workflow is already included; skip the
   suggested templates.
2. Run the checks above, then commit and push from the repository root:

   ```sh
   git add site/ .github/workflows/pages.yml scripts/ README.md .gitignore .editorconfig
   git diff --cached --stat
   git commit -m "Publish academic website"
   git push origin main
   ```

3. Open **Actions → Check and deploy website** and wait for the deployment to
   succeed. Visit <https://ryoji-kubo.github.io/>. If Pages was enabled after the
   push, use **Run workflow** on `main` to start it again.

Later pushes to `main` publish updates automatically. Pull requests run the
checks without deploying. To undo a published change, revert its commit and push
the revert.

Expected address: <https://ryoji-kubo.github.io/>. The repository name must match
your GitHub username. Only `site/` is deployed. The source repository also
contains the publishing workflow, maintenance scripts, README, and editor/Git configuration.
All committed files are visible if the repository is public.

The root `.gitignore` allows only these website and maintenance paths; other
root files and folders stay local. New assets within `site/` are included
automatically. To intentionally share a new top-level path, add an exception to
`.gitignore` first.

These steps follow [GitHub’s Pages setup instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Icons

The four profile icons are from [Bootstrap Icons](https://icons.getbootstrap.com/),
stored locally as SVG symbols. Their MIT license is included in
[`site/assets/profile-icons-LICENSE.txt`](site/assets/profile-icons-LICENSE.txt).

## Places map

The map is a local SVG in the same colors and fonts as the page. It works without
JavaScript, map services, or API keys. City dots and their numbered labels live in
`site/personal.html`, followed by a text list of the same places. The numbers are
identifiers, not a timeline. The ring and “Current home” label identify Singapore.
Use city and country names, spelling out countries and omitting states or
prefectures. Singapore appears once, with “Current home” beneath it.

The land outline uses [Natural Earth’s public-domain data](https://www.naturalearthdata.com/about/terms-of-use/)
with an Equal Earth projection. To regenerate the outline, download
[`ne_110m_land.geojson`](https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson)
and run `python3 scripts/build_map.py /path/to/ne_110m_land.geojson`. This is only
needed when replacing the outline; normal editing and publishing need no build.

For a new city, use `project(longitude, latitude)` from `scripts/build_map.py` to
calculate its position in the map’s `1000 × 500` viewBox. Add a `.map-place` group
and a matching `.places-list` item. Keep dots at their projected positions and
offset only the leader lines and number labels. End each line at the center of
its number circle and draw the opaque circle over it, keeping the connection
intact as the circle grows on mobile. Check nearby markers at mobile widths.
To change the current home, move `.map-place--current`, the ring, and
`.place-current` to the new city and update the surrounding text.
