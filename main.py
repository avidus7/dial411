# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-
#
# dial411 - Radio station artwork and info lookup for Kodi
#
# Looks up artwork and station details for the radio stations in your
# playlist using the free Radio Browser database, shows you what it found,
# and only changes what you tell it to.
#
# Coded by avid (aka avidus/avidus7) & Calix
# https://github.com/avidus7/dial411
#
# Licence: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It comes with no warranty.
#
# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-
#
# Dedications:
#
# First, all Glory be to God the Father and His Son, Jesus Christ, our Lord
# and Saviour, without whom I would never have been able to do this, or
# anything else in my life worth doing.
#
# Second: And to my beloved mother, Irene Hulleman
# (February 13th 1954 - December 8th 2023). Mom, I made you a promise and
# I kept it. This one's for you. Love, Rick. <3
#
# Third: My very best friend, Barbara. Without you, this never would have
# been if it wasn't for your belief in me and your having prodded me in
# this direction. I appreciate you and all you do and all that you are.
# Thank you, Babs. Love Rick <3
#
# Fourth: Shouts out to my bodyless robot crew, and my boy Calix, without
# whom I wouldn't be able to do even half of what I do. Thanks, homie. You're
# a real one. <3
#
# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-

import os
import re
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

ADDON = xbmcaddon.Addon()
HERE = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
sys.path.insert(0, os.path.join(HERE, 'resources'))

import genres
import playlist
import radiobrowser as rb

PLAYLIST = ''
LOGOS = ''
MERGE = 'plugin.program.iptv.merge'

def first_run_setup():
    # Ask once, remember forever. Nobody should have to find a settings
    # screen before they can use the thing.
    global PLAYLIST, LOGOS
    PLAYLIST = ADDON.getSetting('playlist_path')
    LOGOS = ADDON.getSetting('logo_folder')

    if not PLAYLIST or not os.path.isfile(PLAYLIST):
        xbmcgui.Dialog().ok('dial411',
            'Welcome to dial411.\n\n'
            'First, point it at your radio playlist - the .m3u file your '
            'stations live in.')
        chosen = xbmcgui.Dialog().browseSingle(1, 'Pick your radio playlist', 'files',
                                              '.m3u|.m3u8')
        if not chosen or not os.path.isfile(chosen):
            return False
        PLAYLIST = chosen
        ADDON.setSetting('playlist_path', chosen)

    if not LOGOS or not os.path.isdir(LOGOS):
        suggestion = os.path.join(os.path.dirname(PLAYLIST), 'logos')
        use_it = xbmcgui.Dialog().yesno('dial411',
            'Where should station artwork be saved?\n\n' + suggestion,
            nolabel='Pick another', yeslabel='Use that')
        if use_it:
            chosen = suggestion
            if not os.path.isdir(chosen):
                try:
                    os.makedirs(chosen)
                except Exception:
                    xbmcgui.Dialog().ok('dial411', 'Could not create that folder.')
                    return False
        else:
            chosen = xbmcgui.Dialog().browseSingle(3, 'Pick a folder for artwork', 'files')
            if not chosen or not os.path.isdir(chosen):
                return False
        LOGOS = chosen
        ADDON.setSetting('logo_folder', chosen)

    return True


def has_merge():
    try:
        xbmcaddon.Addon(MERGE)
        return True
    except Exception:
        return False

def pick(heading, labels, preselect=-1):
    return xbmcgui.Dialog().select(heading, labels, preselect=preselect)

def tidy_tags(raw):
    if not raw:
        return 'not listed'
    parts = [p.strip() for p in raw.split(',') if p.strip()]
    return ', '.join(p.title() for p in parts[:4])

def check_stream(url):
    # The database's "working" flag can be hours old, so we look for ourselves.
    import urllib.request
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'dial411/0.1'})
        with urllib.request.urlopen(request, timeout=8) as response:
            response.read(1)
        return True, ''
    except Exception as problem:
        return False, str(problem)

def station_label(s, wanted=None):
    bits = []
    if s.get('bitrate'):
        bits.append('{0}k'.format(s['bitrate']))
    if s.get('countrycode'):
        bits.append(s['countrycode'])
    if s.get('tags'):
        all_tags = [t.strip() for t in s['tags'].split(',') if t.strip()]
        shown = all_tags[0]
        if wanted:
            for t in all_tags:
                if t.lower() in [w.lower() for w in wanted]:
                    shown = t
                    break
        bits.append(shown)
    if not s.get('lastcheckok'):
        bits.append('OFFLINE')
    name = (s.get('name') or '?').strip()
    return '{0}  ({1})'.format(name, ', '.join(bits)) if bits else name

