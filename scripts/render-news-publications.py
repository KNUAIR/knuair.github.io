#!/usr/bin/env python3
"""Embed compact Publications cards in news HTML, without a browser-side fetch.

Edit publications/index.html, then run this script. News pages declare their
paper IDs in <!-- related-publications: paper-id ... --> slots. Abstracts and
author-explanation paragraphs are omitted from news cards.
"""

import argparse
from pathlib import Path
import re


CARD = re.compile(r'<article\b[^>]*\bid="(paper-[^"]+)"[^>]*>.*?</article>', re.S)
DETAIL = re.compile(r'<p class="publication-card__(?:abstract|note)">.*?</p>', re.S)
SLOT = re.compile(
    r'<!-- related-publications: ([\w -]+) -->.*?<!-- /related-publications -->',
    re.S,
)


def render_pages(root):
    source = (root / "publications/index.html").read_text()
    cards = {}
    for match in CARD.finditer(source):
        paper_id = match[1]
        if paper_id in cards:
            raise ValueError(f"Duplicate publication ID: {paper_id}")
        cards[paper_id] = DETAIL.sub("", match[0])
    if not cards:
        raise ValueError("No publication cards found in publications/index.html")

    def render_slot(match):
        ids = match[1].split()
        if not ids or len(ids) != len(set(ids)):
            raise ValueError(f"Empty or duplicate paper IDs: {ids}")
        missing = set(ids) - cards.keys()
        if missing:
            raise ValueError(f"Unknown publication IDs: {', '.join(sorted(missing))}")
        return (
            f'<!-- related-publications: {" ".join(ids)} -->'
            '<section class="news-publications" aria-labelledby="related-publications-title">'
            '<h2 class="visually-hidden" id="related-publications-title">Related publications</h2>'
            + "".join(cards[paper_id] for paper_id in ids)
            + '</section><!-- /related-publications -->'
        )

    pages = []
    for page in sorted((root / "news").glob("*/index.html")):
        before = page.read_text()
        if "<!-- related-publications:" not in before:
            continue
        if len(SLOT.findall(before)) != 1 or before.count("<!-- related-publications:") != 1:
            raise ValueError(f"Expected one complete publication slot: {page}")
        after = SLOT.sub(render_slot, before)
        prefix = re.search(r'href="([^"]*/assets/)refinements\.css', before)
        if not prefix:
            raise ValueError(f"Cannot locate the site's stylesheet path: {page}")
        asset_root = prefix[1]
        for name in ("publications-sync.css", "news-publications.css"):
            href = asset_root + name
            if f'href="{href}"' not in after:
                if after.count("</head>") != 1:
                    raise ValueError(f"Expected one HTML head: {page}")
                after = after.replace("</head>", f'<link rel="stylesheet" href="{href}"></head>')
        pages.append((page, before, after))
    if not pages:
        raise ValueError("No related-publications slots found in news pages")
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Fail if news cards need regeneration")
    args = parser.parse_args()
    try:
        pages = render_pages(args.root)
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
    changed = [(page, after) for page, before, after in pages if before != after]
    if args.check:
        if changed:
            for page, _ in changed:
                print(f"Out of date: {page.relative_to(args.root)}")
            parser.exit(1, "Run render-news-publications.py to refresh news cards.\n")
        print(f"Verified publication cards on {len(pages)} news pages.")
    else:
        for page, after in changed:
            page.write_text(after)
        print(f"Rendered {len(pages)} news pages; updated {len(changed)} files.")


if __name__ == "__main__":
    main()
