"""Kodi-only adapter for the passive custom guide skin snapshot."""
import xbmcgui
import xbmcvfs
from typing import Dict, Optional, Tuple

from custom_skin import BUNDLED, SkinError, Snapshot, prepare


GUIDE_URL = ('https://github.com/kcook98765/script.tvguide.fullscreen/'
             'blob/preserve/custom-skins/docs/custom-guide-skins.md')


def select_skin(addon):
    bundled = addon.getSetting('skin')
    if bundled not in BUNDLED:
        bundled = 'Default'
    fallback: Tuple[str, str, Dict[str, str], Optional[Snapshot]] = (addon.getAddonInfo('path'), bundled, {}, None)
    if addon.getSetting('skin.custom.enabled') != 'true':
        return fallback
    try:
        source_type = addon.getSetting('skin.source')
        if source_type == '0':
            return fallback
        elif source_type == '1':
            source = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
        elif source_type == '2':
            source = addon.getSetting('skin.folder')
            if source.startswith('special://profile/'):
                source = xbmcvfs.translatePath(source)
        else:
            raise SkinError('Choose Profile or Local folder under Skin Type.')
        snapshot = prepare(addon.getAddonInfo('path'), source,
                           addon.getSetting('skin.user'), bundled,
                           xbmcvfs.translatePath('special://temp/'))
        return snapshot.path, snapshot.skin, snapshot.filenames, snapshot
    except (OSError, ValueError, ImportError, RecursionError) as exc:
        # Do not echo arbitrary source XML, paths, commands or credentials.
        reason = str(exc) if isinstance(exc, SkinError) else 'Cannot read/prepare the local passive skin.'
        xbmcgui.Dialog().ok('Passive styling/layout overrides unavailable',
                            reason + '\nUsing bundled ' + bundled + '. Originals are unchanged. '
                            'Guide (web): ' + GUIDE_URL)
        return fallback
