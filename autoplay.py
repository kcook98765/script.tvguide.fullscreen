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
import datetime
import os
import xbmc
import xbmcgui, xbmcaddon
import source as src
from command_safety import alarm_name
from autoplay_data import encode_identity

from strings import *

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')


class Autoplay(object):
    @staticmethod
    def _paddingMinutes(setting):
        # Legacy enum stores an index, not its displayed minutes. Invalid strings
        # use the existing one-minute default without rewriting saved settings.
        return {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 10}.get(
            ADDON.getSetting(setting), 1)

    def __init__(self, database, addonPath):
        """
        @param database: source.Database
        """
        self.database = database
        self.addonPath = addonPath
        self.icon = os.path.join(self.addonPath, 'icon.png')

    def createAlarmClockName(self, programTitle, startTime, channelId, sourceKey=None):
        return alarm_name('autoplay', programTitle, startTime,
                          channelId, self.database.source.KEY if sourceKey is None else sourceKey)
        
    def scheduleAutoplays(self):
        for program in self.database.getFullAutoplays():
            self._scheduleAutoplay(program.channel.id, program.title, program.startDate, program.endDate)


    def _scheduleAutoplay(self, channelId, programTitle, startTime, endTime):
        t = startTime - datetime.datetime.now()
        timeToAutoplay = ((t.days * 86400) + t.seconds) // 60
        if timeToAutoplay < 0:
            return
        try:
            payload = encode_identity(channelId, str(startTime))
        except (ValueError, UnicodeError):
            xbmc.log('[script.tvguide.fullscreen] Invalid autoplay data', xbmc.LOGERROR)
            return
        #timeToAutoplay = 1
        # Replace only this known old hashed pair when a future event can be
        # reconstructed. Past-start/possibly in-flight callbacks are left alone.
        legacy = alarm_name('autoplay', programTitle, startTime)
        xbmc.executebuiltin('CancelAlarm(%s-start,True)' % legacy)
        xbmc.executebuiltin('CancelAlarm(%s-stop,True)' % legacy)
        name = self.createAlarmClockName(programTitle, startTime, channelId)
        xbmc.executebuiltin('AlarmClock(%s-start,RunScript(special://home/addons/script.tvguide.fullscreen/play.py,%s),%d,True)' %
        (name, payload, timeToAutoplay - self._paddingMinutes('autoplays.before')))

        t = endTime - datetime.datetime.now()
        timeToAutoplay = ((t.days * 86400) + t.seconds) // 60
        #timeToAutoplay = 0
        if ADDON.getSetting('autoplays.stop') == 'true':
            xbmc.executebuiltin('AlarmClock(%s-stop,RunScript(special://home/addons/script.tvguide.fullscreen/stop.py,%s),%d,True)' %
            (name, payload, timeToAutoplay + self._paddingMinutes('autoplays.after')))


    def _unscheduleAutoplay(self, programTitle, startTime, channelId, sourceKey=None):
        for name in (alarm_name('autoplay', programTitle, startTime),
                     self.createAlarmClockName(programTitle, startTime, channelId, sourceKey)):
            xbmc.executebuiltin('CancelAlarm(%s-start,True)' % name)
            xbmc.executebuiltin('CancelAlarm(%s-stop,True)' % name)

    def addAutoplay(self, program,type):
        self.database.addAutoplay(program,type)
        if type == 2 and program.is_new != 'New':
            return
        self._scheduleAutoplay(program.channel.id, program.title, program.startDate, program.endDate)

    def removeAutoplay(self, program, rule=None):
        if rule is None:
            rule = (program.channel.id, program.title, self.database.source.KEY, program.startDate, '0')
        before = self.database.getFullAutoplays()
        self.database.removeAutoplay(program, rule)
        remaining = {self.createAlarmClockName(p.title, p.startDate, p.channel.id)
                     for p in self.database.getFullAutoplays()}
        if self.database.isAutoPlayRequiredForProgramStart(program):
            remaining.add(self.createAlarmClockName(program.title, program.startDate, program.channel.id))
        for previous in before + [program]:
            if self.createAlarmClockName(previous.title, previous.startDate, previous.channel.id) not in remaining:
                self._unscheduleAutoplay(previous.title, previous.startDate, previous.channel.id)

    def clearAutoplays(self):
        before = self.database.getAutoplayAlarmIdentities()
        self.database.clearAllAutoplays()
        for channelId, title, start, sourceKey in before:
            self._unscheduleAutoplay(title, start, channelId, sourceKey)


if __name__ == '__main__':
    database = src.Database()

    def onAutoplaysCleared():
        xbmcgui.Dialog().ok(strings(CLEAR_NOTIFICATIONS), strings(DONE)) #TODO

    def onInitialized(success):
        if success:
            Autoplay(database, ADDON.getAddonInfo('path')).clearAutoplays()
            database.close(onAutoplaysCleared)
            ADDON.setSetting('playing.channel','')
            ADDON.setSetting('playing.start','')
        else:
            database.close()

    database.initialize(onInitialized)
