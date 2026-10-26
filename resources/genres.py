# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-
#
# dial411 - the genre menu
#
# Coded by avid (aka avidus/avidus7) & Calix
# https://github.com/avidus7/dial411
#
# Licence: GPL-3.0-or-later. No warranty. See main.py for the full notice.
#
# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-

# Each entry is (what the user sees, [tags to search]).
# Several tags means the database spells it more than one way - we pool them.
# Station counts in the comments are from October 2026, for sanity checking.

GENRES = [
    ('Electronic', [
        ('Dance', ['dance']),                                  # 1791
        ('Electronic', ['electronic', 'electronica']),         # 1332
        ('House', ['house']),                                  # 868
        ('Techno', ['techno']),                                # 448
        ('Retro / Synth', ['retro', 'synthpop']),              # 483
        ('EDM', ['edm']),                                      # 326
        ('Trance', ['trance']),                                # 324
        ('Drum and Bass', ['drum and bass', 'dnb', 'drum n bass']),  # 204
        ('Experimental', ['experimental']),                    # 160
        ('Tech House', ['tech house']),                        # 101
        ('Hardcore', ['hardcore', 'happy hardcore', 'gabber']),# 130
        ('Dubstep', ['dubstep']),                              # 83
        ('Dub', ['dub']),                                      # 71
        ('Industrial', ['industrial']),                        # 65
        ('Jungle', ['jungle']),                                # 59
        ('Lo-fi', ['lo-fi']),                                  # 40
        ('Chiptune / Game', ['chiptune', 'video game music']), # 86
        ('Breaks', ['breaks', 'garage']),                      # 48
        ('Rave', ['rave']),                                    # 30
    ]),
    ('Chill', [
        ('Chillout', ['chillout', 'chill']),                   # 693
        ('Lounge', ['lounge']),                                # 382
        ('Ambient', ['ambient']),                              # 444
        ('Instrumental', ['instrumental']),                    # 224
        ('Downtempo', ['downtempo']),                          # 143
        ('New Age', ['new age']),                              # 72
        ('Meditation', ['meditation']),                        # 71
    ]),
    ('Rock and Metal', [
        ('Rock', ['rock']),                                    # 3466
        ('Classic Rock', ['classic rock']),                    # 1001
        ('Alternative', ['alternative']),                      # 779
        ('Indie', ['indie']),                                  # 504
        ('Metal', ['metal']),                                  # 477
        ('Punk', ['punk']),                                    # 181
        ('New Wave', ['new wave']),                            # 125
        ('Grunge', ['grunge']),                                # 65
        ('Death / Black Metal', ['death metal', 'black metal']),  # 87
    ]),
    ('Pop', [
        ('Pop', ['pop']),                                      # 6760
        ('Top 40', ['top 40']),                                # 1151
        ('Disco', ['disco']),                                  # 400
    ]),
    ('Hip Hop and Soul', [
        ('Soul', ['soul']),                                    # 523
        ('Rap', ['rap']),                                      # 396
        ('Funk', ['funk']),                                    # 377
        ('Reggae', ['reggae']),                                # 306
        ('Hip Hop', ['hip hop']),                              # 244
        ('R&B', ['r&b']),                                      # 208
        ('Trap', ['trap']),                                    # 101
    ]),
    ('Jazz and Blues', [
        ('Jazz', ['jazz']),                                    # 1367
        ('Blues', ['blues']),                                  # 380
    ]),
    ('Classical', [
        ('Classical', ['classical']),                          # 1689
        ('Opera', ['opera']),                                  # 69
    ]),
    ('Country and Folk', [
        ('Country', ['country']),                              # 771
        ('Folk', ['folk']),                                    # 699
        ('Bluegrass', ['bluegrass']),                          # 47
    ]),
    ('World', [
        ('Latin', ['latin']),                                  # 201
        ('World', ['world']),                                  # 97
        ('African', ['african music', 'african']),             # 106
        ('Celtic', ['celtic']),                                # 30
    ]),
    ('Talk and News', [
        ('News', ['news']),                                    # 3545
        ('Talk', ['talk']),                                    # 2032
        ('Sports', ['sports']),                                # 491
        ('Comedy', ['comedy']),                                # 110
    ]),
    ('Decades', [
        ('Oldies', ['oldies']),                                # 1574
        ('80s', ['80s']),                                      # 1339
        ('90s', ['90s']),                                      # 1071
        ('70s', ['70s']),                                      # 628
        ('60s', ['60s']),                                      # 276
        ('2000s', ['00s']),                                    # 181
        ('50s', ['50s']),                                      # 77
        ('40s', ['1940s']),                                    # 42
        ('30s', ['1930s']),                                    # 23
        ('20s', ['20s']),                                      # 22
    ]),
    ('Christian', [
        ('Christian', ['christian']),                          # 1083
        ('Gospel', ['gospel']),                                # 460
    ]),
]

def group_names():
    return [name for name, _ in GENRES]

def entries(group_name):
    for name, items in GENRES:
        if name == group_name:
            return items
    return []