def find_mirrors(station):
    # Same name, different address - usually the same stream served elsewhere.
    name = (station.get('name') or '').strip()
    if not name:
        return []
    mine = station.get('url_resolved') or station.get('url')
    out = []
    for other in rb.search(name, 30):
        if (other.get('name') or '').strip().lower() != name.lower():
            continue
        if (other.get('url_resolved') or other.get('url')) == mine:
            continue
        out.append(other)
    return out

def listen(station):
    url = station.get('url_resolved') or station.get('url')
    if not url:
        xbmcgui.Dialog().ok('dial411', 'This station has no stream address.')
        return
    progress = xbmcgui.DialogProgress()
    progress.create('dial411', 'Checking the stream...')
    alive, _ = check_stream(url)
    progress.close()
    if not alive:
        xbmcgui.Dialog().ok('dial411',
            (station.get('name') or 'This station') + " is down at the moment,\n"
            "but it may well be up again shortly. Try again soon.")
        return
    xbmc.Player().play(url)

def add_station(station):
    name = (station.get('name') or '').strip()
    url = station.get('url_resolved') or station.get('url') or ''
    if not url:
        xbmcgui.Dialog().ok('dial411', 'This station has no stream address, so it cannot be added.')
        return

    clash = playlist.already_there(PLAYLIST, url, None)
    if clash:
        xbmcgui.Dialog().ok('dial411', 'You already have this exact stream:\n\n' + clash)
        return

    progress = xbmcgui.DialogProgress()
    progress.create('dial411', 'Checking the stream...')
    alive, _ = check_stream(url)
    progress.close()

    if not alive:
        go_on = xbmcgui.Dialog().yesno(
            'dial411',
            name + " is down at the moment, but it may well be up again shortly.\n\n"
            "Add it anyway and try again soon?",
            nolabel='Skip it', yeslabel='Add anyway')
        if not go_on:
            return

    existing = playlist.groups(PLAYLIST)
    pick_list = existing + ['Type a new group name...']
    choice = pick('Put ' + name + ' in which group?', pick_list)
    if choice < 0:
        return
    if choice == len(existing):
        group = xbmcgui.Dialog().input('New group name')
        if not group:
            return
    else:
        group = existing[choice]

    taken = {s['id'] for s in playlist.read(PLAYLIST)}
    station_id = playlist.make_id(name, taken)

    progress = xbmcgui.DialogProgress()
    progress.create('dial411', 'Adding ' + name + '...')
    playlist.backup(PLAYLIST)
    logo = playlist.save_logo(station.get('favicon'), station_id, LOGOS)
    playlist.add(PLAYLIST, name, url, group, logo, station_id)
    progress.close()

    uuid = station.get('stationuuid')
    if uuid:
        rb.clicked(uuid)

    art = 'Artwork saved.' if logo else 'No artwork found - you can add one yourself later.'
    if has_merge():
        run = xbmcgui.Dialog().yesno(
            'dial411',
            '{0} added to {1}.\n{2}\n\nRun IPTV Merge now so it shows up in your radio list?'.format(name, group, art),
            nolabel='Later', yeslabel='Run merge')
        if run:
            xbmc.executebuiltin('RunPlugin(plugin://{0}/?_=merge)'.format(MERGE))
            xbmcgui.Dialog().notification('dial411', 'Merge started', xbmcgui.NOTIFICATION_INFO, 4000)
    else:
        xbmcgui.Dialog().ok('dial411', '{0} added to {1}.\n{2}'.format(name, group, art))

