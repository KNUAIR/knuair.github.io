#!/usr/bin/env python3
"""Render student profile links into static HTML; run from any directory."""
import html
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ICONS = {
    "homepage": ('Homepage', '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a19 19 0 0 1 0 18 19 19 0 0 1 0-18Z"/>'),
    "github": ('GitHub', '<path fill="currentColor" stroke="none" d="M12 .75a11.25 11.25 0 0 0-3.56 21.92c.56.1.77-.24.77-.54v-2.1c-3.13.68-3.79-1.33-3.79-1.33-.51-1.3-1.25-1.65-1.25-1.65-1.02-.7.08-.69.08-.69 1.13.08 1.73 1.16 1.73 1.16 1 1.72 2.64 1.22 3.28.93.1-.73.39-1.22.71-1.5-2.5-.28-5.13-1.25-5.13-5.56 0-1.23.44-2.23 1.16-3.02-.12-.28-.5-1.43.11-2.98 0 0 .95-.3 3.1 1.15a10.8 10.8 0 0 1 5.64 0c2.15-1.46 3.1-1.15 3.1-1.15.62 1.55.23 2.7.12 2.98a4.35 4.35 0 0 1 1.15 3.02c0 4.32-2.63 5.28-5.14 5.56.4.35.76 1.03.76 2.08v3.1c0 .3.2.65.77.54A11.25 11.25 0 0 0 12 .75Z"/>'),
    "linkedin": ('LinkedIn', '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7.5 10v7M11 17v-7m0 3a3 3 0 0 1 6 0v4"/><circle cx="7.5" cy="7" r=".65" fill="currentColor" stroke="none"/>'),
}
page = ROOT / 'people/student/index.html'
source = page.read_text()
profiles = json.loads((ROOT / 'data/student-profiles.json').read_text())
seen = set()
for profile in profiles:
    name = profile['name']
    if name in seen:
        raise ValueError(f'Duplicate student: {name}')
    seen.add(name)
    links = []
    for key, (label, icon) in ICONS.items():
        url = profile.get(key, '').strip()
        if not url:
            continue
        parsed = urlparse(url)
        if parsed.scheme not in ('https', 'http') or not parsed.netloc:
            raise ValueError(f'Invalid {key} URL for {name}')
        links.append(f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="{html.escape(name, quote=True)} — {label} (opens in a new tab)" title="{label}"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{icon}</svg></a>')
    heading = f'<h3>{html.escape(name)}</h3>'
    if links:
        heading = f'<div class="person-card__heading">{heading}<div class="person-card__socials">{"".join(links)}</div></div>'
    start, end = f'<!-- profile: {name} -->', f'<!-- /profile: {name} -->'
    pattern = re.escape(start) + '.*?' + re.escape(end)
    source, count = re.subn(pattern, lambda _: start + heading + end, source, flags=re.S)
    if count != 1:
        raise ValueError(f'Expected one profile slot for {name}, found {count}')
page.write_text(source)
print(f'Rendered {len(profiles)} student profile slots.')
