# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-
#
# dial411 - matching your own stations against the database
#
# Coded by avid (aka avidus/avidus7) & Calix
# https://github.com/avidus7/dial411
#
# Licence: GPL-3.0-or-later. No warranty. See main.py for the full notice.
#
# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-

import re
import radiobrowser as rb

_cache = {}

def tidy(text):
    # Strip the frequency and city people put in station names, so
    # "CFNY 102.1 The Edge" still matches "The Edge".
    text = (text or '').lower()
    text = re.sub(r'\b\d+[.,]?\d*\s*(fm|am|mhz|khz)?\b', ' ', text)
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    return ' '.join(text.split())

def score(mine, theirs):
    # How confident are we that these are the same station?
    my_url = (mine.get('url') or '').rstrip('/')
    their_url = (theirs.get('url_resolved') or theirs.get('url') or '').rstrip('/')
    if my_url and my_url == their_url:
        return 100                      # same stream address - certain

    my_name = tidy(mine.get('name'))
    their_name = tidy(theirs.get('name'))
    if not my_name or not their_name:
        return 0
    if my_name == their_name:
        return 90

    my_words = set(my_name.split())
    their_words = set(their_name.split())
    if not my_words or not their_words:
        return 0
    shared = my_words & their_words
    if not shared:
        return 0
    overlap = len(shared) / float(min(len(my_words), len(their_words)))
    return int(overlap * 80)

def drop_callsign(name):
    # Canadian and US stations are often listed without their call sign,
    # so "CFNY 102.1 The Edge" needs to also look for "The Edge".
    words = tidy(name).split()
    if words and re.match(r'^[cwk][a-z]{2,4}$', words[0]):
        return ' '.join(words[1:])
    return ''

def dedupe(stations):
    # The database holds the same station submitted more than once.
    seen, out = set(), []
    for s in stations:
        key = ((s.get('name') or '').strip().lower(),
               (s.get('url_resolved') or s.get('url') or '').rstrip('/'))
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out

def matches(station, limit=5):
    # Try the full name, then the tidied name, and pool what comes back.
    key = (station.get('name') or '') + '|' + (station.get('url') or '')
    if key in _cache:
        return _cache[key][:limit]

    found, seen = [], set()
    tried = set()
    for query in (station.get('name'), tidy(station.get('name')),
                  drop_callsign(station.get('name'))):
        if not query or query in tried:
            continue
        tried.add(query)
        for s in rb.search(query, 30):
            uuid = s.get('stationuuid')
            if uuid and uuid not in seen:
                seen.add(uuid)
                found.append(s)
        # A certain or near-certain hit means the other searches are wasted trips.
        if any(score(station, s) >= 90 for s in found):
            break
    found = dedupe(found)
    scored = [(score(station, s), s) for s in found]
    scored = [(n, s) for n, s in scored if n >= 40]
    scored.sort(key=lambda pair: (pair[0], pair[1].get('votes', 0)), reverse=True)
    _cache[key] = [pair for pair in scored]
    return scored[:limit]

def gaps(mine, theirs):
    # What could this match actually improve? Never overwrite artwork the user picked.
    out = []
    if not mine.get('logo') and theirs.get('favicon'):
        out.append(('artwork', 'Artwork', theirs.get('favicon')))
    if theirs.get('tags'):
        out.append(('genre', 'Genre', theirs.get('tags')))
    if theirs.get('country'):
        out.append(('country', 'Country', theirs.get('country')))
    if theirs.get('bitrate'):
        out.append(('quality', 'Quality', '{0} {1}k'.format(
            theirs.get('codec') or '?', theirs.get('bitrate'))))
    if theirs.get('homepage'):
        out.append(('website', 'Website', theirs.get('homepage')))
    return out
