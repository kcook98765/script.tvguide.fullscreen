# -*- coding: utf-8 -*-
#
#      Copyright (C) 2012 Tommy Winther
#      http://tommy.winther.nu
#
#      Modified for FTV Guide (09/2014 onwards)
#      by Thomas Geppert [bluezed] - bluezed.apps@gmail.com
#
#      Modified for TV Guide Fullscreen (2016)
#      by primaeval - primaeval.dev@gmail.com
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import xbmcaddon
import notification
import autoplay
import xbmc, xbmcgui
import source
import time
import time, datetime

def log(x):
    xbmc.log(repr(x))


def _time_left(schedule_type, interval, daily_time, last_update, now):
    """Read legacy schedule strings without rewriting settings or polling."""
    if schedule_type in ('1', 'Time'):
        try:
            hms = daily_time.split(':')
            next_time = now.replace(hour=int(hms[0]), minute=int(hms[1]),
                                    second=0, microsecond=0)
        except (ValueError, IndexError):
            # Same daily default as settings.xml; empty/malformed saves must wait.
            next_time = now.replace(hour=3, minute=33, second=0, microsecond=0)
        if next_time < now:
            next_time += datetime.timedelta(hours=24)
    else:
        # '0', the legacy default 'Period', empty and unknown values use period.
        try:
            interval = int(interval)
        except ValueError:
            interval = 1
        wait_time = {0: 7200, 1: 21600, 2: 43200, 3: 86400}.get(interval, 21600)
        try:
            last_time = datetime.datetime.fromtimestamp(float(last_update or '0.0'))
            next_time = last_time + datetime.timedelta(seconds=wait_time)
        except (ValueError, OverflowError, OSError):
            # Unusable history is due now, like missing/epoch history. The normal
            # update path records a fresh timestamp, not a zero-delay retry loop.
            next_time = now
    td = next_time - now
    return max(0, td.seconds + td.days * 24 * 3600)


class Service(object):
    def __init__(self):
        self.database = source.Database(True)
        self.database.initialize(self.onInit)

    def onInit(self, success):
        if success:
            xbmc.log("[script.tvguide.fullscreen] Background Update Starting...", xbmc.LOGINFO)
            self.database.updateChannelAndProgramListCaches(self.onCachesUpdated)
        else:
            self.database.close()

    def onCachesUpdated(self):
        if ADDON.getSetting('notifications.enabled') == 'true':
            n = notification.Notification(self.database, ADDON.getAddonInfo('path'))
            n.scheduleNotifications()
        if ADDON.getSetting('autoplays.enabled') == 'true':
            n = autoplay.Autoplay(self.database, ADDON.getAddonInfo('path'))
            n.scheduleAutoplays()
        self.database.close(None)
        xbmc.log("[script.tvguide.fullscreen] Background Update Finished", xbmc.LOGINFO)
        if ADDON.getSetting('background.notify') == 'true':
            d = xbmcgui.Dialog()
            d.notification("TV Guide Fullscreen", "Finished Updating")
if __name__ == '__main__':
    ADDON = xbmcaddon.Addon('script.tvguide.fullscreen')

    version = ADDON.getAddonInfo('version')
    if ADDON.getSetting('version') != version:
        #text = xbmcvfs.File('special://home/addons/script.tvguide.fullscreen/changelog.txt','rb').read()
        #xbmcgui.Dialog().textviewer("TV Guide Fullscreen",text)
        ADDON.setSetting('version', version)

    # SQLite owns journal recovery; source updates own their normal lock cleanup.
    # Startup cannot establish ownership of either file and must not delete them.
    try:
        if ADDON.getSetting('autostart') == "true":
            xbmc.executebuiltin("RunAddon(script.tvguide.fullscreen)")

        if ADDON.getSetting('background.service') == 'true':
            monitor = xbmc.Monitor()
            xbmc.log("[script.tvguide.fullscreen] Background service started...", xbmc.LOGDEBUG)
            if ADDON.getSetting('background.startup') == 'true':
                Service()
                ADDON.setSetting('last.background.update', str(time.time()))
                if ADDON.getSetting('service.addon.folders') == "true":
                    xbmc.executebuiltin('RunScript(special://home/addons/script.tvguide.fullscreen/ReloadAddonFolders.py)')
            while not monitor.abortRequested():
                timeLeft = _time_left(ADDON.getSetting('service.type'),
                                      ADDON.getSetting('service.interval'),
                                      ADDON.getSetting('service.time'),
                                      ADDON.getSetting('last.background.update'),
                                      datetime.datetime.now())
                xbmc.log("[script.tvguide.fullscreen] Service waiting for %d seconds" % timeLeft, xbmc.LOGDEBUG)
                if timeLeft and monitor.waitForAbort(timeLeft):
                    break
                if monitor.abortRequested():
                    break
                xbmc.log("[script.tvguide.fullscreen] Service now triggered...", xbmc.LOGDEBUG)
                Service()
                if ADDON.getSetting('service.addon.folders') == "true":
                    xbmc.executebuiltin('RunScript(special://home/addons/script.tvguide.fullscreen/ReloadAddonFolders.py)')
                now = time.time()
                ADDON.setSetting('last.background.update', str(now))

    except source.SourceNotConfiguredException:
        pass  # ignore
    except Exception as ex:
        xbmc.log('[script.tvguide.fullscreen] Uncaught exception in service.py: %s' % str(ex), xbmc.LOGDEBUG)
