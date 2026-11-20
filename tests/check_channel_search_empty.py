"""Actual extracted search/dialog code, synthetic SQLite and inert UI only.

No legacy module/Kodi stub imports, network, profile, settings or player access.
This is not native Kodi acceptance.
"""
import ast
import datetime
from pathlib import Path
import re
import sqlite3
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]


def extract(path, name, env, methods=None, base=None):
    tree = ast.parse((ROOT / path).read_text(), feature_version=(3, 8))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
    if methods is not None:
        cls.body = [n for n in cls.body if base and isinstance(n, ast.Assign)
                    or isinstance(n, ast.FunctionDef) and n.name in methods]
    cls.bases = [ast.Name(id='WindowCapture', ctx=ast.Load())] if base else []
    if base:
        env['WindowCapture'] = base
    module = ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[]))
    exec(compile(module, str(ROOT / path), 'exec'), env)
    return env[name]


class Cursor(sqlite3.Cursor):
    closed = False
    executed = False

    def execute(self, *args):
        self.executed = True
        return super().execute(*args)

    def close(self):
        self.closed = True
        return super().close()


class Connection(sqlite3.Connection):
    def cursor(self):
        self.last_cursor = super().cursor(factory=Cursor)
        return self.last_cursor


class Control:
    def __init__(self):
        self.items = []
        self.label = None

    def setLabel(self, label):
        self.label = label

    def addItems(self, items):
        self.items.extend(items)

    def getSelectedItem(self):
        return None


class WindowCapture:
    def __init__(self):
        self.controls = {1000: Control(), 1001: Control()}
        self.closed = False

    def getControl(self, number):
        return self.controls[number]

    def setFocus(self, control):
        self.focus = control

    def getFocusId(self):
        return 1000

    def close(self):
        self.closed = True


class ChannelSearchEmpty(unittest.TestCase):
    def setUp(self):
        self.now = datetime.datetime(2026, 1, 15, 12)
        clock = SimpleNamespace(datetime=SimpleNamespace(now=lambda: self.now))
        env = {'datetime': clock, 're': re}
        self.Program = extract('utils.py', 'Program', env)
        Channel = extract('utils.py', 'Channel', env)
        Database = extract('source.py', 'Database', env, {'_channelSearch'})
        self.db = Database()
        self.conn = sqlite3.connect(':memory:', factory=Connection)
        self.addCleanup(self.conn.close)
        def row_factory(cursor, values):
            return {column[0]: datetime.datetime.fromisoformat(value)
                    if column[0] in ('start_date', 'end_date') else value
                    for column, value in zip(cursor.description, values)}

        self.conn.row_factory = row_factory
        self.conn.execute('''CREATE TABLE programs (
            channel, source, title, sub_title, start_date, end_date,
            description, categories, image_large, image_small, season, episode,
            is_new, is_movie, language)''')
        self.db.conn = self.conn
        self.db.source = SimpleNamespace(KEY='fixture')
        self.channels = [Channel('a', 'Fixture News', '', logo='logo.png')]
        self.visible_requests = []

        def visible_channels(visible):
            self.visible_requests.append(visible)
            return self.channels

        self.db._getChannelList = visible_channels
        self.Dialog = extract(
            'gui.py', 'ProgramListDialog',
            {'COMMAND_ACTIONS': {'CLOSE': [92], 'MENU': [117]}},
            {'__init__', 'onInit', 'onAction'}, base=WindowCapture)

    def search(self, query):
        # Bind datetimes just as source.py does, without global adapter changes.
        # SQLite's default adapter preserves these ISO timestamps; explicit
        # fixture strings below retain the same ordering/comparison semantics.
        return self.db._channelSearch(query)

    def assert_empty(self, query):
        self.assertEqual(self.search(query), [])
        self.assertTrue(self.conn.last_cursor.closed)
        self.assertFalse(self.conn.last_cursor.executed)
        self.assertEqual(self.visible_requests, [True])

    def test_no_matching_visible_channel_returns_empty_and_closes_cursor(self):
        self.assert_empty('absent')

    def test_zero_visible_channels_returns_empty_and_closes_cursor(self):
        self.channels = []
        self.assert_empty('Fixture')

    def test_no_match_cursor_is_closed(self):
        self.search('absent')
        self.assertTrue(self.conn.last_cursor.closed, 'no-match cursor leaked')

    def test_no_match_dialog_renders_empty_and_back_closes(self):
        dialog = self.Dialog('Synthetic search', self.search('absent'))
        dialog.onInit()
        self.assertEqual(dialog.controls[1001].label, 'Synthetic search')
        self.assertEqual(dialog.controls[1000].items, [])
        self.assertIs(dialog.focus, dialog.controls[1000])
        dialog.onAction(SimpleNamespace(getId=lambda: 92))
        self.assertTrue(dialog.closed)
        self.assertEqual(dialog.index, -1)
        self.assertIsNone(dialog.action)

    def test_matching_current_programme_metadata_and_filters_unchanged(self):
        self.channels.append(SimpleNamespace(id='b', title='Other channel'))
        start = self.now - datetime.timedelta(minutes=15)
        end = self.now + datetime.timedelta(minutes=15)
        metadata = ('Episode', 'Subtitle', str(start), str(end), 'Description',
                    'Drama', 'large.png', 'small.png', '2', '3', 1, 0, 'en')
        for channel, source, begin, finish in (
                ('a', 'fixture', start, end),
                ('a', 'other-source', start, end),
                ('b', 'fixture', start, end),
                ('hidden', 'fixture', start, end),
                ('a', 'fixture', start - datetime.timedelta(hours=2), start),
                ('a', 'fixture', end, end + datetime.timedelta(hours=2))):
            row = (channel, source) + metadata[:2] + (str(begin), str(finish)) + metadata[4:]
            self.conn.execute('INSERT INTO programs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', row)
        # Exercises existing case-insensitive regex and space -> .* behavior.
        result = self.search('fIxTuRe n.ws')
        self.assertEqual(len(result), 1)
        expected = self.Program(self.channels[0], *metadata[:2], start, end,
                                *metadata[4:6], *metadata[6:8],
                                season='2', episode='3', is_new=1, is_movie=0, language='en')
        self.assertEqual(vars(result[0]), vars(expected))
        self.assertIs(result[0].channel, self.channels[0])
        self.assertTrue(self.conn.last_cursor.closed)
        self.assertTrue(self.conn.last_cursor.executed)
        self.assertEqual(self.visible_requests, [True])


if __name__ == '__main__':
    unittest.main(verbosity=2)
