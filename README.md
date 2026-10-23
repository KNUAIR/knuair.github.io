# AIR Lab website

Public website for AIR Lab at Kyungpook National University.

- Website: https://knuair.github.io/
- Hosting: GitHub Pages, `main` branch, repository root.
- Format: static HTML, CSS, JavaScript and images; `.nojekyll` disables Jekyll processing.

## Editing

Edit the HTML page and its referenced assets, then commit to `main`. GitHub Pages publishes the change automatically. Use your own GitHub account and a commit email linked to that account.

The current files are the static export of the existing lab website. The original Astro source project is not part of this repository. Reusable navigation appears in each HTML page, including the serialized `MobileNavigation` component props; update both when changing the menu.

## Local preview

```sh
python3 -m http.server 4177 --bind 127.0.0.1
```

Open http://127.0.0.1:4177/ in a browser. Root-relative asset paths need an HTTP server rather than opening HTML directly as a file.

## Published content

This repository includes only the public lab pages and the assets they use. Disabled Research/Projects pages, the former gallery posts and unused placeholder images were not imported. The personal portfolio, CV files and its Git history were not imported. GradOrient links to its existing project website at https://givingdragon.github.io/GradOrient/.

The Collaborators page is temporarily disabled and is absent from navigation, the sitemap and the published files. Its previous version remains in Git history. Student entries show names and membership dates without placeholder initials.

To add or remove a page, update the navigation and `sitemap-0.xml` as appropriate. Keep unreleased content outside this public repository rather than hiding it with CSS.

Gallery is open at `/gallery/` with the placeholder “Photos coming soon.” and no posts. Its link is included in both desktop and mobile navigation.

## Student profile links

Edit `data/student-profiles.json` to add each student's `homepage` URL. Leave unknown URLs empty; those names remain plain text. Then run:

```sh
python3 scripts/render-student-links.py
```

Commit the JSON and generated `people/student/index.html` together. The student's name links directly to their homepage in the same tab, without social icons or JavaScript. To add a new student, add their card with `<!-- profile: Full Name -->` and `<!-- /profile: Full Name -->` markers around its heading, plus a matching JSON entry.

## Shared publication cards

`data/publications.json` is the single source for Publications and News: one object per paper, identified by a stable `paper-...` ID. Each object holds its title, authors (including existing emphasis and contribution markers), venue, topics, and Paper/Code/Project resources. Keep unavailable resources empty.

`render_card()` in `scripts/render-publications.py` generates identical HTML for both pages. The card contains no extra summary or author-explanation paragraphs. Edit the JSON, then run:

```sh
python3 scripts/render-publications.py
python3 scripts/render-publications.py --check
```

Commit the JSON and generated HTML together. The renderer updates the Publications list, counts, year filters, and every related news card in one run. `--check` fails if either page is out of date. Generated cards work without JavaScript. The older `render-news-publications.py` command delegates to this renderer.

News text remains authored in each news page. Only the card slot is generated. To reference one or more publication objects below the news body, use their IDs separated by spaces:

```html
<!-- related-publications: paper-compsplat --><!-- /related-publications -->
```

Do not edit generated cards in `publications/index.html` or inside news slots; edit the object or the shared card renderer. General announcements have no slot.

Publication cards use `lab_member: true` to display AIR Lab authors in bold. Only `*` for equal contribution is shown; cards have no corresponding-author symbol, underlines, or author-style legend.
