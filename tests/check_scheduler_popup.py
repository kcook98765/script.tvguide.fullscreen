"""Actual scheduler queries/popup handlers with real SQLite and inert adapters.

No Kodi/stub imports, native actions, network, profile or callback execution.
--original and --revert exercise product negatives without editing source files.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import argparse
import ast
import copy
import datetime
from functools import lru_cache
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import time
from types import SimpleNamespace as NS
import unittest

import check_popup_optional_controls as popup_adapter

ROOT = Path(__file__).resolve().parents[1]
BASE = '09c0602857fb4e05c726df5e45f6244daeb1b0c7'
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--original', action='store_true')
parser.add_argument('--revert', choices=('matching', 'dispatch', 'navigation',
                                       'popup-cancel', 'key-cancel', 'title-copy'))
OPTIONS, remaining = parser.parse_known_args()
sys.argv = [sys.argv[0]] + remaining
NOW = datetime.datetime(2026, 11, 21, 12)
START = NOW + datetime.timedelta(hours=2)


@lru_cache(maxsize=None)
def original(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT, text=True)


@lru_cache(maxsize=None)
def tree(path):
    text = original(path) if OPTIONS.original else (ROOT / path).read_text()
    result = ast.parse(text)
    if OPTIONS.revert == 'matching' and path == 'source.py':
        old = ast.parse(original(path))
        names = {'_isNotificationRequiredForProgramStart', '_isAutoPlayRequiredForProgramStart'}
        current_db = next(n for n in result.body if isinstance(n, ast.ClassDef) and n.name == 'Database')
        old_db = next(n for n in old.body if isinstance(n, ast.ClassDef) and n.name == 'Database')
        prior = {n.name: n for n in old_db.body if isinstance(n, ast.FunctionDef) and n.name in names}
        current_db.body = [prior.get(getattr(n, 'name', ''), n) for n in current_db.body]
    if path == 'gui.py' and OPTIONS.revert in ('dispatch', 'navigation', 'popup-cancel', 'key-cancel', 'title-copy'):
        # Narrowly revert only the selected production correction in memory.
        replacements = {
            'dispatch': [
                ('if self.database.isNotificationRequiredForProgramStart(program):', 'if program.notificationScheduled:'),
                ('if self.database.isAutoPlayRequiredForProgramStart(program):', 'if program.autoplayScheduled:')],
            'navigation': [
                ('        self.showRemind = not self.database.isNotificationRequiredForProgramStart(self.program)\n', ''),
                ('        self.showAutoplay = not self.database.isAutoPlayRequiredForProgramStart(self.program)\n', '')],
            'title-copy': [('program = copy.copy(program)', 'program = program')],
        }
        if OPTIONS.revert in ('popup-cancel', 'key-cancel'):
            # Both sites are identical apart from indentation; target the owner method.
            cls = next(n for n in result.body if isinstance(n, ast.ClassDef) and n.name == 'TVGuide')
            name = '_showContextMenu' if OPTIONS.revert == 'popup-cancel' else 'onActionEPGMode'
            method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
            class RemoveCancel(ast.NodeTransformer):
                changed = 0
                def visit_If(self, node):
                    if (isinstance(node.test, ast.BoolOp) and isinstance(node.test.op, ast.Or)
                            and isinstance(node.test.values[-1], ast.Name) and node.test.values[-1].id == 'title'):
                        node.test = ast.copy_location(ast.Constant(value=True), node.test)
                        self.changed += 1
                    return self.generic_visit(node)
            mutation = RemoveCancel()
            mutation.visit(method)
            assert mutation.changed == 1, ('cancel mutation not applied', name)
        else:
            for before, after in replacements[OPTIONS.revert]:
                assert before in text, ('mutation not applied', OPTIONS.revert, before)
                text = text.replace(before, after)
            result = ast.parse(text)
    return result


def extract(path, name, methods, env):
    cls = copy.deepcopy(next(n for n in tree(path).body if isinstance(n, ast.ClassDef) and n.name == name))
    cls.bases = []
    if methods is not None:
        cls.body = [n for n in cls.body if isinstance(n, ast.Assign)
                    or isinstance(n, ast.FunctionDef) and n.name in methods]
    exec(compile(ast.Module(body=[cls], type_ignores=[]), path + ':actual', 'exec'), env)
    return env[name]


Channel = extract('utils.py', 'Channel', None, {})
Program = extract('utils.py', 'Program', None, {})


class Clock(datetime.datetime):
    @classmethod
    def now(cls):
        return NOW


METHODS = {'_createTables', 'adapt_datetime', 'convert_datetime', '_getFullNotifications', '_getFullAutoplays',
           '_getNotificationRulesForProgram', '_getAutoplayRulesForProgram',
           '_isNotificationRequiredForProgramStart', '_isAutoPlayRequiredForProgramStart',
           '_removeNotification', '_removeAutoplay', '_addNotification', '_addAutoplay', '_getChannelListing'}


class SchedulerPopup(unittest.TestCase):
    def setUp(self):
        env = dict(sqlite3=sqlite3, datetime=NS(datetime=Clock, timedelta=datetime.timedelta), time=time,
                   Channel=Channel, Program=Program, ADDON=NS(getSetting=lambda _: '5'),
                   xbmc=NS(log=lambda *a: None, LOGERROR=4), log=lambda *a: None)
        Database = extract('source.py', 'Database', METHODS, env)
        for kind in (datetime.datetime, Clock):
            sqlite3.register_adapter(kind, Database.adapt_datetime)
        sqlite3.register_converter('timestamp', Database.convert_datetime)
        self.db = db = Database()
        db.conn = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
        self.addCleanup(db.conn.close)
        db.conn.row_factory = sqlite3.Row
        db.conn.execute('PRAGMA foreign_keys=ON')
        db.source = NS(KEY='active')
        db._createTables()
        self.assertEqual(tuple(db.conn.execute('SELECT * FROM version').fetchone()), (1, 4, 1))
        for idx, src in enumerate(('active', 'other'), 1):
            db.conn.execute('INSERT OR IGNORE INTO sources VALUES (?,?)', (src, NOW))
            db.conn.execute('INSERT INTO updates VALUES (?,?,?,?)', (idx, src, '2026-11-21', NOW))
            for channel in ('one', 'two'):
                db.conn.execute('INSERT INTO channels VALUES (?,?,?,?,?,?,?,?)',
                                (channel, src+'/'+channel, '', 'inert.mp4', src, '', 1, 0))
        db.isNotificationRequiredForProgramStart = db._isNotificationRequiredForProgramStart
        db.isAutoPlayRequiredForProgramStart = db._isAutoPlayRequiredForProgramStart
        for public, private in (('getNotificationRulesForProgram', '_getNotificationRulesForProgram'),
                                ('getAutoplayRulesForProgram', '_getAutoplayRulesForProgram')):
            if hasattr(db, private):
                setattr(db, public, getattr(db, private))
        db.isAutoPlaywithRequiredForProgramStart = lambda _: False
        db.getNextProgram = db.getPreviousProgram = lambda _: None
        db.getCustomStreamUrl = lambda _: 'inert.mp4'
        db.setCategory = lambda _: None
        self.calls = []

    def event(self, start=START, new='New', title='Show', channel='one', source='active'):
        self.db.conn.execute('INSERT INTO programs(channel,title,start_date,end_date,source,updates_id,is_new) '
                             'VALUES (?,?,?,?,?,?,?)',
                             (channel, title, start, start+datetime.timedelta(minutes=30), source,
                              1 if source == 'active' else 2, new))
        return Program(Channel(channel, source+'/'+channel, '', '', 'inert.mp4'), title, '', start,
                       start+datetime.timedelta(minutes=30), 'Synthetic plot', '', is_new=new)

    def rule(self, table, kind, start=START, title='Show', channel='one', source='active'):
        self.db.conn.execute('INSERT INTO '+table+' VALUES (?,?,?,?,?)', (channel, title, source, start, str(kind)))

    def snapshot(self):
        return {table: [tuple(row) for row in self.db.conn.execute('SELECT rowid,* FROM '+table)]
                for table in ('channels', 'programs', 'notifications', 'autoplays', 'autoplaywiths')}

    def test_event_queries_match_reconstruction_and_do_not_mutate_data(self):
        for table, query, full in (
                ('notifications', self.db._isNotificationRequiredForProgramStart, self.db._getFullNotifications),
                ('autoplays', self.db._isAutoPlayRequiredForProgramStart, self.db._getFullAutoplays)):
            for kind, delta, new, expected in (
                    (0, 0, 'New', True), (0, -86400, 'New', False), (1, -86400, '', True),
                    (2, -86400, 'New', True), (2, 0, '', False),
                    (3, -86400, '', True), (3, -3600, 'New', False)):
                with self.subTest(table=table, kind=kind, delta=delta, new=new):
                    self.db.conn.execute('DELETE FROM programs')
                    self.db.conn.execute('DELETE FROM '+table)
                    p = self.event(new=new)
                    self.rule(table, kind, start=START+datetime.timedelta(seconds=delta))
                    before = self.snapshot()
                    self.assertEqual(bool(query(p)), expected)
                    self.assertEqual(bool(full(5)), expected)
                    self.assertEqual(self.snapshot(), before)

    def test_all_matching_rows_are_considered_in_both_orders(self):
        p = self.event()
        for table, query in (('notifications', self.db._isNotificationRequiredForProgramStart),
                             ('autoplays', self.db._isAutoPlayRequiredForProgramStart)):
            for order in ((-3600, 0), (0, -3600)):
                with self.subTest(table=table, order=order):
                    self.db.conn.execute('DELETE FROM '+table)
                    for delta in order:
                        self.rule(table, 0, start=START+datetime.timedelta(seconds=delta))
                    self.assertTrue(query(p))

    def test_source_channel_and_daily_time_boundaries(self):
        p = self.event()
        for table, query in (('notifications', self.db._isNotificationRequiredForProgramStart),
                             ('autoplays', self.db._isAutoPlayRequiredForProgramStart)):
            for source, channel in (('other', 'one'), ('active', 'two')):
                self.rule(table, 1, source=source, channel=channel)
                self.assertFalse(query(p))
            for delta, expected in ((-86400, True), (-86400+1, False), (-86400-1, False)):
                self.db.conn.execute('DELETE FROM '+table)
                self.rule(table, 3, start=START+datetime.timedelta(seconds=delta))
                self.assertEqual(bool(query(p)), expected)

    def test_wildcards_are_source_wide_type_four_and_not_masked(self):
        p = self.event(title='Café_20 Show')
        for reverse in (False, True):
            self.db.conn.execute('DELETE FROM notifications')
            rules = [(0, p.title, 'one'), (4, 'Café%Show', 'two')]
            for kind, title, channel in rules[::(-1 if reverse else 1)]:
                self.rule('notifications', kind, start=START-datetime.timedelta(days=1), title=title, channel=channel)
            self.assertTrue(self.db._isNotificationRequiredForProgramStart(p))
        self.db.conn.execute('DELETE FROM notifications')
        self.rule('notifications', 4, title='Café%Show', source='other')
        self.assertFalse(self.db._isNotificationRequiredForProgramStart(p))
        self.rule('notifications', 0, title='Café%Show')
        self.assertFalse(self.db._isNotificationRequiredForProgramStart(p))

    def guide(self, programme, chosen, selections=(), answer='', navigate=None, after_label=None):
        # Reuse actual bundled-XML/visibility/control/super adapter, not another UI mock.
        popup_adapter.TREE = tree('gui.py')
        popup, scope = popup_adapter.make_popup()
        popup.database = self.db
        popup.program = programme
        popup.currentChannel = programme.channel
        popup.nextprogram = None
        popup.category = 'All Channels'
        popup.categories = []
        popup.showRemind = not self.db.isNotificationRequiredForProgramStart(programme)
        popup.showAutoplay = not self.db.isAutoPlayRequiredForProgramStart(programme)
        scope['copy'] = copy
        scope['ADDON'].setSetting = lambda *args: None
        Popup = scope['PopupMenu']
        def modal():
            popup.onInit()
            if navigate is not None:
                self.db.getNextProgram = lambda _: navigate
                popup.onClick(Popup.C_POPUP_PROGRAM_NEXT_BIG)
            if after_label:
                after_label(popup)
            popup.onClick(chosen)
        popup.show = popup.onInit
        popup.doModal = modal
        # Use the existing instance with its original class name/super namespace intact.
        def factory(*args):
            return popup
        factory.__dict__.update({name: value for name, value in vars(Popup).items() if name.startswith('C_POPUP_')})
        guide_scope = dict(scope, PopupMenu=factory, copy=copy)
        selection = iter(selections)
        self.prompts = []
        def select(*args):
            self.prompts.append(args)
            return next(selection)
        guide_scope['xbmcgui'] = NS(Dialog=lambda: NS(select=select, input=lambda *a: answer))
        Guide = extract('gui.py', 'TVGuide', {'_showContextMenu', 'onActionEPGMode', '_selectScheduleRule'}, guide_scope)
        guide = Guide()
        guide.database = self.db
        guide.tvdb_urls = {}
        guide.category = 'All Channels'
        guide.categories = []
        guide.mode = guide_scope['MODE_EPG']
        guide.channelIdx, guide.viewStartDate = 0, NOW
        guide._hideControl = lambda *a: None
        guide.redraws = []
        guide.onRedrawEPG = lambda *a: guide.redraws.append(a)
        for name, table, add, remove in (
                ('notification', 'notifications', self.db._addNotification, self.db._removeNotification),
                ('autoplay', 'autoplays', self.db._addAutoplay, self.db._removeAutoplay)):
            def add_capture(p, kind, name=name, add=add):
                self.calls.append((name, 'add', p, kind))
                add(p, kind)
            def remove_capture(p, rule=None, name=name, remove=remove):
                self.calls.append((name, 'remove', p))
                if rule is None:
                    remove(p)
                else:
                    remove(p, rule)
            setattr(guide, name, NS(addNotification=add_capture, removeNotification=remove_capture)
                    if name == 'notification' else NS(addAutoplay=add_capture, removeAutoplay=remove_capture))
        return guide, popup, guide_scope

    def test_listing_false_flags_cancel_instead_of_duplicate(self):
        self.event()
        for table, cid in (('notifications', 4002), ('autoplays', 4008)):
            with self.subTest(table=table):
                self.rule(table, 0)
                p = self.db._getChannelListing(Channel('one', 'active/one', '', '', 'inert.mp4'))[0]
                self.assertFalse(p.notificationScheduled)
                self.assertFalse(p.autoplayScheduled)
                g, popup, _ = self.guide(p, cid, [0])
                g._showContextMenu(p)
                self.assertEqual(popup.controls[cid].label, "Don't Remind" if cid == 4002 else "Don't AutoPlay")
                self.assertEqual(self.calls[-1][1], 'remove')
                self.assertEqual(self.db.conn.execute('SELECT COUNT(*) FROM '+table).fetchone()[0], 0)
                self.assertEqual(self.prompts, [])

    def test_popup_navigation_refreshes_label_and_dispatch_for_selected_event(self):
        first = self.event()
        second = self.event(start=START+datetime.timedelta(hours=1), title='Next show', channel='two')
        for table, cid in (('notifications', 4002), ('autoplays', 4008)):
            for initial_scheduled in (False, True):
                with self.subTest(table=table, initial_scheduled=initial_scheduled):
                    self.db.conn.execute('DELETE FROM '+table)
                    target = first if initial_scheduled else second
                    self.rule(table, 0, title=target.title, channel=target.channel.id, start=target.startDate)
                    g, popup, _ = self.guide(first, cid, [0], navigate=second)
                    g._showContextMenu(first)
                    self.assertIs(self.calls[-1][2], second)
                    self.assertEqual(self.calls[-1][1], 'add' if initial_scheduled else 'remove')
                    expected = ('Remind' if cid == 4002 else 'AutoPlay') if initial_scheduled else (
                        "Don't Remind" if cid == 4002 else "Don't AutoPlay")
                    self.assertEqual(popup.controls[cid].label, expected)

    def test_dispatch_rechecks_database_not_initial_popup_or_program_flags(self):
        p = self.event()
        p.notificationScheduled = p.autoplayScheduled = True
        for cid, table in ((4002, 'notifications'), (4008, 'autoplays')):
            self.db.conn.execute('DELETE FROM '+table)
            g, _, _ = self.guide(p, cid, [0])
            g._showContextMenu(p)
            self.assertEqual(self.calls[-1][1], 'add')
            # A newly opened popup sees the new authoritative row despite false flags.
            p.notificationScheduled = p.autoplayScheduled = False
            g, _, _ = self.guide(p, cid)
            g._showContextMenu(p)
            self.assertEqual(self.calls[-1][1], 'remove')

    def run_prompt(self, route, p, answer, kind):
        selections = [kind] if route == 'popup' else [0, kind]
        g, _, scope = self.guide(p, 4002, selections, answer)
        if route == 'popup':
            g._showContextMenu(p)
        else:
            action_id = scope['COMMAND_ACTIONS']['SCHEDULERS_MENU'][0] if 'COMMAND_ACTIONS' in scope else 991
            # Extracted GUI module loads its command map at runtime; inert map only selects this branch.
            keys = ('CLOSE', 'CATEGORIES_BAR', 'NEXT_DAY', 'PREV_DAY', 'PAGE_UP', 'PAGE_DOWN', 'GO_TO_NOW',
                    'GO_TO_FIRST_CHANNEL', 'CHANNEL_LISTING', 'STOP_AUTOPLAYWITH', 'PLAY_AUTOPLAYWITH',
                    'DELETE_PROGRAM_IMAGE', 'SCHEDULERS_MENU')
            scope['COMMAND_ACTIONS'] = {k: ([action_id] if k == 'SCHEDULERS_MENU' else []) for k in keys}
            g.focusPoint = None
            g.controlAndProgramList = []
            g.getFocus = lambda: popup_adapter.Control()
            g.getFocusId = lambda: 123
            g._getProgramFromControl = lambda _: p
            g.onActionEPGMode(NS(getId=lambda: action_id))
        return g

    def test_wildcard_cancel_is_no_rule_no_action_no_programme_mutation_both_routes(self):
        p = self.event()
        for route in ('popup', 'key'):
            with self.subTest(route=route):
                before, metadata = self.snapshot(), vars(p).copy()
                self.calls.clear()
                guide = self.run_prompt(route, p, '', 4)
                self.assertEqual(self.calls, [])
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(vars(p), metadata)
                self.assertEqual(guide.redraws, [(0, NOW)])

    def test_accepted_wildcard_retains_text_without_mutating_selected_programme(self):
        for route in ('popup', 'key'):
            self.db.conn.execute('DELETE FROM notifications')
            self.db.conn.execute('DELETE FROM programs')
            p = self.event(title="Café's episode")
            metadata = vars(p).copy()
            pattern = "Café%_ 'episode'"
            self.run_prompt(route, p, pattern, 4)
            rows = [tuple(r) for r in self.db.conn.execute('SELECT program_title,type FROM notifications')]
            self.assertEqual(rows, [(pattern, '4')])
            self.assertEqual(vars(p), metadata)
            saved = self.calls[-1][2]
            self.assertIsNot(saved, p)
            self.assertIs(saved.channel, p.channel)
            self.assertEqual(vars(saved), dict(metadata, title=pattern))

    def test_ordinary_reminder_choices_and_outer_cancel_are_unchanged(self):
        p = self.event()
        for route in ('popup', 'key'):
            for kind in (-1, 0, 1, 2, 3):
                with self.subTest(route=route, kind=kind):
                    self.db.conn.execute('DELETE FROM notifications')
                    self.calls.clear()
                    guide = self.run_prompt(route, p, '', kind)
                    rows = [tuple(r) for r in self.db.conn.execute('SELECT program_title,type FROM notifications')]
                    self.assertEqual(rows, [] if kind == -1 else [(p.title, str(kind))])
                    self.assertEqual(len(self.calls), 0 if kind == -1 else 1)
                    self.assertEqual(guide.redraws, [(0, NOW)])


if __name__ == '__main__':
    unittest.main(verbosity=2)
