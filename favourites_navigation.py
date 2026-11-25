# SPDX-License-Identifier: GPL-2.0-or-later
"""Closed Favorites routes; stored settings/labels never become Kodi commands."""

# Keep Matrix/Nexus's supported dialog. Omega removed it in favor of the browser.
LEGACY_NATIVE = 'ActivateWindow(10134)'
_PROVIDERS = {
    'Simple Favourites': ('ActivateWindow(10001,plugin://plugin.program.simple.favourites,return)',
                          'plugin.program.simple.favourites'),
    'Video Favourites': ('ActivateWindow(10025,plugin://plugin.video.favourites,return)',
                         'plugin.video.favourites'),
    'Super Favourites': ('ActivateWindow(10001,plugin://plugin.program.super.favourites,return)',
                         'plugin.program.super.favourites'),
}


def native_command(build_version):
    """System.BuildVersion starts with the major; never interpolate it in a builtin."""
    try:
        major = int(build_version.split('.', 1)[0])
    except (AttributeError, TypeError, ValueError):
        major = 0  # Preserve the old route if Kodi cannot supply a version.
    return 'ActivateWindow(favouritesbrowser)' if major >= 21 else LEGACY_NATIVE


def route(value, build_version):
    """Legacy select/values persists names, not indices. Unset uses its XML default.

    No setting migration/writes, numeric-index guesses, command parsing or provider
    installation. The optional add-on ID is fixed alongside its fixed command.
    """
    if value is None or value in ('', 'Favourites'):
        return native_command(build_version), None
    if not isinstance(value, str):
        return None, None
    return _PROVIDERS.get(value, (None, None))
