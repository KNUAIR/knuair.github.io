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
        label = f'<a class="person-card__name-link" href="{html.escape(url, quote=True)}">{label}</a>'
    heading = f'<h3>{label}</h3>'
    start, end = f'<!-- profile: {name} -->', f'<!-- /profile: {name} -->'
    pattern = re.escape(start) + '.*?' + re.escape(end)
    source, count = re.subn(pattern, lambda _: start + heading + end, source, flags=re.S)
    if count != 1:
        raise ValueError(f'Expected one profile slot for {name}, found {count}')
page.write_text(source)
print(f'Rendered {len(profiles)} student profile slots.')
