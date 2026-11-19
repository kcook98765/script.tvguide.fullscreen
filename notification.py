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
import time
import xbmc
import xbmcgui, xbmcaddon, xbmcvfs
import source as src
from command_safety import alarm_name
from reminder_data import ReminderData, alarm_command

from strings import *


class Notification(object):
    def __init__(self, database, addonPath):
        """
        @param database: source.Database
        """
        self.database = database
        self.addonPath = addonPath
        self.icon = os.path.join(self.addonPath, 'icon.png')
        self.reminders = ReminderData(xbmcvfs.translatePath(
            xbmcaddon.Addon('script.tvguide.fullscreen').getAddonInfo('profile')))

    def createAlarmClockName(self, programTitle, startTime):
        return alarm_name('notification', programTitle, startTime)
       
    def scheduleNotifications(self):
        self.reminders.prune_completed(time.time())
        for program in self.database.getFullNotifications():
            self._scheduleNotification(program.channel.title, program.title, program.startDate)

            
    def _scheduleNotification(self, channelTitle, programTitle, startTime):
        t = startTime - datetime.datetime.now()
        timeToNotification = ((t.days * 86400) + t.seconds) // 60
        if timeToNotification < 0:
            return

        name = self.createAlarmClockName(programTitle, startTime)

        description = strings(NOTIFICATION_5_MINS, channelTitle)
        descriptionNow = strings(NOTIFICATION_NOW, channelTitle)
        try:
            token = self.reminders.save(name, programTitle, description, descriptionNow,
                                        self.icon, startTime.timestamp(), timeToNotification >= 5)
        except (OSError, ValueError, UnicodeError):
            xbmc.log('[script.tvguide.fullscreen] Unable to save reminder data', xbmc.LOGERROR)
            return
        # Do not pass a negative interval for an already missed five-minute phase.
        if timeToNotification >= 5:
            xbmc.executebuiltin(alarm_command(name, token, '5mins', timeToNotification - 5))
        xbmc.executebuiltin(alarm_command(name, token, 'now', timeToNotification))

    def _unscheduleNotification(self, programTitle, startTime):
        name = self.createAlarmClockName(programTitle, startTime)
        self.reminders.cancel(name)
        xbmc.executebuiltin('CancelAlarm(%s-5mins,True)' % name)
        xbmc.executebuiltin('CancelAlarm(%s-now,True)' % name)

    def addNotification(self, program, type):
        self.database.addNotification(program, type)
        self._scheduleNotification(program.channel.title, program.title, program.startDate)

    def removeNotification(self, program):
        before = self.database.getFullNotifications()
        self.database.removeNotification(program)
        remaining = {self.createAlarmClockName(p.title, p.startDate)
                     for p in self.database.getFullNotifications()}
        for previous in before:
            if self.createAlarmClockName(previous.title, previous.startDate) not in remaining:
                self._unscheduleNotification(previous.title, previous.startDate)
        self._unscheduleNotification(program.title, program.startDate)

    def clearNotifications(self):
        self.database.clearAllNotifications()
        for name in self.reminders.clear():
            xbmc.executebuiltin('CancelAlarm(%s-5mins,True)' % name)
            xbmc.executebuiltin('CancelAlarm(%s-now,True)' % name)


if __name__ == '__main__':
    database = src.Database()

    def onNotificationsCleared():
        xbmcgui.Dialog().ok(strings(CLEAR_NOTIFICATIONS), strings(DONE))

    def onInitialized(success):
        if success:
            Notification(database, xbmcaddon.Addon('script.tvguide.fullscreen').getAddonInfo('path')).clearNotifications()
            database.close(onNotificationsCleared)
        else:
            database.close()

    database.initialize(onInitialized)