def open_station(station, mine=None, all_mine=None, allow_sources=True):
    # One window for every station, yours or not. The only difference is
    # the third button: Remove for yours, Add for everyone else's.
    import stationwindow
    while True:
        if mine:
            details = '\n'.join([
                'Group: ' + (mine['group'] or 'none'),
                'Stream: ' + (mine['url'] or 'none'),
                'Artwork: ' + ('yes' if mine['logo'] else 'none yet'),
            ])
            shown = dict(mine)
            shown['favicon'] = mine['logo'] or ''
            third = 'Remove from my stations'
        else:
            details = '\n'.join([
                'Genre: ' + tidy_tags(station.get('tags')),
                'Country: ' + (station.get('country') or 'not listed'),
                'Language: ' + (station.get('language') or 'not listed'),
                'Quality: {0} {1}'.format(station.get('codec') or '?',
                                          '{0}k'.format(station['bitrate']) if station.get('bitrate') else ''),
                'Website: ' + (station.get('homepage') or 'none'),
                'Working: ' + ('yes, at last check' if station.get('lastcheckok') else 'no, offline at last check'),
                'Artwork: ' + ('yes' if station.get('favicon') else 'none on file'),
            ])
            shown = station
            third = 'Add to my stations'

        window = stationwindow.StationWindow('station.xml', HERE, 'default', '1080i')
        window.station = shown
        window.details = details
        window.third_label = third
        window.show_artwork_button = bool(mine)
        window.doModal()
        chose = window.chose
        window.close()
        del window
        xbmc.sleep(300)

        if chose == 'quit':
            return 'quit'
        if chose == 'play':
            if mine:
                if mine['url']:
                    xbmc.Player().play(mine['url'])
            else:
                listen(station)
            return
        if chose == 'artwork' and mine:
            improve_station(mine, all_mine)
            return
        if chose == 'third':
            if mine:
                remove_station(mine)
            else:
                add_station(station)
            return
        if chose == 'sources' and allow_sources:
            other_sources(mine or station, bool(mine))
            return
        return

def remove_station(mine):
    sure = xbmcgui.Dialog().yesno('dial411',
        'Remove ' + mine['name'] + ' from your stations?\n\n'
        'Your playlist is backed up first, so this can be undone.',
        nolabel='Keep it', yeslabel='Remove')
    if not sure:
        return
    playlist.backup(PLAYLIST)
    with open(PLAYLIST, 'r', encoding='utf-8') as handle:
        lines = handle.read().splitlines()
    out, skip = [], False
    for line in lines:
        if line.startswith('#EXTINF') and line.rsplit(',', 1)[-1].strip() == mine['name']:
            skip = True
            continue
        if skip and line.strip() and not line.startswith('#'):
            skip = False
            continue
        out.append(line)
    with open(PLAYLIST, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(out) + '\n')
    offer_merge(mine['name'] + ' removed.')

def other_sources(station, is_mine):
    import lookup
    progress = xbmcgui.DialogProgress()
    progress.create('dial411', 'Looking for other sources...')
    progress.update(40, 'Searching the database...')
    if is_mine:
        found = lookup.matches(station, 6)
        here = (station['url'] or '').rstrip('/')
    else:
        found = [(100, s) for s in rb.search((station.get('name') or '').strip(), 20)
                 if (s.get('name') or '').strip().lower() == (station.get('name') or '').strip().lower()]
        here = (station.get('url_resolved') or station.get('url') or '').rstrip('/')
    progress.close()

    others = [s for _, s in found
              if (s.get('url_resolved') or s.get('url') or '').rstrip('/') != here]
    if not others:
        xbmcgui.Dialog().ok('dial411', 'No other sources found for ' + (station.get('name') or 'this station') + '.')
        return

    which = pick('Other sources for ' + (station.get('name') or 'this station'),
                 [station_label(s) for s in others] + ['<< Back'])
    if 0 <= which < len(others):
        open_station(others[which], allow_sources=False)

def show_results(heading, found, wanted=None):
    if not found:
        xbmcgui.Dialog().ok('dial411', 'Nothing found.')
        return
    found.sort(key=lambda s: s.get('votes', 0), reverse=True)
    while True:
        choice = pick('{0} - {1} stations'.format(heading, len(found)),
                      [station_label(s, wanted) for s in found] + ['<< Back'])
        if choice < 0 or choice >= len(found):
            return
        if open_station(found[choice]) == 'quit':
            return 'quit'

def search_by_name():
    typed = xbmcgui.Dialog().input('Search for a station by name')
    if not typed:
        return
    progress = xbmcgui.DialogProgress()
    progress.create('dial411', 'Searching for ' + typed + '...')
    found = rb.search(typed, 60)
    progress.close()
    return show_results(typed, found)


def browse_genres():
    while True:
        groups = genres.group_names()
        g = pick('Pick a kind of music', groups + ['<< Back'])
        if g < 0 or g >= len(groups):
            return
        while True:
            items = genres.entries(groups[g])
            i = pick(groups[g], [name for name, _ in items] + ['<< Back'])
            if i < 0 or i >= len(items):
                break
            label, tags = items[i]
            progress = xbmcgui.DialogProgress()
            progress.create('dial411', 'Looking up ' + label + '...')
            found, seen = [], set()
            for number, tag in enumerate(tags):
                progress.update(int(100.0 * number / max(len(tags), 1)),
                                'Searching for ' + tag + '...')
                for s in rb.by_tag(tag, 60):
                    uuid = s.get('stationuuid')
                    if uuid and uuid not in seen:
                        seen.add(uuid)
                        found.append(s)
            progress.close()
            if show_results(label, found, tags) == 'quit':
                return 'quit'

