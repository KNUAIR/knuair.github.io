#!/usr/bin/env python3
"""Render Publications and News from the same publication objects and card function."""

import argparse
import html
import json
from pathlib import Path
import re
from urllib.parse import urlparse


CATEGORIES = {
    "international-conference": "International Conference",
    "international-journal": "International Journal",
}
GROUPS = {"lab": "AIR Lab", "prior": "Earlier work"}
ARCHIVE_SLOT = re.compile(r"<!-- publications -->.*?<!-- /publications -->", re.S)
NEWS_SLOT = re.compile(
    r"<!-- related-publications: ([\w -]+) -->.*?<!-- /related-publications -->", re.S
)


def load_publications(root):
    records = json.loads((root / "data/publications.json").read_text())
    if not isinstance(records, list) or not records:
        raise ValueError("publications.json must contain a nonempty array")
    seen = set()
    for paper in records:
        paper_id = paper["id"]
        if not re.fullmatch(r"paper-[a-z0-9]+(?:-[a-z0-9]+)*", paper_id) or paper_id in seen:
            raise ValueError(f"Invalid or duplicate publication ID: {paper_id}")
        seen.add(paper_id)
        if paper["type"] not in CATEGORIES or paper["group"] not in GROUPS:
            raise ValueError(f"Unknown publication type or group: {paper_id}")
        if type(paper["year"]) is not int:
            raise ValueError(f"Publication year must be an integer: {paper_id}")
        for field in ("code", "title", "venue"):
            if not isinstance(paper[field], str) or not paper[field].strip():
                raise ValueError(f"Missing {field}: {paper_id}")
        if not paper["authors"]:
            raise ValueError(f"Missing authors: {paper_id}")
        for author in paper["authors"]:
            if not isinstance(author["name"], str) or not author["name"].strip():
                raise ValueError(f"Missing author name: {paper_id}")
            for flag in ("lab_member", "equal_contribution"):
                if flag in author and type(author[flag]) is not bool:
                    raise ValueError(f"Author {flag} must be boolean: {paper_id}")
        for field in ("topics", "search_aliases"):
            values = paper.get(field, [])
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                raise ValueError(f"{field} must be an array of strings: {paper_id}")
        for resource in paper["resources"]:
            url = resource["url"]
            if resource["label"] not in {"Paper", "Code", "Project"}:
                raise ValueError(f"Unknown resource label: {paper_id}")
            if not isinstance(url, str):
                raise ValueError(f"Resource URL must be text: {paper_id}")
            parsed = urlparse(url)
            if url and (parsed.scheme not in {"https", "http"} or not parsed.netloc):
                raise ValueError(f"Invalid resource URL: {paper_id}: {url}")
            if "new_tab" in resource and type(resource["new_tab"]) is not bool:
                raise ValueError(f"Resource new_tab must be boolean: {paper_id}")
    return records


def render_author(author):
    name = html.escape(author["name"])
    if author.get("equal_contribution"):
        name += '<sup title="Equal contribution" aria-label="Equal contribution">*</sup>'
    return f"<strong>{name}</strong>" if author.get("lab_member") else name


def render_card(paper):
    """The exact same HTML is used by the publication archive and news slots."""
    escape = html.escape
    category = CATEGORIES[paper["type"]]
    searchable = " ".join(
        [paper["id"].removeprefix("paper-"), paper["code"], paper["title"],
         paper["venue"], category, str(paper["year"])]
        + [author["name"] for author in paper["authors"]]
        + paper.get("topics", []) + paper.get("search_aliases", [])
    ).lower()
    result = (
        f'<article id="{paper["id"]}" class="publication-card publication-card--row publication-card--text"'
        f' data-publication-item data-search="{escape(searchable)}" data-year="{paper["year"]}"'
        f' data-type="{paper["type"]}" data-era="{paper["group"]}">'
        '<div class="publication-card__content"><div class="publication-card__meta">'
        f'<span>[{escape(paper["code"])}] {category}</span><span>{paper["year"]}</span></div>'
        f'<h3>{escape(paper["title"])}</h3>'
        '<p class="publication-card__authors">'
        + " · ".join(render_author(author) for author in paper["authors"])
        + f'</p><p class="publication-card__venue">{escape(paper["venue"])}</p>'
    )
    if paper.get("topics"):
        result += f'<p class="publication-card__topic">{escape(" · ".join(paper["topics"]))}</p>'
    links = []
    for resource in paper["resources"]:
        if not resource["url"]:
            continue
        attributes = ' target="_blank" rel="noopener noreferrer"' if resource.get("new_tab", True) else ""
        links.append(
            f'<a href="{escape(resource["url"])}"{attributes}>{resource["label"]} '
            '<span aria-hidden="true">↗</span></a>'
        )
    if links:
        result += '<div class="publication-card__resources" aria-label="Publication resources">' + "".join(links) + "</div>"
    return result + "</div></article>"


