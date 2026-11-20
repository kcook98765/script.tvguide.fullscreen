"""Optional named-provider directory lookup; no Kodi imports or command grammar.

Search results/details belong to the provider, not the guide's plot/art cache.
Keep this module stdlib-only and compatible with Python 3.8.
"""
import json
import re
from urllib.parse import urlencode, quote


TMDBHELPER = 'plugin.video.themoviedb.helper'
HEADING = 'TV Guide — optional metadata lookup'


def search_uri(provider, media_type, query):
    """Only one reviewed directory route, never provider IDs/actions from data."""
    if provider != TMDBHELPER or media_type not in ('movie', 'tv'):
        raise ValueError('Unsupported metadata provider or media type.')
    if (not isinstance(query, str) or not query.strip() or len(query) > 1024
            or any((ord(c) < 32 and c not in '\t\n\r')
                   or 0xD800 <= ord(c) <= 0xDFFF for c in query)):
        raise ValueError('Enter a nonblank title of at most 1024 characters. '
                         'XML title whitespace (tab/newline/CR) is supported; '
                         'invalid XML control characters or Unicode surrogates are not.')
    # Encode *all* query delimiters, including literal +, &, =, %, quotes and
    # backslashes. Do not strip punctuation/year or rewrite the programme title.
    return 'plugin://' + TMDBHELPER + '/?' + urlencode(
        [('info', 'search'), ('tmdb_type', media_type), ('query', query)],
        quote_via=quote, safe='')


def supported_version(version):
    """Known route families; new major versions need receiver review first."""
    if not isinstance(version, str) or not re.fullmatch(r'[45]\.\d+\.\d+', version):
        return False
    parts = tuple(int(n) for n in version.split('.'))
    return (parts[0] == 4 and parts >= (4, 10, 14)
            or parts[0] == 5 and parts >= (5, 4, 16))


class MetadataSearch:
    def __init__(self, execute, dialog):
        self.execute = execute
        self.dialog = dialog
        self.sequence = 0

    def _rpc(self, method, params):
        self.sequence += 1
        request = dict(jsonrpc='2.0', id=self.sequence, method=method, params=params)
        try:
            response = json.loads(self.execute(json.dumps(request)))
        except (ValueError, TypeError) as error:
            raise RuntimeError('Unreadable Kodi response') from error
        if (not isinstance(response, dict) or response.get('jsonrpc') != '2.0'
                or type(response.get('id')) is not int or response['id'] != self.sequence
                or 'error' in response or 'result' not in response):
            raise RuntimeError('Unconfirmed Kodi response')
        return response['result']

    def _provider(self):
        result = self._rpc('Addons.GetAddonDetails', {
            'addonid': TMDBHELPER, 'properties': ['installed', 'enabled', 'version']})
        addon = result.get('addon') if isinstance(result, dict) else None
        if (not isinstance(addon, dict) or addon.get('addonid') != TMDBHELPER
                or addon.get('installed') is not True or addon.get('enabled') is not True):
            raise ValueError('TMDbHelper must already be installed and enabled. '
                             'Use Kodi Add-ons to manage it; guide search still works.')
        if not supported_version(addon.get('version')):
            raise ValueError('This lookup supports TMDbHelper 4.10.14+ (4.x, Matrix) '
                             'or 5.4.16+ (5.x, newer Kodi). Other versions need review. '
                             'Guide search is still available.')

    def run(self, title='', provider=TMDBHELPER):
        """True means window dispatch acknowledged, never provider/UI acceptance."""
        try:
            if provider != TMDBHELPER:
                raise ValueError('Unsupported metadata provider. Choose TMDbHelper; '
                                 'arbitrary add-on commands are not supported.')
            choice = self.dialog.select('Lookup in TMDbHelper — choose media type',
                                        ['Movie search / details', 'TV show search / details'])
            if type(choice) is not int or choice not in (0, 1):
                return False
            # GetAddonDetails returns an RPC error when absent; the same useful
            # prerequisite explanation covers absence and an unreadable inventory.
            try:
                self._provider()
            except (RuntimeError, TypeError, KeyError, json.JSONDecodeError):
                raise ValueError('Cannot verify TMDbHelper. It must already be installed '
                                 'and enabled in Kodi Add-ons. Guide search still works.')
            query = self.dialog.input('TMDbHelper title (online; use Information on a result)',
                                      title if isinstance(title, str) else '')
            if query == '':  # Keyboard cancelled or cleared; no provider dispatch.
                return False
            uri = search_uri(provider, ('movie', 'tv')[choice], query)
            self._provider()  # Recheck after the keyboard, without enabling/installing.
            if self._rpc('GUI.ActivateWindow', {
                    'window': 'videos', 'parameters': [uri, 'return']}) != 'OK':
                raise RuntimeError('Window dispatch not acknowledged')
            return True
        except ValueError as error:
            self.dialog.ok(HEADING, str(error))
        except Exception:
            self.dialog.ok(HEADING, 'TMDbHelper lookup could not be confirmed. '
                           'If its window opened, use Back to return to the guide. '
                           'No automatic retry was made; internal guide search remains available.')
        return False
