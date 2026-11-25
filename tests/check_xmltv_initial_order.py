"""Fresh ordering and persisted Beta profiles; real extracted startup/import paths.

Synthetic local XMLTV/M3U, VFS and SQLite only. No Kodi/stub imports or network.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import ast
import datetime
from pathlib import Path
import sqlite3
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import check_xmltv_local_refresh as refresh
from check_xmltv_source_cache import ROOT, extract

KEY = 'xmltv.initial.order'
DATE = datetime.datetime(2026, 11, 20)
XML_ORDER = ['zulu', 'alpha', 'mike']
M3U_ORDER = ['mike', 'zulu', 'alpha', 'playlist-only']


def guide(ids):
    return ('<tv>' + ''.join(
        f'<channel id="{cid}"><display-name>{cid}</display-name></channel>' for cid in ids) +
        ''.join(f'<programme channel="{cid}" start="20261120120000 +0000" '
                f'stop="20261120123000 +0000"><title>{cid} programme</title></programme>'
                for cid in dict.fromkeys(ids)) + '</tv>').encode()


class InitialOrder(unittest.TestCase):
    copy_file = refresh.LocalRefresh.copy_file
    download = refresh.LocalRefresh.download
    reopen = refresh.LocalRefresh.reopen
    update = refresh.LocalRefresh.update
    snapshot = refresh.LocalRefresh.snapshot

    def setUp(self):
        refresh.LocalRefresh.setUp(self)
        self.settings.update({'xmltv2.enabled': 'false', 'xmltv3.enabled': 'false',
                              'mapping.m3u.enabled': 'true', 'mapping.m3u.type': '0',
                              'mapping.m3u.order': 'false'})
        self.inputs[0].write_bytes(guide(XML_ORDER))
        self.playlist = self.profile / 'synthetic.m3u'
        self.settings['mapping.m3u.file'] = str(self.playlist)
        self.write_playlist(M3U_ORDER)
        (self.profile / 'categories.ini').write_text('zulu=Saved category\n')
        self.reopen()
        self.env.update(utils=SimpleNamespace(Channel=self.env['Channel']), debug_log=Mock())
        self.gui_cls = extract('gui.py', 'TVGuide', self.env,
                               {'loadChannelMappings', 'onSourceInitialized'})
        self.db_cls = extract('source.py', 'Database', self.env, {
            '_initialize', '_createTables', '_close', 'adapt_datetime', 'convert_datetime',
            '_wasSettingsChanged', '_isCacheExpired', '_getChannelList', 'getChannelList',
            'saveChannelListBlock', '_saveChannelListBlock', '_saveChannelList',
            '_setCustomStreamUrls', 'setCustomStreamUrls',
            '_updateChannelAndProgramListCaches', '_updateChannelAndProgramListCachesLocked'})

    def write_playlist(self, ids):
        self.playlist.write_text('#EXTM3U\n' + ''.join(
            f'#EXTINF:-1 tvg-id="{cid}",{cid}\nhttps://example.invalid/{cid}\n' for cid in ids))

    def database(self, name='source.db', beta=False):
        db = self.db_cls()
        db.source, db.databasePath = self.source, str(self.profile / name)
        db.conn = None
        db.category, db.channelList = 'Any', []
        db.updateInProgress = db.updateFailed = False
        # Synchronous DB-thread adapter; execute the real public blocking methods.
        db._invokeAndBlockForResult = lambda method, *args: method(*args)
        if beta:
            # Exact published Beta 0.1.2 schema creation, not a hand-copied schema.
            text = subprocess.check_output(['git', 'show', '8fe6ede:source.py'], cwd=ROOT, text=True)
            tree = ast.parse(text)
            cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Database')
            cls.name, cls.bases = 'BetaDatabase', []
            cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_createTables']
            exec(compile(ast.Module(body=[cls], type_ignores=[]), '<exact Beta schema>', 'exec'), self.env)
            db.conn = sqlite3.connect(db.databasePath)
            self.env['BetaDatabase']._createTables(db)
            schema = db.conn.execute('SELECT type,name,sql FROM sqlite_master ORDER BY type,name').fetchall()
            db.conn.close()
        self.assertTrue(db._initialize(None))
        if beta:
            self.assertEqual([tuple(r) for r in db.conn.execute(
                'SELECT type,name,sql FROM sqlite_master ORDER BY type,name')], schema)
        self.addCleanup(db._close)
        return db

    def mappings(self, db):
        gui = self.gui_cls()
        gui.database = db
        gui.loadChannelMappings()
        return gui

    def close_database(self, db):
        db._close()
        db.conn = None

    def order(self, db, exclude=('catchup',)):
        return [c.id for c in db.getChannelList(False, True) if c.id not in exclude]

    def pending(self, db):
        row = db.conn.execute('SELECT value FROM settings WHERE key=?', [KEY]).fetchone()
        return row[0] if row else None

    def channel_rows(self, db):
        return {r['id']: tuple(r) for r in db.conn.execute(
            "SELECT rowid,* FROM channels WHERE source='xmltv'")}

    def assert_healthy(self, db):
        self.assertEqual(db.conn.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(db.conn.execute('PRAGMA foreign_key_check').fetchall(), [])
        self.assertEqual(tuple(db.conn.execute('SELECT * FROM version').fetchone()), (1, 4, 1))
        self.assertFalse(db.conn.in_transaction)

    def test_fresh_explicit_off_xmltv_wins_over_real_m3u_preseed(self):
        db = self.database()
        self.mappings(db)
        self.assertEqual(self.order(db), M3U_ORDER)  # Ensure the defect's prerequisite.
        before = self.channel_rows(db)
        self.update(db)
        self.assertFalse(db.updateFailed)
        self.assertEqual(self.order(db), XML_ORDER + ['playlist-only'])
        self.assertIsNone(self.pending(db))
        after = self.channel_rows(db)
        for cid, row in before.items():
            self.assertEqual(after[cid][:-1], row[:-1])  # rowids/fields except weight
        self.assert_healthy(db)

    def test_fresh_explicit_on_m3u_wins_and_stays_authoritative(self):
        self.settings['mapping.m3u.order'] = 'true'
        db = self.database()
        self.mappings(db)
        before = self.channel_rows(db)
        self.update(db)
        self.assertEqual(self.order(db), M3U_ORDER)
        self.assertEqual({cid: self.channel_rows(db)[cid] for cid in before}, before)
        self.assertIsNone(self.pending(db))
        self.inputs[0].write_bytes(guide(list(reversed(XML_ORDER)) + ['new']))
        self.reopen()
        self.update(db)
        self.assertEqual(self.order(db), M3U_ORDER + ['new'])
        self.mappings(db)
        self.assertEqual(self.order(db), M3U_ORDER + ['new'])
        self.assert_healthy(db)

    def test_failed_initial_import_retries_after_reopen_without_losing_provenance(self):
        db = self.database()
        self.mappings(db)
        before = self.snapshot(db)
        real_parser = self.source.getDataFromExternal

        def broken(*args):
            yield from real_parser(*args)
            raise ValueError('synthetic initial import failure')

        self.source.getDataFromExternal = broken
        self.update(db)
        self.assertTrue(db.updateFailed)
        self.assertEqual(self.snapshot(db), before)
        self.assertEqual(self.pending(db), 'pending')
        self.close_database(db)
        self.reopen()  # Successful producer already persisted; no in-memory reset.
        db = self.database()
        self.mappings(db)  # Another foreground M3U seed must not lose provenance.
        self.update(db)
        self.assertFalse(db.updateFailed)
        self.assertEqual(self.order(db), XML_ORDER + ['playlist-only'])
        after = self.snapshot(db)
        self.close_database(db)
        self.reopen(force=True)
        db = self.database()
        self.update(db)  # Service/restart, same committed XMLTV and no M3U load.
        self.assertEqual(self.snapshot(db), after)
        self.assert_healthy(db)

    def test_interrupted_after_m3u_seed_before_import(self):
        db = self.database()
        self.mappings(db)
        self.close_database(db)
        self.reopen()
        db = self.database()
        self.update(db)  # Service completes a foreground seed after process restart.
        self.assertEqual(self.order(db), XML_ORDER + ['playlist-only'])
        self.assertIsNone(self.pending(db))

    def test_cancel_empty_and_commit_failure_keep_pending_order_and_all_rows(self):
        db = self.database()
        self.mappings(db)
        before = self.snapshot(db)
        real_parser = self.source.getDataFromExternal
        for failure in ('cancel', 'empty', 'commit'):
            with self.subTest(failure=failure):
                def broken(*args):
                    if failure == 'empty':
                        return
                    yield from real_parser(*args)
                    if failure == 'cancel':
                        raise self.env['SourceUpdateCanceledException']()
                    # Deferrable FK fails only at commit, after order/key bookkeeping.
                    yield self.env['Program']('orphan', 'Invalid', '', DATE,
                                              DATE + datetime.timedelta(minutes=30), '', '')
                self.source.getDataFromExternal = broken
                self.update(db)
                self.assertTrue(db.updateFailed)
                self.assertEqual(self.snapshot(db), before)
                self.assertEqual(self.pending(db), 'pending')
        self.source.getDataFromExternal = real_parser
        self.update(db)
        self.assertEqual(self.order(db), XML_ORDER + ['playlist-only'])
        self.assert_healthy(db)

    def test_user_channel_save_before_success_cancels_pending_order(self):
        db = self.database()
        self.mappings(db)
        channels = db.getChannelList(False, True)
        channels[0].weight, channels[0].visible = 42, False
        db._saveChannelList(channels)  # Real channel manager save, not automatic seed.
        before = self.channel_rows(db)
        self.update(db)
        for cid, row in before.items():
            self.assertEqual(self.channel_rows(db)[cid], row)
        self.assertIsNone(self.pending(db))

    def test_membership_append_and_retain_absent_rows_after_first_success(self):
        db = self.database()
        self.mappings(db)
        self.update(db)
        before = self.channel_rows(db)
        self.inputs[0].write_bytes(guide(['new-b', 'mike', 'new-a', 'zulu']))
        self.reopen()
        self.update(db)
        self.assertEqual(self.order(db), XML_ORDER + ['playlist-only', 'new-b', 'new-a'])
        for cid, row in before.items():
            self.assertEqual(self.channel_rows(db)[cid], row)
        self.assertFalse(db.conn.execute("SELECT 1 FROM programs WHERE channel='alpha'").fetchone())
        self.write_playlist(['playlist-new', 'mike'])
        self.mappings(db)
        self.assertEqual(self.order(db), XML_ORDER + ['playlist-only', 'new-b', 'new-a', 'playlist-new'])
        self.assert_healthy(db)

    def test_beta_customized_hidden_profile_and_unknown_existing_db_never_reorder(self):
        for history in ('populated', 'empty-history'):
            with self.subTest(history=history):
                db = self.database(history + '.db', beta=True)
                self.assertIsNone(self.pending(db))
                self.mappings(db)
                if history == 'populated':
                    self.update(db)
                # Published Beta has no #92 successful-import key or new provenance.
                db.conn.execute("DELETE FROM settings WHERE key='xmltv.imported.cache'")
                db.conn.execute("UPDATE channels SET weight=42,visible=0,lineup='Saved category' WHERE id='zulu'")
                db.conn.execute("INSERT INTO custom_stream_url VALUES ('manual-only','fixture://manual')")
                db.conn.execute("INSERT INTO alt_custom_stream_url VALUES ('zulu','Alternate','fixture://alt')")
                for table in ('notifications', 'autoplays', 'autoplaywiths'):
                    db.conn.execute('INSERT INTO ' + table + ' VALUES (?,?,?,?,?)',
                                    ['zulu', 'zulu programme', 'xmltv', DATE, '1'])
                db.conn.commit()
                before = self.snapshot(db)
                channels = self.channel_rows(db)
                categories = (self.profile / 'categories.ini').read_bytes()
                self.close_database(db)
                self.reopen(force=True)
                db = self.database(history + '.db')
                for iteration in range(3):
                    self.mappings(db)
                    self.update(db)
                    current = self.channel_rows(db)
                    self.assertEqual({cid: current[cid] for cid in channels}, channels)
                    self.assertLessEqual(set(current) - set(channels), {'catchup'})
                    after = self.snapshot(db)
                    for table in ('custom_stream_url', 'alt_custom_stream_url',
                                  'notifications', 'autoplays', 'autoplaywiths'):
                        self.assertEqual(sorted(after[table]), sorted(before[table]), table)
                    self.assertEqual((self.profile / 'categories.ini').read_bytes(), categories)
                    self.assertIsNone(self.pending(db))
                self.assert_healthy(db)

    def test_real_foreground_and_service_callbacks_both_startup_orders(self):
        for first, explicit in (('foreground', False), ('service', False),
                                ('foreground', True), ('service', True)):
            with self.subTest(first=first, explicit=explicit):
                self.settings['mapping.m3u.order'] = str(explicit).lower()
                db = self.database(first + str(explicit) + '.db')
                db.initialize = lambda callback, *args: callback(True)
                db.updateChannelAndProgramListCaches = lambda callback: (self.update(db), callback())
                db.close = Mock()  # Keep fixture connection available for assertions.
                db.exportChannelList = db.exportChannelIdList = Mock()
                self.addon.getAddonInfo = lambda key: 'inert-addon-path'
                scheduler = SimpleNamespace(scheduleNotifications=Mock(), scheduleAutoplays=Mock())
                self.env.update(Notification=lambda *args: scheduler, Autoplay=lambda *args: scheduler)
                gui = self.gui_cls()
                gui.database = db
                gui.clear_catchup = Mock()
                gui.channelIdx, gui.viewStartDate = 0, DATE
                gui.onRedrawEPG = lambda *args: self.update(db)
                env = dict(self.env, source=SimpleNamespace(Database=lambda force: db),
                           notification=SimpleNamespace(Notification=lambda *args: scheduler),
                           autoplay=SimpleNamespace(Autoplay=lambda *args: scheduler))
                service = extract('service.py', 'Service', env)
                env['xbmc'].LOGINFO = 1
                foreground = lambda: gui.onSourceInitialized(True)
                background = lambda: service()
                (foreground if first == 'foreground' else background)()
                foreground()
                background()
                self.assertEqual(self.order(db), M3U_ORDER if explicit else XML_ORDER + ['playlist-only'])
                after = self.snapshot(db)
                after.pop('sources')  # M3U saves legitimately advance channels_updated.
                foreground()
                background()
                current = self.snapshot(db)
                self.assertEqual([r[0] for r in current.pop('sources')], ['xmltv'])
                self.assertEqual(current, after)
                self.assert_healthy(db)

    def test_service_import_between_m3u_read_and_seed_cannot_restore_stale_weights(self):
        db = self.database()
        self.mappings(db)
        invoke = db._invokeAndBlockForResult
        def interleave(method, *args):
            if method.__name__ == '_saveChannelListBlock':
                self.update(db)  # Foreground has already read the old M3U weights.
            return invoke(method, *args)
        db._invokeAndBlockForResult = interleave
        self.mappings(db)
        self.assertEqual(self.order(db), XML_ORDER + ['playlist-only'])
        self.assertIsNone(self.pending(db))
        self.assert_healthy(db)

    def test_merged_declarations_first_seen_order_and_stable_undeclared_tail(self):
        self.settings.update({'xmltv2.enabled': 'true', 'xmltv2.offset': '0'})
        self.inputs[0].write_bytes(guide(['zulu', 'alpha']))
        # Duplicate declaration has no second event/UNIQUE collision.
        self.inputs[1].write_bytes(guide(['bravo', 'mike']).replace(
            b'<tv>', b'<tv><channel id="alpha"><display-name>alpha</display-name></channel>'))
        self.write_playlist(['playlist-tail-2', 'mike', 'playlist-tail-1', 'alpha'])
        self.reopen()
        db = self.database()
        self.mappings(db)
        self.update(db)
        self.assertEqual(self.order(db), ['zulu', 'alpha', 'bravo', 'mike',
                                          'playlist-tail-2', 'playlist-tail-1'])
        self.assert_healthy(db)

    def test_non_xmltv_source_does_not_gain_marker_or_change_save_policy(self):
        self.source.KEY = 'fixture-other'
        db = self.database()
        self.assertIsNone(self.pending(db))
        channel = self.env['Channel']('one', 'Original', '', '', 'fixture://stream', True, 5)
        db.saveChannelListBlock([channel], initial_m3u=True)
        channel.weight, channel.visible = 9, False
        db.saveChannelListBlock([channel], initial_m3u=True)
        self.assertEqual([tuple(row) for row in db.conn.execute(
            'SELECT id,visible,weight FROM channels')], [('one', 0, 9)])
        self.assertIsNone(self.pending(db))
        self.assert_healthy(db)

    def test_process_exit_during_first_import_keeps_committed_seed_provenance(self):
        # Real OS process exit with an open import transaction, no finally/close.
        # The child's caches are disposable; only its committed DB is shared here.
        script = """
