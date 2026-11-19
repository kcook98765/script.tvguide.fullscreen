import sys
import xbmc,xbmcaddon
from autoplay_data import callback_identity


def main(argv):
    try:
        channel, start = callback_identity(argv)
    except (ValueError, UnicodeError):
        xbmc.log('[script.tvguide.fullscreen] Invalid autoplay data', xbmc.LOGERROR)
        return

    ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')
    if ADDON.getSetting('playing.channel') != channel:
        return
    elif ADDON.getSetting('playing.start') != start:
        return
    ADDON.setSetting('playing.channel','')
    ADDON.setSetting('playing.start','')

    xbmc.executebuiltin('PlayerControl(Stop)')


if __name__ == '__main__':
    main(sys.argv)
