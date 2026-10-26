# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-
#
# dial411 - finding artwork on a station's own website
#
# Coded by avid (aka avidus/avidus7) & Calix
# https://github.com/avidus7/dial411
#
# Licence: GPL-3.0-or-later. No warranty. See main.py for the full notice.
#
# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-

import re
import urllib.parse
import urllib.request

AGENT = 'dial411/0.1'
TIMEOUT = 12
MAX_PAGE = 400000          # no need to read a whole site, the tags are near the top

def _page(url):
    request = urllib.request.Request(url, headers={'User-Agent': AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read(MAX_PAGE).decode('utf-8', 'ignore')

def find(homepage):
    # Websites declare their own artwork in standard tags. We read those
    # rather than guessing at page layout, which breaks on every redesign.
    if not homepage:
        return []
    if not homepage.startswith('http'):
        homepage = 'http://' + homepage
    try:
        html = _page(homepage)
    except Exception:
        return []

    wanted = [
        # (what to look for, how to describe it, roughly how good it usually is)
        (r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', 'sharing image', 3),
        (r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)', 'sharing image', 3),
        (r'<link[^>]+rel=["\']apple-touch-icon[^"\']*["\'][^>]+href=["\']([^"\']+)', 'touch icon', 2),
        (r'<link[^>]+rel=["\'][^"\']*icon[^"\']*["\'][^>]+href=["\']([^"\']+)', 'site icon', 1),
    ]

    found, seen = [], set()
    for pattern, label, quality in wanted:
        for match in re.finditer(pattern, html, re.I):
            link = urllib.parse.urljoin(homepage, match.group(1).strip())
            if link in seen or link.lower().endswith('.svg'):
                continue       # Kodi cannot display SVG artwork
            seen.add(link)
            found.append({'url': link, 'label': label, 'quality': quality})

    found.sort(key=lambda item: item['quality'], reverse=True)

    # The same picture often appears under several tags - keep the best label only.
    best, picked = [], set()
    for item in found:
        if item['url'] in picked:
            continue
        picked.add(item['url'])
        best.append(item)
    return best[:4]
