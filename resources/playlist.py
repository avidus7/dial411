# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-
#
# dial411 - reads and writes the radio playlist
#
# Coded by avid (aka avidus/avidus7) & Calix
# https://github.com/avidus7/dial411
#
# Licence: GPL-3.0-or-later. No warranty. See main.py for the full notice.
#
# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-

import os
import re
import shutil
import time
import urllib.request

AGENT = 'dial411/0.1'

def backup(path):
    stamp = time.strftime('%Y%m%d-%H%M%S')
    target = '{0}.bak-{1}'.format(path, stamp)
    shutil.copy2(path, target)
    return target

def read(path):
    stations = []
    with open(path, 'r', encoding='utf-8') as handle:
        lines = handle.read().splitlines()
    for n, line in enumerate(lines):
        if not line.startswith('#EXTINF'):
            continue
        url = ''
        for following in lines[n + 1:]:
            if following.strip() and not following.startswith('#'):
                url = following.strip()
                break
        def grab(key):
            found = re.search(key + r'="([^"]*)"', line)
            return found.group(1) if found else ''
        stations.append({
            'name': line.rsplit(',', 1)[-1].strip(),
            'id': grab('tvg-id'),
            'logo': grab('tvg-logo'),
            'group': grab('group-title'),
            'url': url,
        })
    return stations

def groups(path):
    seen = []
    for station in read(path):
        if station['group'] and station['group'] not in seen:
            seen.append(station['group'])
    return seen

def already_there(path, url, name):
    for station in read(path):
        if url and station['url'] == url:
            return station['name']
        if name and station['name'].lower() == name.lower():
            return station['name']
    return None

def make_id(name, taken):
    # Kodi matches EPG data on tvg-id, so it has to be unique and plain.
    base = re.sub(r'[^A-Za-z0-9]', '', name) or 'Station'
    candidate = base
    suffix = 2
    while candidate in taken:
        candidate = '{0}{1}'.format(base, suffix)
        suffix += 1
    return candidate

def save_logo(url, station_id, folder):
    # Always keep artwork local - websites redesign and links die.
    if not url:
        return ''
    extension = os.path.splitext(url.split('?')[0])[1].lower()
    if extension not in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico'):
        extension = '.png'
    target = os.path.join(folder, station_id + extension)
    request = urllib.request.Request(url, headers={'User-Agent': AGENT})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = response.read()
    except Exception:
        return ''
    if len(data) < 100:
        return ''
    # Check it is really an image and not a website saying "not found".
    if not (data[:4] == b'\x89PNG' or data[:3] == b'\xff\xd8\xff'
            or data[:6] in (b'GIF87a', b'GIF89a') or data[:4] == b'RIFF'
            or data[:4] == b'\x00\x00\x01\x00'):
        return ''
    if not os.path.isdir(folder):
        os.makedirs(folder)
    with open(target, 'wb') as handle:
        handle.write(data)
    return target

def add(path, name, url, group, logo_path, station_id):
    line = '#EXTINF:-1 radio="true" tvg-id="{0}" tvg-logo="{1}" group-title="{2}",{3}'.format(
        station_id, logo_path, group, name)
    with open(path, 'r', encoding='utf-8') as handle:
        content = handle.read()
    if not content.endswith('\n'):
        content += '\n'
    content += line + '\n' + url + '\n'
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write(content)