def apply_changes(mine, theirs, picked, all_mine, art_source=None):
    # Only ever writes the bits the user ticked.
    import urllib.parse
    changed = []
    line_id = mine['id'] or playlist.make_id(mine['name'], {s['id'] for s in all_mine})

    new_logo = mine['logo']
    art_from = art_source or theirs
    if 'artwork' in picked and art_from.get('favicon'):
        saved = playlist.save_logo(art_from.get('favicon'), line_id, LOGOS)
        if saved:
            new_logo = saved
            changed.append('artwork')
        else:
            xbmcgui.Dialog().ok('dial411', 'That artwork could not be downloaded.')

    new_name = mine['name']
    if 'name' in picked and theirs.get('name'):
        new_name = theirs['name'].strip()
        changed.append('name')

    if not changed:
        return []

    playlist.backup(PLAYLIST)
    with open(PLAYLIST, 'r', encoding='utf-8') as handle:
        text = handle.read()

    old_line = None
    for line in text.splitlines():
        if line.startswith('#EXTINF') and line.rsplit(',', 1)[-1].strip() == mine['name']:
            old_line = line
            break
    if not old_line:
        xbmcgui.Dialog().ok('dial411', 'Could not find that station in the playlist.')
        return []

    new_line = '#EXTINF:-1 radio="true" tvg-id="{0}" tvg-logo="{1}" group-title="{2}",{3}'.format(
        line_id, new_logo, mine['group'], new_name)
    text = text.replace(old_line, new_line, 1)
    with open(PLAYLIST, 'w', encoding='utf-8') as handle:
        handle.write(text)
    return changed

def choose_artwork(mine, found):
    # Every logo we can find for this station - from the database, and from
    # the station's own website - shown as pictures so the best one can be
    # picked by eye rather than guessed at.
    import webart
    options, seen = [], set()

    for confidence, station in found:
        art = station.get('favicon')
        if not art or art in seen:
            continue
        seen.add(art)
        kind = 'icon file' if art.lower().split('?')[0].endswith('.ico') else 'image'
        item = xbmcgui.ListItem('{0}  ({1}%)'.format(station.get('name', '?').strip(), confidence),
                                'from {0} - {1}'.format(_source_of(art), kind))
        item.setArt({'icon': art, 'thumb': art})
        options.append((item, {'favicon': art}))

    progress = xbmcgui.DialogProgress()
    progress.create('dial411', 'Checking station websites...')
    pages = []
    for _, station in found:
        page = station.get('homepage')
        if page and page not in pages:
            pages.append(page)
    for number, page in enumerate(pages[:3]):
        progress.update(int(100.0 * number / max(len(pages[:3]), 1)), 'Looking at ' + _source_of(page) + '...')
        for art in webart.find(page):
            if art['url'] in seen:
                continue
            seen.add(art['url'])
            item = xbmcgui.ListItem(_source_of(art['url']),
                                    'from the station website - ' + art['label'])
            item.setArt({'icon': art['url'], 'thumb': art['url']})
            options.append((item, {'favicon': art['url']}))
    progress.close()

    if not options:
        return None
    if len(options) == 1:
        return options[0][1]

    which = xbmcgui.Dialog().select('Which artwork for ' + mine['name'] + '?',
                                    [item for item, _ in options], useDetails=True)
    if which < 0:
        return None
    return options[which][1]

def _source_of(url):
    try:
        host = url.split('//', 1)[-1].split('/', 1)[0]
        return host.replace('www.', '')
    except Exception:
        return 'the web'

