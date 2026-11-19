# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
"""Fixed bundled AlarmClock entry point; never import the legacy guide or DB."""
import sys
import time
from typing import List

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from reminder_data import ReminderData, deliver, valid_token, PHASES


def main(argv: List[str]) -> None:
    if len(argv) != 3 or not valid_token(argv[1]) or argv[2] not in PHASES:
        return
    profile = xbmcvfs.translatePath(xbmcaddon.Addon('script.tvguide.fullscreen').getAddonInfo('profile'))
    try:
        deliver(ReminderData(profile), argv[1], argv[2], time.time(), xbmcgui.Dialog().notification)
    except (OSError, ValueError, UnicodeError):
        # Do not log the private title/body/path or any malformed profile data.
        xbmc.log('[script.tvguide.fullscreen] Invalid or unavailable reminder data', xbmc.LOGERROR)


if __name__ == '__main__':
    main(sys.argv)