import os, sys, tempfile
from check_xmltv_initial_order import InitialOrder
tempfile.tempdir = sys.argv[2]
t = InitialOrder()
t.setUp()
db = t.database(sys.argv[1])
t.mappings(db)
parser = t.source.getDataFromExternal
def interrupted(*args):
    yield from parser(*args)
    os._exit(0)
t.source.getDataFromExternal = interrupted
t.update(db)
raise AssertionError('import did not reach interruption')
"""
        result = subprocess.run([sys.executable, '-c', script, str(self.profile / 'source.db'), str(self.profile)],
                                cwd=ROOT / 'tests', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        db = self.database()
        self.assertEqual(self.pending(db), 'pending')
        self.assertEqual(self.order(db), M3U_ORDER)
        self.assertEqual(db.conn.execute('SELECT count(*) FROM programs').fetchone()[0], 0)
        self.update(db)
        self.assertFalse(db.updateFailed)
        self.assertEqual(self.order(db), XML_ORDER + ['playlist-only'])
        self.assertIsNone(self.pending(db))
        self.assert_healthy(db)


if __name__ == '__main__':
    if '--baseline' in sys.argv:
        sys.argv.remove('--baseline')
        original = Path.read_text
        def baseline(path, *args, **kwargs):
            if path in (ROOT / 'source.py', ROOT / 'gui.py'):
                return subprocess.check_output(['git', 'show', '548b674:' + path.name], cwd=ROOT, text=True)
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', baseline):
            unittest.main(verbosity=2)
    else:
        unittest.main(verbosity=2)