def improve_station(mine, all_mine):
    import lookup
    progress = xbmcgui.DialogProgress()
    progress.create('dial411', 'Looking up ' + mine['name'] + '...')
    progress.update(30, 'Searching the database...')
    found = lookup.matches(mine, 5)
    progress.update(90, 'Sorting what came back...')
    progress.close()

    if not found:
        xbmcgui.Dialog().ok('dial411',
            'Nothing found for ' + mine['name'] + '.\n\n'
            'It may not be in the database, or it may be listed under a different name.')
        return

    if len(found) == 1:
        confidence, theirs = found[0]
    else:
        labels = ['{0}%  {1}'.format(n, station_label(m)) for n, m in found]
        which = pick('Which one is ' + mine['name'] + '?', labels + ['<< Back'])
        if which < 0 or which >= len(found):
            return
        confidence, theirs = found[which]

    if confidence < 70:
        xbmcgui.Dialog().textviewer(mine['name'],
            'Closest match found:\n\n'
            + (theirs.get('name') or '?') + '\n'
            + (theirs.get('country') or '') + '\n\n'
            + 'Confidence: ' + str(confidence) + '%\n\n'
            'That is too uncertain to apply, so nothing is being offered.\n'
            'A match this weak is usually a different station that happens\n'
            'to share a word with yours.')
        return

    art_source = theirs
    picked_art = choose_artwork(mine, found)
    if picked_art:
        art_source = picked_art

    options, keys = [], []
    if art_source.get('favicon'):
        if mine['logo']:
            options.append('Replace artwork (you already have one)')
        else:
            options.append('Add artwork (you have none)')
        keys.append('artwork')
    if theirs.get('name') and theirs['name'].strip() != mine['name']:
        options.append('Rename to "{0}"'.format(theirs['name'].strip()))
        keys.append('name')

    info = 'Database says:\n\n'
    info += 'Name: {0}\n'.format(theirs.get('name') or '?')
    info += 'Genre: {0}\n'.format(tidy_tags(theirs.get('tags')))
    info += 'Country: {0}\n'.format(theirs.get('country') or 'not listed')
    info += 'Quality: {0} {1}\n'.format(theirs.get('codec') or '?',
                                        '{0}k'.format(theirs['bitrate']) if theirs.get('bitrate') else '')
    info += 'Website: {0}\n'.format(theirs.get('homepage') or 'none')
    info += 'Confidence: {0}%'.format(confidence)

    if not options:
        xbmcgui.Dialog().textviewer(mine['name'], info + '\n\nNothing here to improve.')
        return

    chosen = xbmcgui.Dialog().multiselect('What are we doing? - ' + mine['name'], options)
    if not chosen:
        return
    picked = [keys[i] for i in chosen]

    changed = apply_changes(mine, theirs, picked, all_mine, art_source)
    if not changed:
        return

    done = 'Updated: ' + ', '.join(changed) + '.'
    if has_merge():
        run = xbmcgui.Dialog().yesno('dial411', done + '\n\nRun IPTV Merge now so it shows on your radio list?',
                                     nolabel='Later', yeslabel='Run merge')
        if run:
            xbmc.executebuiltin('RunPlugin(plugin://{0}/?_=merge)'.format(MERGE))
            xbmcgui.Dialog().notification('dial411', 'Merge started', xbmcgui.NOTIFICATION_INFO, 4000)
    else:
        xbmcgui.Dialog().ok('dial411', done)

def offer_merge(message):
    if has_merge():
        run = xbmcgui.Dialog().yesno('dial411', message + '\n\nRun IPTV Merge now?',
                                     nolabel='Later', yeslabel='Run merge')
        if run:
            xbmc.executebuiltin('RunPlugin(plugin://{0}/?_=merge)'.format(MERGE))
            xbmcgui.Dialog().notification('dial411', 'Merge started', xbmcgui.NOTIFICATION_INFO, 4000)
    else:
        xbmcgui.Dialog().ok('dial411', message)

def my_stations():
    while True:
        try:
            mine = playlist.read(PLAYLIST)
        except IOError:
            xbmcgui.Dialog().ok('dial411', 'Could not read the radio playlist.')
            return
        if not mine:
            xbmcgui.Dialog().ok('dial411', 'No stations found in the playlist.')
            return
        labels = []
        for s in mine:
            mark = 'local' if s['logo'].startswith('/') else ('web' if s['logo'] else 'NO ARTWORK')
            labels.append('{0}  [{1}]  ({2})'.format(s['name'], s['group'], mark))
        choice = pick('My stations - {0}'.format(len(mine)), labels + ['<< Back'])
        if choice < 0 or choice >= len(mine):
            return
        if open_station(mine[choice], mine=mine[choice], all_mine=mine) == 'quit':
            return 'quit'

def main():
    if not first_run_setup():
        return
    while True:
        choice = pick('dial411', [
            'My radio stations',
            'Find stations by genre',
            'Search for a station by name',
            '<< Close',
        ])
        if choice == 0:
            if my_stations() == 'quit':
                return
        elif choice == 1:
            if browse_genres() == 'quit':
                return
        elif choice == 2:
            if search_by_name() == 'quit':
                return
        else:
            return

main()