def update_filters(source, records):
    island = re.search(
        r'<astro-island\b[^>]*component-url="[^"]*PublicationFilters[^>]*>.*?</astro-island>',
        source, re.S,
    )
    if not island:
        raise ValueError("Missing Publications filter component")
    component = island[0]
    props_match = re.search(r'props="([^"]*)"', component)
    props = json.loads(html.unescape(props_match[1]))
    years = sorted({paper["year"] for paper in records}, reverse=True)
    props["years"] = [1, [[0, year] for year in years]]
    props["total"] = [0, len(records)]
    encoded = html.escape(json.dumps(props, ensure_ascii=False, separators=(",", ":")))
    component = component[:props_match.start(1)] + encoded + component[props_match.end(1):]
    year_id = re.search(r'<label for="([^"]+)">Year</label>', component)[1]
    options = '<option value="all" selected="">All years</option>' + "".join(
        f'<option value="{year}">{year}</option>' for year in years
    )
    component, count = re.subn(
        r'(<select\b[^>]*id="' + re.escape(year_id) + r'"[^>]*>).*?(</select>)',
        lambda match: match[1] + options + match[2], component, flags=re.S,
    )
    if count != 1:
        raise ValueError("Missing Publications year filter")
    component, count = re.subn(
        r'<p aria-live="polite">.*?</p>',
        f'<p aria-live="polite">{len(records)}<!-- --> <!-- -->publications</p>',
        component, flags=re.S,
    )
    if count != 1:
        raise ValueError("Missing Publications result count")
    return source[:island.start()] + component + source[island.end():]


def render_pages(root):
    records = load_publications(root)
    cards = {paper["id"]: render_card(paper) for paper in records}
    archive = root / "publications/index.html"
    before = archive.read_text()
    if len(ARCHIVE_SLOT.findall(before)) != 1:
        raise ValueError("Expected one complete Publications slot")
    groups = []
    for group, title in GROUPS.items():
        papers = [paper for paper in records if paper["group"] == group]
        if not papers:
            continue
        groups.append(
            f'<section class="collection-group" aria-labelledby="{group}-publications-title" data-publication-group>'
            f'<header class="collection-group__header"><h2 id="{group}-publications-title">{title}</h2>'
            f'<p data-publication-group-count>{len(papers):02d}</p></header>'
            '<div class="publication-list publication-list--text">'
            + "".join(cards[paper["id"]] for paper in papers) + "</div></section>"
        )
    after = ARCHIVE_SLOT.sub(lambda _: "<!-- publications -->" + "".join(groups) + "<!-- /publications -->", before)
    pages = [(archive, before, update_filters(after, records))]

    def news_slot(match):
        ids = match[1].split()
        if not ids or len(ids) != len(set(ids)):
            raise ValueError(f"Empty or duplicate news publication IDs: {ids}")
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

    for page in sorted((root / "news").glob("*/index.html")):
        before = page.read_text()
        if "<!-- related-publications:" not in before:
            continue
        if len(NEWS_SLOT.findall(before)) != 1 or before.count("<!-- related-publications:") != 1:
            raise ValueError(f"Expected one complete publication slot: {page}")
        after = NEWS_SLOT.sub(news_slot, before)
        asset_root = re.search(r'href="([^"]*/assets/)refinements\.css', before)
        if not asset_root:
            raise ValueError(f"Cannot locate stylesheet path: {page}")
        for name in ("publications-sync.css", "news-publications.css"):
            href = asset_root[1] + name
            if f'href="{href}"' not in after:
                if after.count("</head>") != 1:
                    raise ValueError(f"Expected one HTML head: {page}")
                after = after.replace("</head>", f'<link rel="stylesheet" href="{href}"></head>')
        pages.append((page, before, after))
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="Fail when either page needs regeneration")
    args = parser.parse_args()
    try:
        pages = render_pages(args.root)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"{error}\n")
    changed = [(page, after) for page, before, after in pages if before != after]
    if args.check:
        if changed:
            for page, _ in changed:
                print(f"Out of date: {page.relative_to(args.root)}")
            parser.exit(1, "Run render-publications.py to update Publications and News together.\n")
        print(f"Verified shared publication cards on {len(pages)} pages.")
    else:
        for page, after in changed:
            page.write_text(after)
        print(f"Rendered {len(pages)} pages from publication objects; updated {len(changed)} files.")


if __name__ == "__main__":
    main()
