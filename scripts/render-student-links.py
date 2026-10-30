#!/usr/bin/env python3
"""Render student profile links into static HTML; run from any directory."""
import html
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
page = ROOT / 'people/student/index.html'
source = page.read_text()
profiles = json.loads((ROOT / 'data/student-profiles.json').read_text())
seen = set()
for profile in profiles:
    name = profile['name']
    if name in seen:
        raise ValueError(f'Duplicate student: {name}')
    seen.add(name)
    label = html.escape(name)
    url = profile.get('homepage', '').strip()
    if url:
        parsed = urlparse(url)
        if parsed.scheme not in ('https', 'http') or not parsed.netloc:
            raise ValueError(f'Invalid homepage URL for {name}')
        accessible_label = html.escape(f"{name}'s homepage", quote=True)
        label += (
            f'<a class="person-card__homepage" href="{html.escape(url, quote=True)}"'
            f' aria-label="{accessible_label}" title="Homepage">'
            '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"'
            ' fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"'
            ' stroke-linejoin="round" aria-hidden="true" focusable="false">'
            '<circle cx="12" cy="12" r="9"></circle>'
            '<ellipse cx="12" cy="12" rx="4" ry="9"></ellipse>'
            '<path d="M3 12h18"></path></svg></a>'
        )
    heading = f'<h3 class="person-card__name">{label}</h3>'
    start, end = f'<!-- profile: {name} -->', f'<!-- /profile: {name} -->'
    pattern = re.escape(start) + '.*?' + re.escape(end)
    source, count = re.subn(pattern, lambda _: start + heading + end, source, flags=re.S)
    if count != 1:
        raise ValueError(f'Expected one profile slot for {name}, found {count}')
page.write_text(source)
print(f'Rendered {len(profiles)} student profile slots.')
