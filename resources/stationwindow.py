# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-
#
# dial411 - the station details window
#
# Coded by avid (aka avidus/avidus7) & Calix
# https://github.com/avidus7/dial411
#
# Licence: GPL-3.0-or-later. No warranty. See main.py for the full notice.
#
# -=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=-=+=+=-

import xbmcgui

TITLE = 1000
ART = 1001
DETAILS = 1002

# The grid, left to right then top to bottom.
PLAY = 9001
SOURCES = 9002
ARTWORK = 9003
THIRD = 9004      # Remove, or Add to my stations
BACK = 9005
QUIT = 9006

ACTIONS = {PLAY: 'play', SOURCES: 'sources', ARTWORK: 'artwork',
           THIRD: 'third', QUIT: 'quit'}

class StationWindow(xbmcgui.WindowXMLDialog):
    # Set .station, .details and .third_label before calling doModal().
    # Afterwards .chose holds 'play', 'sources', 'artwork', 'third',
    # 'quit' or None for back.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.station = {}
        self.details = ''
        self.third_label = 'Add to my stations'
        self.show_artwork_button = True
        self.chose = None
        self.busy = False

    def onInit(self):
        self.getControl(TITLE).setLabel(self.station.get('name') or 'Station')
        self.getControl(DETAILS).setText(self.details)
        self.getControl(ART).setImage(self.station.get('favicon') or 'noart.png')
        self.getControl(THIRD).setLabel(self.third_label)
        self.getControl(ARTWORK).setEnabled(bool(self.show_artwork_button))
        self.setFocusId(PLAY)

    def onClick(self, control_id):
        if self.busy:
            return
        self.busy = True
        self.chose = ACTIONS.get(control_id)
        self.close()

    def onAction(self, action):
        # 10 is Escape, 92 is Back - both mean "go back a page".
        if action.getId() in (10, 92):
            self.chose = None
            self.close()
