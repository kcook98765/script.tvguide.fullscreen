"""Actual channel-save methods/schema/adapters, in-memory SQLite; no Kodi imports."""
import ast
import datetime
from pathlib import Path
import sqlite3
import time
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]


def extracted_class(path, name, methods=None):
    tree = ast.parse((ROOT / path).read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
    if methods is not None:
        cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in methods]
    env = dict(sqlite3=sqlite3, datetime=datetime, time=time)
    exec(compile(ast.Module(body=[cls], type_ignores=[]), path + ':extracted', 'exec'), env)
    return env[name]


Database = extracted_class('source.py', 'Database', {
    '_createTables', 'adapt_datetime', 'convert_datetime',
    '_saveChannelListBlock', '_saveChannelList',
})
Channel = extracted_class('utils.py', 'Channel')
CHILDREN = ('programs', 'notifications', 'autoplays', 'autoplaywiths')
UNCHANGED = CHILDREN + ('updates', 'custom_stream_url', 'alt_custom_stream_url')
STAMP = datetime.datetime(2026, 11, 20, 8, 0)


class ChannelUpdates(unittest.TestCase):
    def database(self):
        sqlite3.register_adapter(datetime.datetime, Database.adapt_datetime)
        sqlite3.register_converter('timestamp', Database.convert_datetime)
        conn = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
        self.addCleanup(conn.close)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        db = Database.__new__(Database)
        db.conn, db.source = conn, SimpleNamespace(KEY='xmltv')
        # Run the actual empty-database schema/migrations, not a hand-copied schema.
        db._createTables()
        self.assertEqual(tuple(conn.execute('SELECT * FROM version').fetchone()), (1, 4, 1))
        self.assertEqual(conn.execute('PRAGMA foreign_keys').fetchone()[0], 1)
        for source, update in [('xmltv', 1), ('other', 2)]:
            conn.execute('INSERT OR IGNORE INTO sources VALUES (?, ?)', (source, STAMP))
            conn.execute('UPDATE sources SET channels_updated=? WHERE id=?', (STAMP, source))
            conn.execute('INSERT INTO updates VALUES (?, ?, ?, ?)',
                         (update, source, '2026-11-20', STAMP))
            for index, channel in enumerate(('one', 'two', 'omitted')):
                conn.execute('INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                             (channel, source + '/' + channel, 'old.png', 'old.mp4',
                              source, 'Lineup ' + source, 1, index if source == 'xmltv' else 100 + index))
                start = STAMP + datetime.timedelta(hours=update, minutes=index)
                conn.execute('INSERT INTO programs(channel, title, start_date, end_date, '
                             'description, source, updates_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
                             (channel, 'Film (1999)', start, start + datetime.timedelta(minutes=30),
                              'Original plot', source, update))
                for table in CHILDREN[1:]:
                    conn.execute('INSERT INTO ' + table + ' VALUES (?, ?, ?, ?, ?)',
                                 (channel, 'Film (1999)', source, start, '0'))
        conn.execute('INSERT INTO custom_stream_url VALUES (?, ?)', ('one', 'mapped.mp4'))
        conn.execute('INSERT INTO alt_custom_stream_url VALUES (?, ?, ?)',
                     ('one', 'Alternate', 'alternate.mp4'))
        conn.commit()
        self.assertEqual(conn.execute('SELECT typeof(start_date) FROM programs').fetchone()[0], 'integer')
        self.assertIsInstance(conn.execute('SELECT start_date FROM programs').fetchone()[0], datetime.datetime)
        return db

    def rows(self, db, table, where='', args=()):
        return [tuple(r) for r in db.conn.execute('SELECT * FROM ' + table + ' ' + where, args)]

    def test_import_and_reorder_preserve_cached_guide_and_rules(self):
        for reorder in (False, True):
            with self.subTest(reorder=reorder):
                db = self.database()
                before = {t: self.rows(db, t) for t in UNCHANGED}
                other = self.rows(db, 'channels', 'WHERE source=?', ('other',))
                channel_list = [Channel('one', 'xmltv/one', 'Lineup xmltv', 'old.png', 'old.mp4', True, 0),
                                Channel('two', 'xmltv/two', 'Lineup xmltv', 'old.png', 'old.mp4', True, 1),
                                Channel('omitted', 'xmltv/omitted', 'Lineup xmltv', 'old.png', 'old.mp4', True, 2)]
                if reorder:
                    channel_list.reverse()
                    for weight, channel in enumerate(channel_list, 1):
                        channel.weight = weight
                db.channelList = ['stale cache']
                db._saveChannelListBlock(channel_list)
                after = {t: self.rows(db, t) for t in UNCHANGED}
                print('reorder=', reorder, 'child rows before/after=',
                      {t: (len(before[t]), len(after[t])) for t in CHILDREN},
                      'mapping retained=', after['custom_stream_url'] == before['custom_stream_url'],
                      'other-source channels=', len(self.rows(db, 'channels', 'WHERE source=?', ('other',))))
                self.assertEqual(after, before)
                self.assertEqual(self.rows(db, 'channels', 'WHERE source=?', ('other',)), other)
                self.assertEqual([tuple(r) for r in db.conn.execute(
                    'SELECT id, weight FROM channels WHERE source=? ORDER BY weight', ('xmltv',))],
                    [(c.id, c.weight) for c in channel_list])
                self.assertIsNone(db.channelList)
                self.assertEqual(db.conn.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_metadata_additions_partial_list_and_append_weights(self):
        db = self.database()
        before = {t: self.rows(db, t) for t in UNCHANGED}
        other_channels = self.rows(db, 'channels', 'WHERE source=?', ('other',))
        other_source = self.rows(db, 'sources', 'WHERE id=?', ('other',))
        omitted = self.rows(db, 'channels', 'WHERE source=? AND id=?', ('xmltv', 'omitted'))
        save_started = datetime.datetime.now().replace(microsecond=0)
        db._saveChannelListBlock([
            Channel('two', 'Updated two', None, 'new.png', 'new.mp4', False, 8),
            Channel('one', 'Updated one', None, '', '', True, -1),
            Channel('new', 'New channel', None, 'added.png', 'added.mp4', True, -1),
            Channel('explicit', 'Explicit channel', None, None, None, False, 4),
        ])
        self.assertEqual({t: self.rows(db, t) for t in UNCHANGED}, before)
        self.assertEqual(self.rows(db, 'channels', 'WHERE source=?', ('other',)), other_channels)
        self.assertEqual(self.rows(db, 'sources', 'WHERE id=?', ('other',)), other_source)
        self.assertEqual(self.rows(db, 'channels', 'WHERE source=? AND id=?', ('xmltv', 'omitted')), omitted)
        self.assertEqual([tuple(r) for r in db.conn.execute(
            'SELECT id, title, logo, stream_url, visible, weight, lineup FROM channels '
            'WHERE source=? ORDER BY weight', ('xmltv',))], [
                ('one', 'Updated one', '', '', 1, 0, 'Lineup xmltv'),
                ('omitted', 'xmltv/omitted', 'old.png', 'old.mp4', 1, 2, 'Lineup xmltv'),
                ('explicit', 'Explicit channel', None, None, 0, 4, None),
                ('two', 'Updated two', 'new.png', 'new.mp4', 0, 8, 'Lineup xmltv'),
                ('new', 'New channel', 'added.png', 'added.mp4', 1, 9, None),
            ])
        updated = db.conn.execute('SELECT channels_updated FROM sources WHERE id=?',
                                  ('xmltv',)).fetchone()[0]
        self.assertGreaterEqual(updated, save_started)
        self.assertLessEqual(updated, datetime.datetime.now())
        saved = self.rows(db, 'channels')
        db._saveChannelListBlock([])
        self.assertEqual(self.rows(db, 'channels'), saved)
        self.assertEqual({t: self.rows(db, t) for t in UNCHANGED}, before)
        self.assertEqual(db.conn.execute('PRAGMA foreign_key_check').fetchall(), [])
        self.assertFalse(db.conn.in_transaction)


if __name__ == '__main__':
    unittest.main(verbosity=2)
