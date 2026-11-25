"""User action-bar choices are data, never Kodi command text (GPL-2.0-or-later)."""
import json
import os
import tempfile


PROFILE = 'special://profile/addon_data/script.tvguide.fullscreen/actions.json'
MAX_BYTES = 65536
MAX_ROWS = 32
MAX_STRING = 1024

# Reviewed original bundled actions, in their original order. Only this code
# supplies commands to Kodi; neither profile nor bundled JSON is executable.
CATALOG = (
    ('num', 'Num', 'Action(MiddleClick)', ''),
    ('stop', 'Stop', 'Action(Stop)', ''),
    ('search', 'Search', 'Action(Number4)', 'button_search.png'),
    ('title', 'Title', 'Action(Blue)', ''),
    ('now', 'Now', 'Action(Number2)', ''),
    ('next-program', 'Next', 'Action(Number3)', ''),
    ('remind', 'Remind', 'Action(Number5)', ''),
    ('autoplay', 'Autoplay', 'Action(Number6)', ''),
    ('next-page', 'Next', 'Action(SkipNext)', ''),
    ('previous-page', 'Prev', 'Action(skipprevious)', ''),
    ('home', 'Home', 'Action(FirstPage)', ''),
    ('first', 'First', 'Action(LastPage)', ''),
    # Keep the exact legacy token for saved-row compatibility. TVGuide remaps
    # this native-only shortcut to the supported Kodi window at dispatch time.
    ('favourites', 'Favs', 'ActivateWindow(10134)', ''),
    ('quit', 'Quit', 'Action(Close)', ''),
)
_COMMANDS = {key: command for key, label, command, icon in CATALOG}
_LEGACY_IDS = {command: key for key, command in _COMMANDS.items()}


def defaults():
    return [[label, key, icon] for key, label, command, icon in CATALOG]


def normalize(rows):
    """Return closed-ID rows and an unsupported count, or reject malformed data."""
    if not isinstance(rows, list) or len(rows) > MAX_ROWS:
        raise ValueError('Invalid action-bar rows')
    result = []
    unsupported = 0
    for row in rows:
        if (not isinstance(row, list) or len(row) != 3 or
                any(not isinstance(s, str) or len(s) > MAX_STRING for s in row)):
            raise ValueError('Invalid action-bar row')
        # JSON accepts escaped lone surrogates; Kodi's UTF-8 string boundary
        # does not. Validate encoding without altering valid display data.
        for value in row:
            value.encode('utf-8')
        label, key, icon = row
        key = key if key in _COMMANDS else _LEGACY_IDS.get(key)
        if key is None:
            unsupported += 1
        else:
            result.append([label, key, icon])
    return result, unsupported


def load(path):
    """Bounded read; fallback never deletes, migrates or rewrites the original."""
    try:
        with open(path, 'rb') as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError('Action-bar file too large')
        rows, unsupported = normalize(json.loads(data.decode('utf-8')))
        warning = ('Action bar: unsupported custom commands/IDs skipped; '
                   'original file unchanged.') if unsupported else ''
        return rows, warning
    except FileNotFoundError:
        return defaults(), ''
    except (OSError, ValueError, RecursionError):
        return defaults(), 'Action bar: unreadable or malformed profile; using defaults, original file unchanged.'


def save(path, rows):
    """Explicit save/reset only. Atomic replacement preserves the old file on failure."""
    temporary = None
    try:
        rows, unsupported = normalize(rows)
        if unsupported:
            return False
        data = json.dumps(rows, ensure_ascii=False, indent=2).encode('utf-8')
        if len(data) > MAX_BYTES:
            return False
        folder = os.path.dirname(path)
        os.makedirs(folder, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=folder, delete=False) as stream:
            temporary = stream.name
            if stream.write(data) != len(data):
                raise OSError('Incomplete action-bar write')
        os.replace(temporary, path)
        return True
    except (OSError, ValueError):
        return False
    finally:
        if temporary:
            try:
                os.unlink(temporary)
            except OSError:
                pass


def command_at(rows, position):
    """Reject cancelled/stale selections and raw command strings, even in memory."""
    if type(position) is not int or not 0 <= position < len(rows):
        return None
    row = rows[position]
    if not isinstance(row, list) or len(row) != 3 or not isinstance(row[1], str):
        return None
    return _COMMANDS.get(row[1])
