"""Issue #85: actual fetch/parser/schema/importer, synthetic VFS and SQLite only.

No Kodi imports, real network, user profiles or duplicated refresh logic.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import datetime
import ast
import gzip
from html import entities
from itertools import chain
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import unittest
from unittest.mock import Mock
from unittest.mock import patch
import xml.etree.ElementTree as ET

import check_xmltv_source_cache as cache_tests
from check_xmltv_source_cache import VFSFile, extract


def feed(slot, changed=False):
    events = [('Old', '1200', '1230'), ('Removed', '1230', '1300')]
    if changed:
        events = [('New', '1205', '1240'), ('Added', '1240', '1310')]
    return (f'<tv><channel id="{slot}"><display-name>{slot}</display-name></channel>' +
            ''.join(f'<programme channel="{slot}" start="20261120{start}00 +0000" '
                    f'stop="20261120{stop}00 +0000"><title>{title}</title>'
                    '<category>Fixture</category></programme>'
                    for title, start, stop in events) + '</tv>').encode()


class LocalRefresh(unittest.TestCase):
    copy_file = cache_tests.SourceCache.copy_file
    download = cache_tests.SourceCache.download

    def setUp(self):
        cache_tests.SourceCache.setUp(self)
        self.settings.update({'xmltv.type': '0', 'xmltv2.type': '0', 'xmltv3.type': '0',
                              'logos.source': '0', 'xmltv.offset': '0',
                              'xmltv2.offset': '-45', 'xmltv3.offset': '90',
                              'xmltv2.enabled': 'true', 'xmltv3.enabled': 'true',
                              'xmltv.keep.channels': 'false', 'logos.keep': 'true'})
        self.env.update(sqlite3=sqlite3, ElementTree=ET, re=re, chain=chain,
                        is_meta_catchup=lambda value: False, log=Mock(),
                        NO_DESCRIPTION=0,
                        SourceUpdateCanceledException=type('Canceled', (Exception,), {}),
                        SourceNotConfiguredException=type('NotConfigured', (Exception,), {}))
        tree = ast.parse((cache_tests.ROOT / 'source.py').read_text())
        unescape = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'unescape2')
        self.env['htmlentitydefs'] = entities
        exec(compile(ast.Module(body=[unescape], type_ignores=[]), '<real entity repair>', 'exec'), self.env)
        prefix = 'special://profile/addon_data/script.tvguide.fullscreen/'

        def local_path(path):
            return str(self.profile / path[len(prefix):]) if str(path).startswith(prefix) else path

        class File(VFSFile):
            def __init__(self, path, mode='r'):
                super().__init__(local_path(path), mode)

        self.env['xbmcvfs'].File = File
        self.env['xbmcvfs'].exists = lambda path: os.path.exists(local_path(path))
        self.env['xbmcvfs'].delete = lambda path: Path(local_path(path)).unlink(missing_ok=True)
        self.env['xbmcvfs'].translatePath = local_path
        self.env['FileWrapper'] = extract('source.py', 'FileWrapper', self.env)
        for name in ('Channel', 'Program'):
            self.env[name] = extract('utils.py', name, self.env)
        # All XMLTV methods, including constructor, routing and actual parser.
        self.env['Source'] = object
        self.source_cls = extract('source.py', 'XMLTVSource', self.env)
        self.source_cls.PLUGIN_DATA = str(self.profile)
        self.inputs = []
        for slot in ('xmltv', 'xmltv2', 'xmltv3'):
            path = self.profile / (slot + '-input.xml')
            path.write_bytes(feed(slot))
            self.inputs.append(path)
            self.settings[slot + '.file'] = str(path)
        self.reopen()

    def reopen(self, force=False):
        self.source = self.source_cls(self.addon, force)

    def rows(self):
        return [(row.channel, row.title, row.startDate, row.endDate)
                for row in self.source.getDataFromExternal(datetime.datetime(2026, 11, 20), [])
                if isinstance(row, self.env['Program'])]

    def database(self):
        cls = extract('source.py', 'Database', self.env, {
            '_createTables', 'adapt_datetime', 'convert_datetime', '_isCacheExpired',
            '_updateChannelAndProgramListCaches', '_updateChannelAndProgramListCachesLocked',
            'getEPGView', 'getQuickEPGView'})
        sqlite3.register_adapter(datetime.datetime, cls.adapt_datetime)
        sqlite3.register_converter('timestamp', cls.convert_datetime)
        db = cls()
        db.conn = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
        self.addCleanup(db.conn.close)
        db.conn.row_factory = sqlite3.Row
        db.conn.execute('PRAGMA foreign_keys=ON')
        db.source = self.source
        db._createTables()
        db.settingsChanged = False
        db._getChannelList = Mock(return_value=[])
        db.updateInProgress = db.updateFailed = False
        return db

    def update(self, db):
        db.source = self.source
        db._updateChannelAndProgramListCaches(datetime.datetime(2026, 11, 20), None, True)

    def snapshot(self, db):
        return {row[0]: [tuple(r) for r in db.conn.execute('SELECT * FROM "' + row[0] + '"')]
                for row in db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}

    def test_same_path_changes_each_slot_with_new_equal_and_older_mtimes(self):
        db = self.database()
        for index in range(3):
            for stamp in ('new', 'equal', 'older'):
                with self.subTest(slot=index, timestamp=stamp):
                    path = self.inputs[index]
                    path.write_bytes(feed(('xmltv', 'xmltv2', 'xmltv3')[index]))
                    self.reopen(force=True)
                    self.update(db)
                    before = self.rows()
                    cached = self.profile / ('xmltv', 'xmltv2', 'xmltv3')[index]
                    cache_time = os.path.getmtime(str(cached) + '.xml')
                    path.write_bytes(feed(('xmltv', 'xmltv2', 'xmltv3')[index], True))
                    when = {'new': cache_time + 10, 'equal': cache_time, 'older': 1}[stamp]
                    os.utime(path, (when, when))
                    self.reopen()
                    after = self.rows()
                    print('same path slot=', index, 'mtime=', stamp,
                          'titles=', [r[1] for r in after[index * 2:index * 2 + 2]])
                    self.assertEqual([r[1] for r in after[index * 2:index * 2 + 2]], ['New', 'Added'])
                    self.assertNotEqual(after[index * 2][2:], before[index * 2][2:])
                    self.assertEqual(after[:index * 2], before[:index * 2])
                    self.assertEqual(after[index * 2 + 2:], before[index * 2 + 2:])
                    self.update(db)
                    self.assertFalse(db.updateFailed)
                    actual = [tuple(row) for row in db.conn.execute(
                        "SELECT channel,title,start_date,end_date FROM programs WHERE source='xmltv' "
                        "AND title NOT IN ('?', '-') ORDER BY channel,start_date")]
                    self.assertEqual(actual, sorted(after, key=lambda row: (row[0], row[2])))

    def test_unchanged_local_does_not_replace_or_import(self):
        db = self.database()
        self.update(db)
        for slot in ('xmltv', 'xmltv2', 'xmltv3'):
            os.utime(self.profile / (slot + '.xml'), (1, 1))
        before = self.snapshot(db)
        mtimes = [os.stat(self.profile / (slot + '.xml')).st_mtime_ns
                  for slot in ('xmltv', 'xmltv2', 'xmltv3')]
        self.reopen()
        self.update(db)
        self.assertEqual(self.snapshot(db), before)
        self.assertFalse(self.source.needReset)
        self.assertEqual([os.stat(self.profile / (slot + '.xml')).st_mtime_ns
                          for slot in ('xmltv', 'xmltv2', 'xmltv3')], mtimes)

    def test_malformed_cache_keeps_last_good_and_retries(self):
        path = self.inputs[1]
        good = (self.profile / 'xmltv2.xml').read_bytes()
        path.write_bytes(feed('xmltv2', True)[:-5])
        self.reopen(force=True)
        self.assertEqual((self.profile / 'xmltv2.xml').read_bytes(), good)
        path.write_bytes(feed('xmltv2', True))
        os.utime(path, (1, 1))
        self.reopen()
        self.assertEqual((self.profile / 'xmltv2.xml').read_bytes(), feed('xmltv2', True))

    def test_enabled_secondary_cache_is_checked_without_need_reset(self):
        db = self.database()
        self.update(db)
        self.source.needReset = False
        os.utime(self.profile / 'xmltv.xml', (1, 1))
        path = self.profile / 'xmltv3.xml'
        path.write_bytes(feed('xmltv3', True))
        # The imported content, not the wall clock, must establish freshness.
        os.utime(path, (1, 1))
        self.assertTrue(db._isCacheExpired(datetime.datetime(2026, 11, 20)))

    def test_import_failure_after_10000_items_keeps_entire_database(self):
        db = self.database()
        self.update(db)
        before = self.snapshot(db)
        real_parser = self.source.getDataFromExternal

        def broken(*args):
            rows = list(real_parser(*args))
            rows[1].title = 'Uncommitted replacement'
            for index in range(10001):
                yield rows[index % len(rows)]
            raise ValueError('deterministic late parser failure')

        self.source.getDataFromExternal = broken
        self.source.needReset = True
        self.update(db)
        self.assertTrue(db.updateFailed)
        self.assertEqual(self.snapshot(db), before)
        self.assertFalse((self.profile / 'db.lock').exists())
        self.source.getDataFromExternal = real_parser
        self.update(db)
        self.assertFalse(db.updateFailed)

    def test_refresh_preserves_rules_mappings_channels_settings_and_other_source(self):
        db = self.database()
        self.update(db)
        conn = db.conn
        conn.execute("UPDATE channels SET visible=0, weight=42, lineup='Saved category', "
                     "stream_url='automatic.mp4' WHERE id='xmltv'")
        conn.execute("INSERT INTO custom_stream_url VALUES ('xmltv', 'manual.mp4')")
        conn.execute("INSERT INTO alt_custom_stream_url VALUES ('xmltv', 'Alternate', 'alternate.mp4')")
        for table in ('notifications', 'autoplays', 'autoplaywiths'):
            conn.execute('INSERT INTO ' + table + ' VALUES (?, ?, ?, ?, ?)',
                         ['xmltv', 'Old', 'xmltv', datetime.datetime(2026, 11, 20, 12), '1'])
        conn.execute('INSERT INTO sources VALUES (?, ?)', ['other', datetime.datetime(2026, 11, 20)])
        conn.execute('INSERT INTO updates(source,date,programs_updated) VALUES (?, ?, ?)',
                     ['other', '2026-11-21', datetime.datetime(2026, 11, 21)])
        update_id = conn.execute("SELECT id FROM updates WHERE source='other'").fetchone()[0]
        conn.execute("INSERT INTO channels VALUES ('xmltv','Other','other.png','other.mp4','other','Other group',1,5)")
        conn.execute('INSERT INTO programs(channel,title,start_date,end_date,source,updates_id) VALUES (?, ?, ?, ?, ?, ?)',
                     ['xmltv', 'Other programme', datetime.datetime(2026, 11, 21, 12),
                      datetime.datetime(2026, 11, 21, 13), 'other', update_id])
        conn.execute("INSERT INTO settings VALUES ('preserve.me', 'unchanged')")
        conn.commit()
        before = self.snapshot(db)
        self.inputs[0].write_bytes(feed('xmltv', True))
        self.reopen()
        db.settingsChanged = True  # Also protect the legacy refresh-ON path.
        self.update(db)
        self.assertFalse(db.updateFailed)
        after = self.snapshot(db)
        for table in ('channels', 'custom_stream_url', 'alt_custom_stream_url',
                      'notifications', 'autoplays', 'autoplaywiths'):
            self.assertEqual(after[table], before[table], table)
        for table, column in (('programs', 'source'), ('updates', 'source'), ('sources', 'id')):
            before_other = [row for row in before[table] if 'other' in row]
            after_other = [tuple(row) for row in conn.execute(
                'SELECT * FROM ' + table + ' WHERE ' + column + '=?', ['other'])]
            self.assertEqual(after_other, before_other, table)
        self.assertEqual(conn.execute("SELECT value FROM settings WHERE key='preserve.me'").fetchone()[0], 'unchanged')
        self.assertEqual([row[0] for row in conn.execute(
            "SELECT title FROM programs WHERE source='xmltv' AND channel='xmltv' ORDER BY start_date")], ['New', 'Added'])
        self.assertEqual(conn.execute('PRAGMA foreign_key_check').fetchall(), [])
        self.assertEqual(conn.execute('PRAGMA integrity_check').fetchone()[0], 'ok')

    def test_vfs_uri_without_stat_and_gzip_older_content(self):
        uri = 'smb://synthetic/guide.xml.gz'
        self.settings['xmltv.file'] = uri
        self.inputs[0].write_bytes(gzip.compress(feed('xmltv', True)))
        self.copy.side_effect = lambda source, target: self.copy_file(
            str(self.inputs[0]) if source == uri else source, target)
        os.utime(self.inputs[0], (1, 1))
        self.reopen()
        self.assertEqual(self.cache.read_bytes(), feed('xmltv', True))
        self.assertEqual([row[1] for row in self.rows()[:2]], ['New', 'Added'])
        self.requests.get.assert_not_called()
        before = self.cache.stat().st_mtime_ns
        self.reopen(force=True)
        self.assertEqual(self.cache.stat().st_mtime_ns, before)
        self.assertFalse(self.source.needReset)

    def test_missing_and_model_malformed_sources_preserve_cache_and_retry(self):
        db = self.database()
        self.update(db)
        database_before = self.snapshot(db)
        path = self.inputs[0]
        good, binding = self.cache.read_bytes(), Path(str(self.cache) + '.source').read_bytes()
        for failure in ('missing', 'syntax', 'model', 'wrong-root', 'empty'):
            with self.subTest(failure=failure):
                if failure == 'missing':
                    path.unlink()
                else:
                    path.write_bytes({'syntax': b'<tv><channel', 'model': b'<tv><channel/></tv>',
                                      'wrong-root': b'<html/>', 'empty': b'<tv/>'}[failure])
                self.reopen(force=True)
                self.assertEqual(self.cache.read_bytes(), good)
                self.assertEqual(Path(str(self.cache) + '.source').read_bytes(), binding)
                self.update(db)
                self.assertEqual(self.snapshot(db), database_before)
                path.write_bytes(good)
        path.write_bytes(feed('xmltv', True))
        self.reopen()
        self.assertEqual(self.cache.read_bytes(), feed('xmltv', True))

    def test_secondary_and_tertiary_enabled_alone_refresh_independently(self):
        db = self.database()
        for enabled, index, slot in ((('true', 'false'), 1, 'xmltv2'),
                                     (('false', 'true'), 2, 'xmltv3')):
            with self.subTest(slot=slot):
                self.settings['xmltv2.enabled'], self.settings['xmltv3.enabled'] = enabled
                self.reopen()
                self.update(db)
                primary = [row for row in self.rows() if row[0] == 'xmltv']
                self.inputs[index].write_bytes(feed(slot, True))
                os.utime(self.inputs[index], (1, 1))
                self.reopen()
                self.update(db)
                self.assertFalse(db.updateFailed)
                self.assertEqual([row[0] for row in db.conn.execute(
                    "SELECT title FROM programs WHERE source='xmltv' AND channel=? ORDER BY start_date", [slot])],
                                 ['New', 'Added'])
                self.assertEqual([row for row in self.rows() if row[0] == 'xmltv'], primary)

    def test_legacy_entity_repair_is_staged_and_unchanged_cache_is_not_rewritten(self):
        self.settings['xmltv.and'] = 'true'
        self.inputs[0].write_bytes(feed('xmltv').replace(b'Old', b'News & weather'))
        self.reopen()
        self.assertIn(b'News &amp; weather', self.cache.read_bytes())
        before = self.cache.read_bytes(), self.cache.stat().st_mtime_ns
        self.reopen()
        self.assertEqual((self.cache.read_bytes(), self.cache.stat().st_mtime_ns), before)
        self.inputs[0].write_bytes(b'<tv><channel id="broken">')
        self.reopen()
        self.assertEqual((self.cache.read_bytes(), self.cache.stat().st_mtime_ns), before)

    def test_fetch_and_import_serialize_without_stealing_locks_and_retry(self):
        db = self.database()
        self.update(db)
        before = self.snapshot(db)
        self.inputs[0].write_bytes(feed('xmltv', True))
        lock = self.fetcher.acquireXMLTVLock()
        try:
            self.reopen()
            self.assertEqual(self.cache.read_bytes(), feed('xmltv'))
            self.source.needReset = True
            self.update(db)
            self.assertEqual(self.snapshot(db), before)
            with self.assertRaises(sqlite3.OperationalError):
                self.fetcher.acquireXMLTVLock()
        finally:
            lock.close()
        self.reopen()
        self.update(db)
        self.assertFalse(db.updateFailed)
        self.assertEqual(self.cache.read_bytes(), feed('xmltv', True))
        # Import holds the same lock throughout parsing/commit. A constructor
        # interleaved by its progress callback must not replace active bytes.
        self.inputs[0].write_bytes(feed('xmltv'))
        self.source.needReset = True
        def interleave(percent):
            self.source.updateLocalFile('xmltv.xml', str(self.inputs[0]), self.addon)
            self.assertEqual(self.cache.read_bytes(), feed('xmltv', True))
            return True
        db._updateChannelAndProgramListCaches(datetime.datetime(2026, 11, 20), interleave, True)
        self.assertFalse(db.updateFailed)
        self.reopen()
        self.assertEqual(self.cache.read_bytes(), feed('xmltv'))

    def test_cancellation_empty_import_and_sql_failure_keep_last_good_view(self):
        db = self.database()
        self.update(db)
        before = self.snapshot(db)
        real_parser = self.source.getDataFromExternal
        for failure in ('cancel', 'empty', 'sql'):
            with self.subTest(failure=failure):
                def broken(*args):
                    if failure == 'cancel':
                        yield next(real_parser(*args))
                        raise self.env['SourceUpdateCanceledException']()
                    if failure == 'sql':
                        yield from real_parser(*args)
                self.source.getDataFromExternal = broken
                self.source.needReset = True
                if failure == 'sql':
                    db.conn.set_authorizer(lambda action, table, *rest:
                                           sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_INSERT
                                           and table == 'programs' else sqlite3.SQLITE_OK)
                try:
                    self.update(db)
                finally:
                    db.conn.set_authorizer(None)
                self.assertTrue(db.updateFailed)
                self.assertEqual(self.snapshot(db), before)
                self.assertFalse((self.profile / 'db.lock').exists())
                retained_view = [0, ['retained channel'], ['retained programme']]
                db._invokeAndBlockForResult = lambda *args: retained_view
                db._getEPGView = db._getQuickEPGView = Mock()
                self.assertEqual(db.getEPGView(0), retained_view)
                self.assertEqual(db.getQuickEPGView(0), retained_view)
                self.source.getDataFromExternal = real_parser
        self.update(db)
        self.assertFalse(db.updateFailed)

    def test_freshness_invalidation_and_enabled_slots(self):
        db = self.database()
        self.update(db)
        self.source.needReset = False
        self.assertFalse(db._isCacheExpired(datetime.datetime(2026, 11, 20)))
        self.settings['xmltv3.enabled'] = 'false'
        self.reopen()
        self.update(db)
        self.assertFalse(db._isCacheExpired(datetime.datetime(2026, 11, 20)))
        (self.profile / 'xmltv3.xml').write_bytes(feed('xmltv3', True))
        self.assertFalse(db._isCacheExpired(datetime.datetime(2026, 11, 20)))
        db.conn.execute("UPDATE sources SET channels_updated=0 WHERE id='xmltv'")
        db.conn.commit()
        self.assertTrue(db._isCacheExpired(datetime.datetime(2026, 11, 20)))

    def test_same_time_other_source_collision_rolls_back_instead_of_replacing(self):
        db = self.database()
        self.update(db)
        self.inputs[0].write_bytes(feed('xmltv', True))
        self.reopen()
        programme = self.rows()[0]
        conn = db.conn
        conn.execute('INSERT INTO sources VALUES (?, ?)', ['other', datetime.datetime(2026, 11, 20)])
        conn.execute("INSERT INTO channels VALUES ('xmltv','Other',NULL,NULL,'other',NULL,1,0)")
        conn.execute('INSERT INTO updates(source,date,programs_updated) VALUES (?, ?, ?)',
                     ['other', '2026-11-20', datetime.datetime(2026, 11, 20)])
        update_id = conn.execute("SELECT id FROM updates WHERE source='other'").fetchone()[0]
        conn.execute('INSERT INTO programs(channel,title,start_date,end_date,source,updates_id) VALUES (?, ?, ?, ?, ?, ?)',
                     ['xmltv', 'Protected collision', programme[2], programme[3], 'other', update_id])
        conn.commit()
        before = self.snapshot(db)
        self.update(db)
        self.assertTrue(db.updateFailed)
        self.assertEqual(self.snapshot(db), before)


if __name__ == '__main__':
    if '--baseline' in sys.argv:
        # Fixed reviewed Beta revision only; no checkout, files or Kodi imports.
        sys.argv.remove('--baseline')
        real_read = Path.read_text
        def baseline_read(path, *args, **kwargs):
            if path in (cache_tests.ROOT / 'source.py', cache_tests.ROOT / 'fileFetcher.py'):
                return subprocess.check_output(['git', 'show', '0c4a3c3:' + path.name],
                                               cwd=cache_tests.ROOT, text=True)
            return real_read(path, *args, **kwargs)
        with patch.object(Path, 'read_text', baseline_read):
            unittest.main(verbosity=2)
    else:
        unittest.main(verbosity=2)
