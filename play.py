import sys
import xbmc,xbmcaddon,xbmcvfs
import sqlite3
from playback_mapping import route_mapping
from autoplay_data import callback_identity


def main(argv):
    try:
        channel, start = callback_identity(argv)
    except (ValueError, UnicodeError):
        xbmc.log('[script.tvguide.fullscreen] Invalid autoplay data', xbmc.LOGERROR)
        return

    ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')
    path = xbmcvfs.translatePath('special://profile/addon_data/script.tvguide.fullscreen/source.db')
    try:
        conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    except Exception as detail:
        xbmc.log("EXCEPTION: (script.tvguide.fullscreen)  %s" % detail, xbmc.LOGERROR)
        return

    try:
        c = conn.cursor()
        c.execute('SELECT stream_url FROM custom_stream_url WHERE channel=?', [channel])
        row = c.fetchone()
    finally:
        conn.close()
    if row:
        url, accepted = route_mapping(row[0], xbmc.executeJSONRPC,
            lambda message: xbmc.log('TV Guide playback mapping: ' + message, xbmc.LOGWARNING),
            allow_folder=False)
        if url is None:
            # No folder UI or action execution from a scheduled background callback.
            return
        ADDON.setSetting('playing.channel',channel)
        ADDON.setSetting('playing.start',start)
        # A media location is data, never a formatted Kodi builtin.
        xbmc.Player().play(item=url)


if __name__ == '__main__':
    main(sys.argv)
