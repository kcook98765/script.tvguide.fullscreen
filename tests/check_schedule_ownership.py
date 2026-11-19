"""Actual AST database/producers, real SQLite; no Kodi or legacy module imports.

--baseline executes the pinned PR20 methods and asserts the observed defects.
All profiles, commands and notification deliveries are disposable inert captures.
"""
import ast
import datetime
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = 'd210c1cd199b8c28cb57ec901da98f07ba9b8205'
BASELINE = '--baseline' in sys.argv
if BASELINE:
    sys.argv.remove('--baseline')


def text(path):
    if BASELINE:
        result = subprocess.run(['git', 'show', BASE + ':' + path], cwd=ROOT,
                                capture_output=True, text=True, check=True)
        return result.stdout
    return (ROOT / path).read_text()


def extract(path, names, env, owner=None):
    tree = ast.parse(text(path))
    body = tree.body if owner is None else next(n.body for n in tree.body
                                               if isinstance(n, ast.ClassDef) and n.name == owner)
    nodes = [n for n in body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names]
    # Staticmethod decorators belong to the class, not the extracted functions.
    for node in nodes:
        if isinstance(node, ast.FunctionDef):
            node.decorator_list = []
    exec(compile(ast.Module(body=nodes, type_ignores=[]), path + ':extracted', 'exec'), env)
    return env


def pure(name):
    env = {}
    exec(compile(text(name + '.py'), name + '.py:pure', 'exec'), env)
    return SimpleNamespace(**env)


safe, reminders, autoplay = pure('command_safety'), pure('reminder_data'), pure('autoplay_data')
models = extract('utils.py', ['Channel', 'Program'], dict(re=re))
NOW = datetime.datetime.now().replace(microsecond=0)
START = NOW + datetime.timedelta(days=1)


