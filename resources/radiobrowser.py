# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-
#
# dial411 - talks to the Radio Browser database
#
# Coded by avid (aka avidus/avidus7) & Calix
# https://github.com/avidus7/dial411
#
# Licence: GPL-3.0-or-later. No warranty. See main.py for the full notice.
#
# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-

import json
import random
import time
import urllib.parse
import urllib.request

AGENT = 'dial411/0.1'
FALLBACK = 'de1.api.radio-browser.info'
TIMEOUT = 10

_server = None

def _fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode('utf-8'))

def server():
    # Radio Browser asks that we spread load rather than hammer one machine.
    global _server
    if _server:
        return _server
    try:
        names = {entry['name'] for entry in _fetch('https://all.api.radio-browser.info/json/servers')}
        _server = random.choice(sorted(names)) if names else FALLBACK
    except Exception:
        _server = FALLBACK
    return _server

def _api(path, params=None, tries=3):
    # The service sometimes hands back an empty answer or drops a request.
    # One bad reply should not become "nothing found", so try again, and
    # switch to a different server if this one keeps being unhelpful.
    global _server
    query = '?' + urllib.parse.urlencode(params) if params else ''
    for attempt in range(tries):
        try:
            result = _fetch('https://{0}/json/{1}{2}'.format(server(), path, query))
            if result:
                return result
        except Exception:
            pass
        _server = None          # pick a different server next time round
        time.sleep(0.5)
    return []

def search(name, limit=30):
    return _api('stations/search', {
        'name': name, 'limit': limit, 'order': 'votes',
        'reverse': 'true', 'hidebroken': 'true',
    })

def by_tag(tag, limit=50):
    return _api('stations/search', {
        'tag': tag, 'limit': limit, 'order': 'votes',
        'reverse': 'true', 'hidebroken': 'true',
    })

def by_country(code, limit=100):
    return _api('stations/search', {
        'countrycode': code, 'limit': limit, 'order': 'votes',
        'reverse': 'true', 'hidebroken': 'true',
    })

def tags(limit=60):
    found = _api('tags', {'order': 'stationcount', 'reverse': 'true', 'limit': limit})
    return [tag for tag in found if tag.get('stationcount', 0) >= 20]

def countries():
    return _api('countrycodes', {'order': 'stationcount', 'reverse': 'true'})

def clicked(uuid):
    # Tells Radio Browser a station was actually used. Keeps their rankings honest.
    _api('url/' + uuid)
