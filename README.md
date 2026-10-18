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
