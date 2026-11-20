# SPDX-License-Identifier: GPL-2.0-or-later
"""Small Python 3.8, stdlib-only mapping boundary, not a Kodi command parser.

Saved mappings stay unchanged. Only the listed legacy wrappers are recognized;
their contents are never executed as Kodi language. See docs/typed-playback-mappings.md.
"""
from enum import Enum
import json
import re
from typing import NamedTuple


class Kind(Enum):
    PLAY = 'play'
    OPEN_FOLDER = 'open_folder'
    RUN_ADDON = 'run_addon'


class Mapping(NamedTuple):
    kind: Kind
    uri: str
    window: str = ''


class MappingError(ValueError):
    """Only fixed, locally authored explanations may reach the user."""


def _argument(text):
    # Only the exact quoted StringUtils::Paramify representation: doubled
    # backslashes and backslash-escaped quotes. Invert those two escapes once,
    # as SplitParams does, into DATA, never another command. Not unicode_escape,
    # JSON-string decoding, percent-decoding or a general Kodi grammar parser.
    if re.fullmatch(r'"(?:[^"\\]|\\["\\])+"', text):
        return re.sub(r'\\(["\\])', r'\1', text[1:-1])
    elif text and not re.search(r'[,()"\\]', text):
        return text
    raise MappingError('Ambiguous legacy mapping. Select a plain media path/URL or '
                       'a Kodi-generated folder favourite (quoted backslashes must be doubled).')


def plugin_id(uri):
    match = re.match(r'plugin://([a-zA-Z0-9_.-]+)(?=[/?#]|$)', uri)
    if not match:
        raise MappingError('This mapping needs an ordinary plugin:// add-on URI.')
    return match.group(1)


def parse_mapping(value):
    if (not isinstance(value, str) or not value or
            any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value)):
        raise MappingError('Empty or invalid playback mapping.')
    if value.startswith('@'):
        uri = value[1:]
        plugin_id(uri)
        return Mapping(Kind.RUN_ADDON, uri)
    folder = re.fullmatch(r'ActivateWindow\((10025|Videos|10001|Programs),(.+),return\)', value, re.I)
    if folder:
        uri = _argument(folder.group(2))
        plugin_id(uri)
        window = 'videos' if folder.group(1).lower() in ('10025', 'videos') else 'programs'
        return Mapping(Kind.OPEN_FOLDER, uri, window)
    media = re.fullmatch(r'PlayMedia\((.+)\)', value, re.I)
    if media:
        return Mapping(Kind.PLAY, _argument(media.group(1)))
    # Unknown/malformed Kodi-looking text is not a media filename. URI data
    # (including quotes, commas, parentheses, Unicode and percent escapes) stays
    # byte-for-byte text; it is not split or decoded into command strings.
    if re.match(r'\s*(?:XBMC\.)?[A-Za-z][\w.]*\s*\(', value, re.I):
        raise MappingError('Unsupported legacy command mapping. No command was executed.')
    return Mapping(Kind.PLAY, value)


def route_mapping(value, execute, report, allow_folder=True):
    """Return (media URI, False), or (None, folder dispatch acknowledged).

    False with no URI means rejection, never playback success. No retry on RPC
    failure/response loss. Injected execute/report keep this module Kodi-free.
    """
    try:
        mapping = parse_mapping(value)
        if mapping.kind == Kind.PLAY:
            return mapping.uri, False
        if mapping.kind == Kind.RUN_ADDON:
            raise MappingError('Alternative @ plugin actions are temporarily blocked: '
                               'Kodi ExecuteAddon is not RunPlugin-equivalent. '
                               'The saved mapping is retained; no action was executed.')
        if not allow_folder:
            raise MappingError('Scheduled autoplay supports media playback only. '
                               'Open this folder mapping interactively in the guide.')

        def rpc(method, params, sequence):
            response = json.loads(execute(json.dumps(dict(
                jsonrpc='2.0', id=sequence, method=method, params=params))))
            if (not isinstance(response, dict) or response.get('jsonrpc') != '2.0' or
                    type(response.get('id')) is not int or response['id'] != sequence or
                    'error' in response or 'result' not in response):
                raise RuntimeError('Unconfirmed response')
            return response['result']

        # Content filtering checks the installed manifest, not ID prefixes or
        # untrusted favourite labels. No install, enable or provider setup.
        result = rpc('Addons.GetAddons', {
            'type': 'xbmc.python.pluginsource',
            'content': 'video' if mapping.window == 'videos' else 'executable',
            'installed': True, 'enabled': True}, 1)
        addons = result.get('addons', []) if isinstance(result, dict) else []
        if not isinstance(addons, list) or not any(
                isinstance(addon, dict) and addon.get('addonid') == plugin_id(mapping.uri)
                and addon.get('type') == 'xbmc.python.pluginsource' for addon in addons):
            raise MappingError('Folder mapping requires an already installed, enabled plugin '
                               'providing the selected video/program content. Manage add-ons '
                               'in Kodi; nothing was enabled or installed.')
        if rpc('GUI.ActivateWindow', {
                'window': mapping.window, 'parameters': [mapping.uri, 'return']}, 2) != 'OK':
            raise RuntimeError('Unconfirmed window dispatch')
        return None, True  # Dispatch only, not provider completion or playback.
    except MappingError as error:
        report(str(error))
    except Exception:
        report('Mapping dispatch could not be confirmed. If a folder opened, use Back '
               'to return. No automatic retry was made.')
    return None, False