class Ownership(unittest.TestCase):
    def setUp(self):
        names = ['adapt_datetime', 'convert_datetime', '_getFullNotifications', '_getFullAutoplays',
                 '_addNotification', '_removeNotification', '_clearAllNotifications',
                 '_addAutoplay', '_removeAutoplay', '_clearAllAutoplays', '_getAutoplayAlarmIdentities']
        self.env = extract('source.py', names, dict(datetime=datetime, time=time, **models), 'Database')
        sqlite3.register_adapter(datetime.datetime, self.env['adapt_datetime'])
        sqlite3.register_converter('timestamp', self.env['convert_datetime'])
        self.conn = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
        self.addCleanup(self.conn.close)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('CREATE TABLE channels(id TEXT, title TEXT, lineup TEXT, logo TEXT, '
                          'stream_url TEXT, source TEXT, visible BOOLEAN, weight INTEGER, PRIMARY KEY(id,source))')
        self.conn.execute('CREATE TABLE programs(channel TEXT, title TEXT, sub_title TEXT, '
                          'start_date TIMESTAMP, end_date TIMESTAMP, description TEXT, categories TEXT, '
                          'image_large TEXT, image_small TEXT, season TEXT, episode TEXT, is_new TEXT, '
                          'is_movie TEXT, language TEXT, source TEXT, UNIQUE(channel,start_date,end_date))')
        for table in ('notifications', 'autoplays'):
            self.conn.execute('CREATE TABLE ' + table + '(channel TEXT, program_title TEXT, source TEXT, '
                              'start_date TIMESTAMP, type TEXT)')
        self.db = SimpleNamespace(conn=self.conn, source=SimpleNamespace(KEY='active'))
        self.db.getAutoplayAlarmIdentities = lambda: self.env['_getAutoplayAlarmIdentities'](self.db)
        for public, private in [('getFullNotifications', '_getFullNotifications'),
                                ('getFullAutoplays', '_getFullAutoplays')]:
            setattr(self.db, public, lambda name=private: self.env[name](self.db, 5))
        for public, private in [('addNotification', '_addNotification'), ('removeNotification', '_removeNotification'),
                                ('clearAllNotifications', '_clearAllNotifications'), ('addAutoplay', '_addAutoplay'),
                                ('removeAutoplay', '_removeAutoplay'), ('clearAllAutoplays', '_clearAllAutoplays')]:
            setattr(self.db, public, lambda *args, name=private: self.env[name](self.db, *args))
        for source in ('active', 'other'):
            for channel in ('one', 'two'):
                self.conn.execute('INSERT INTO channels VALUES(?,?,?,?,?,?,?,?)',
                                  (channel, source + '/' + channel, source, '', '', source, 1, 0))
                self.event(channel, source)

    def event(self, channel='one', source='active', start=START, new='New', title='Show'):
        self.conn.execute('INSERT INTO programs VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                          (channel, title, '', start, start + datetime.timedelta(minutes=30 if source == 'active' else 31), '', '',
                           '', '', '', '', new, '', 'en', source))

    def rule(self, table, kind, title='Show', source='active'):
        self.conn.execute('INSERT INTO ' + table + ' VALUES(?,?,?,?,?)', ('one', title, source, START, kind))

    def rows(self, table):
        method = '_getFullNotifications' if table == 'notifications' else '_getFullAutoplays'
        return self.env[method](self.db, 5)

    def test_ordinary_ownership_and_actual_timestamp_semantics(self):
        raw = self.conn.execute('SELECT typeof(start_date), start_date FROM programs').fetchone()
        self.assertEqual(raw[0], 'integer')
        self.assertEqual(raw[1], START)
        for table in ('notifications', 'autoplays'):
            for kind in (0, 1, 2, 3):
                self.rule(table, kind)
                rows = self.rows(table)
                observed = [(p.channel.title, p.channel.lineup) for p in rows]
                print(('BEFORE' if BASELINE else 'AFTER'), table, kind, observed)
                if BASELINE:
                    self.assertEqual(len(rows), 0 if kind == 2 else 8)
                    if kind != 2:
                        self.assertTrue(any(p.channel.title == 'other/two' for p in rows))
                else:
                    self.assertEqual(observed, [('active/one', 'active')])
                    if table == 'autoplays':
                        self.assertEqual([tuple(r) for r in self.db.getAutoplayAlarmIdentities()],
                                         [('one', 'Show', START, 'active')])
                self.conn.execute('DELETE FROM ' + table)
            self.rule(table, 0, source='other')
            self.assertEqual(len(self.rows(table)), 8 if BASELINE else 0)

    @unittest.skipIf(BASELINE, 'scoped identity / legacy retention regression, not baseline behavior')
    def test_scoped_digest_boundaries_and_safe_legacy_pending_reminder(self):
        # Components cannot borrow delimiter bytes from their neighbours.
        names = {safe.alarm_name('notification', 'Show', START, channel, source)
                 for channel, source in [('one', 'active'), ('two', 'active'), ('one', 'other'),
                                         ('one\nactive', ''), ('one', '\nactive')]}
        self.assertEqual(len(names), 5)
        self.assertTrue(all(re.fullmatch(r'tvguide-notification-[0-9a-f]{64}', n) for n in names))
        with tempfile.TemporaryDirectory(prefix='tvguide-legacy-') as profile:
            store = reminders.ReminderData(profile)
            n = self.scheduler('notification', store)
            self.rule('notifications', 0)
            p = self.rows('notifications')[0]
            legacy = safe.alarm_name('notification', p.title, p.startDate)
            token = store.save(legacy, 'Original title', 'Original early', 'Original now',
                               'Original icon', START.timestamp())
            store.take(token, '5mins', START.timestamp() - 300)
            original = store._read(reminders.event_key(legacy))
            n.scheduleNotifications()
            self.assertEqual(store._read(reminders.event_key(legacy)), original)
            self.assertEqual(store.names(), [legacy])
            self.assertIsNone(store.take(token, '5mins', START.timestamp()))
            # A past start cannot be newly scheduled, but pending old data survives
            # and remains deliverable arbitrarily late. No automatic migration/expiry.
            past = NOW - datetime.timedelta(days=2)
            old_name = safe.alarm_name('notification', 'Past', past)
            old_token = store.save(old_name, 'Past', 'Soon', 'Now', 'Icon', past.timestamp())
            self.calls.clear()
            n._scheduleNotification('Channel', 'Past', past, 'one')
            self.assertEqual(self.calls, [])
            self.assertIsNotNone(store.take(old_token, 'now', NOW.timestamp()))
            n._unscheduleNotification('Past', past, 'one')
            self.assertIsNone(store.take(old_token, '5mins', NOW.timestamp()))
            # Explicit cancellation invalidates the known legacy key as well.
            n.removeNotification(p)
            self.assertEqual(store.names(), [])
            self.assertIsNone(store.take(token, 'now', START.timestamp()))

    @unittest.skipIf(BASELINE, 'focused cancellation and horizon regression')
    def test_recurring_cancellation_and_existing_date_bounds(self):
        self.event(start=START + datetime.timedelta(days=1))
        self.event(start=START + datetime.timedelta(days=7))
        self.event(start=NOW - datetime.timedelta(days=1))
        for kind, table in [('notification', 'notifications'), ('autoplay', 'autoplays')]:
            with tempfile.TemporaryDirectory(prefix='tvguide-recurrence-') as profile:
                store = reminders.ReminderData(profile)
                n = self.scheduler(kind, store)
                self.rule(table, 1)
                rows = self.rows(table)
                self.assertEqual({p.startDate for p in rows}, {START, START + datetime.timedelta(days=1)})
                (n.scheduleNotifications if kind == 'notification' else n.scheduleAutoplays)()
                self.calls.clear()
                (n.removeNotification if kind == 'notification' else n.removeAutoplay)(rows[0])
                for p in rows:
                    name = n.createAlarmClockName(p.title, p.startDate, p.channel.id)
                    self.assertTrue(any(name in c for c in self.calls))
                self.assertEqual(store.names(), [])
                self.assertEqual(self.rows(table), [])
                # Once keeps its historical lack of a date horizon, even past start.
                past = NOW - datetime.timedelta(days=1)
                self.conn.execute('INSERT INTO ' + table + ' VALUES(?,?,?,?,?)',
                                  ('one', 'Show', 'active', past, 0))
                self.assertEqual([p.startDate for p in self.rows(table)], [past])
                self.conn.execute('DELETE FROM ' + table)

    @unittest.skipIf(BASELINE, 'new-only add and source-aware producer regression')
    def test_new_rule_add_does_not_arm_rerun_and_source_keys_coexist(self):
        for kind, table in [('notification', 'notifications'), ('autoplay', 'autoplays')]:
            with tempfile.TemporaryDirectory(prefix='tvguide-source-') as profile:
                store = reminders.ReminderData(profile)
                n = self.scheduler(kind, store)
                p = models['Program'](models['Channel']('one', 'Channel', ''), 'Show', '',
                                      START, START + datetime.timedelta(minutes=30), '', '', is_new='')
                add = n.addNotification if kind == 'notification' else n.addAutoplay
                add(p, 2)
                self.assertEqual(self.calls, [])
                self.assertEqual(self.conn.execute('SELECT count(*) FROM ' + table).fetchone()[0], 1)
                self.conn.execute('DELETE FROM ' + table)
                p.is_new = 'New'
                add(p, 2)
                first = n.createAlarmClockName(p.title, p.startDate, p.channel.id)
                self.db.source.KEY = 'other'
                add(p, 2)
                second = n.createAlarmClockName(p.title, p.startDate, p.channel.id)
                self.assertNotEqual(first, second)
                for name in (first, second):
                    self.assertTrue(any(c.startswith('AlarmClock(' + name) for c in self.calls))
                if kind == 'notification':
                    self.assertEqual(set(store.names()), {first, second})
                self.db.source.KEY = 'active'
                self.conn.execute('DELETE FROM ' + table)

    def test_new_daily_and_source_global_like(self):
        self.conn.execute('DELETE FROM programs')
        self.event()
        self.event(start=START + datetime.timedelta(days=1), new='')
        self.event(start=START + datetime.timedelta(hours=1), new='')
        for table in ('notifications', 'autoplays'):
            self.rule(table, 2)
            rows = self.rows(table)
            print(('BEFORE' if BASELINE else 'AFTER'), table, 'new-only', len(rows))
            self.assertEqual(len(rows), 0 if BASELINE else 1)
            if rows:
                self.assertEqual(rows[0].is_new, 'New')
            if not BASELINE and table == 'autoplays':
                self.assertEqual([r['start_date'] for r in self.db.getAutoplayAlarmIdentities()], [START])
            self.conn.execute('DELETE FROM ' + table)
            self.rule(table, 3)
            self.assertEqual({p.startDate for p in self.rows(table)}, {START, START + datetime.timedelta(days=1)})
            if not BASELINE and table == 'autoplays':
                self.assertEqual({r['start_date'] for r in self.db.getAutoplayAlarmIdentities()},
                                 {START, START + datetime.timedelta(days=1)})
            self.conn.execute('DELETE FROM ' + table)
        self.conn.execute('DELETE FROM programs')
        for source in ('active', 'other'):
            for channel in ('one', 'two'):
                self.event(channel, source, title='Show special')
        self.rule('notifications', 4, title='Show%')
        rows = self.rows('notifications')
        print(('BEFORE' if BASELINE else 'AFTER'), 'LIKE Show%', [p.channel.title for p in rows])
        self.assertEqual(len(rows), 8 if BASELINE else 2)
        if not BASELINE:
            self.assertEqual({p.channel.title for p in rows}, {'active/one', 'active/two'})
            self.conn.execute('UPDATE notifications SET program_title=?', ['sh_w%'])
            self.assertEqual({p.channel.id for p in self.rows('notifications')}, {'one', 'two'})
        # Actual removal deliberately removes this source-wide LIKE rule via channel two.
        self.env['_removeNotification'](self.db, next(p for p in rows if p.channel.id == 'two'))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM notifications').fetchone()[0], 0)

    def scheduler(self, kind, store):
        self.calls = []
        name = 'Notification' if kind == 'notification' else 'Autoplay'
        env = dict(datetime=datetime, time=time, alarm_name=safe.alarm_name,
                   alarm_command=reminders.alarm_command, event_key=reminders.event_key,
                   encode_identity=autoplay.encode_identity,
                   strings=lambda phase, channel: phase + ': ' + channel,
                   NOTIFICATION_5_MINS='Soon', NOTIFICATION_NOW='Now',
                   ADDON=SimpleNamespace(getSetting=lambda key: {'autoplays.before': '2',
                       'autoplays.after': '3', 'autoplays.stop': 'true'}[key]),
                   xbmc=SimpleNamespace(executebuiltin=self.calls.append, LOGERROR=4, log=lambda *a: None))
        cls = extract(kind + '.py', [name], env)[name]
        obj = cls.__new__(cls)
        obj.database, obj.reminders, obj.icon = self.db, store, 'icon.png'
        return obj

    def test_distinct_registrations_remove_survivor_and_clear(self):
        for kind, table in [('notification', 'notifications'), ('autoplay', 'autoplays')]:
            with tempfile.TemporaryDirectory(prefix='tvguide-ownership-') as profile:
                store = reminders.ReminderData(profile)
                n = self.scheduler(kind, store)
                self.rule(table, 0)
                p = self.rows(table)[0]
                q = models['Program'](models['Channel']('two', 'active/two', 'active'),
                                      p.title, '', p.startDate, p.endDate, '', '')
                self.conn.execute('DELETE FROM ' + table)
                add = n.addNotification if kind == 'notification' else n.addAutoplay
                add(p, 0)
                add(q, 0)
                alarm_names = {c.split(',', 1)[0] for c in self.calls if c.startswith('AlarmClock(')}
                print(('BEFORE' if BASELINE else 'AFTER'), kind, 'alarm registrations', len(alarm_names),
                      'JSON registrations', len(store.names()))
                self.assertEqual(len(alarm_names), 2 if BASELINE else 4)
                if kind == 'notification':
                    self.assertEqual(len(store.names()), 1 if BASELINE else 2)
                if not BASELINE:
                    survivor = n.createAlarmClockName(q.title, q.startDate, q.channel.id)
                    self.calls.clear()
                    (n.removeNotification if kind == 'notification' else n.removeAutoplay)(p)
                    self.assertFalse(any(survivor in c for c in self.calls))
                    self.assertEqual([r.channel.id for r in self.rows(table)], ['two'])
                    if kind == 'notification':
                        self.assertEqual(store.names(), [survivor])
                    self.calls.clear()
                    (n.clearNotifications if kind == 'notification' else n.clearAutoplays)()
                    self.assertTrue(any(survivor in c for c in self.calls))
                    self.assertEqual(store.names(), [])
                self.conn.execute('DELETE FROM ' + table)

    def test_global_clear_includes_other_source_and_direct_beyond_horizon(self):
        for kind, table in [('notification', 'notifications'), ('autoplay', 'autoplays')]:
            self.conn.execute('DELETE FROM programs')
            with tempfile.TemporaryDirectory(prefix='tvguide-clear-') as profile:
                store = reminders.ReminderData(profile)
                n = self.scheduler(kind, store)
                add = n.addNotification if kind == 'notification' else n.addAutoplay
                for source, days in [('active', 10), ('other', 0)]:
                    start = START + datetime.timedelta(days=days, hours=2)
                    title = 'Direct ' + source
                    self.event(source=source, title=title, start=start)
                    self.db.source.KEY = source
                    p = models['Program'](models['Channel']('one', source, source), title, '',
                                          start, start + datetime.timedelta(minutes=30), '', '')
                    add(p, 1)
                self.db.source.KEY = 'active'
                queued = set()

                def capture(command):
                    match = re.match(r'(AlarmClock|CancelAlarm)\((tvguide-[a-z]+-[0-9a-f]{64}-[a-z0-9]+),', command)
                    self.assertIsNotNone(match)
                    action, name = match.groups()
                    (queued.add if action == 'AlarmClock' else queued.discard)(name)

                for command in self.calls:
                    capture(command)
                self.assertEqual(len(queued), 4)
                if kind == 'notification':
                    late_name = safe.alarm_name('notification', 'Late pending', NOW - datetime.timedelta(days=2))
                    late_token = store.save(late_name, 'Late', 'Soon', 'Now', 'Icon',
                                            (NOW - datetime.timedelta(days=2)).timestamp())
                    n.scheduleNotifications()
                    self.assertIn(late_name, store.names())
                self.calls.clear()
                (n.clearNotifications if kind == 'notification' else n.clearAutoplays)()
                for command in self.calls:
                    capture(command)
                print(('BEFORE' if BASELINE else 'AFTER'), kind, 'global clear queued alarms left', len(queued))
                self.assertEqual(len(queued), 2 if BASELINE and kind == 'autoplay' else 0)
                self.assertEqual(store.names(), [])
                if kind == 'notification':
                    self.assertIsNone(store.take(late_token, 'now', NOW.timestamp()))
                self.assertEqual(self.conn.execute('SELECT count(*) FROM ' + table).fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
