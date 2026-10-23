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

## Publication cards in news

Publication news displays the same cards as `publications/index.html` directly below the announcement. That page is the source for titles, authors, venues, and available Paper/Code/Project links. News cards are generated into static HTML and work without JavaScript.

After editing publication metadata, run:

```sh
python3 scripts/render-news-publications.py
python3 scripts/render-news-publications.py --check
```

Commit the publication page and generated news HTML together. `--check` fails when cards need updating. To associate a news item with one or more papers, put a slot after its `news-detail__body`, using the publication cards' IDs separated by spaces:

```html
<!-- related-publications: paper-compsplat --><!-- /related-publications -->
```

The renderer fills the slot and adds the shared publication styles plus `assets/news-publications.css`. Do not edit generated cards inside the slot. General announcements have no slot.
