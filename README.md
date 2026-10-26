# dial411

Radio station artwork and info lookup for Kodi.

Finds artwork and details for internet radio stations and adds them to your
playlist, using the free [Radio Browser](https://api.radio-browser.info)
database. Shows you what it found and lets you choose what to apply. It never
changes anything without being asked, and it backs up your playlist first.

## What it does

**Find stations** - browse by genre (72 genres across 12 groups), or search by
name. Every station shows its bitrate, country and whether the stream was alive
at the last check.

**Listen before you commit** - play any station from the info page before
adding it. If the stream is down, it tells you instead of hanging.

**Artwork, properly** - looks for logos in the Radio Browser database and on
the station's own website, shows you every one it found as a picture, and lets
you pick the best. Artwork is saved to your own drive, so it keeps working when
a station redesigns its site.

**Your own stations** - play them, change their artwork, find other sources for
the same station, or remove them.

**Other sources** - many stations are listed more than once with different
stream addresses. If one is down or slow, you can see the alternatives.

## Requirements

- Kodi 19 (Matrix) or newer
- An M3U radio playlist
- Optional: IPTV Merge, which dial411 will offer to run after making changes

## Installing

Download the latest release zip, then in Kodi:

**Add-ons** then **Install from zip file**, and pick the downloaded file.

You will need "Unknown sources" enabled in **Settings**, **System**, **Add-ons**.

## Setting your playlist

dial411 reads and writes a single M3U file. Set its path in the add-on's
settings.

## A note on your playlist

Every change makes a timestamped backup of your playlist first. Nothing is
overwritten silently, and artwork you have chosen yourself is never replaced
without being asked.

## Thanks

To the Radio Browser community, who maintain a genuinely free and open database
of internet radio stations, and ask nothing for it.

## Licence

GPL-3.0-or-later. See LICENSE.
