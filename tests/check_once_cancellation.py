"""Actual-schema cancellation/producer/UI regressions; all commands are inert.

--baseline uses exact pre-fix Git objects and must fail assertions, not fixtures.
--mutation applies one narrow production reversion in memory, never on disk.
"""
import ast
import datetime
from functools import lru_cache
import inspect
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace as NS
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = '41593d17f63cb985b95816f3b53ca7acaefc7352'
BASELINE = '--baseline' in sys.argv
if BASELINE:
    sys.argv.remove('--baseline')
MUTATION = None
if '--mutation' in sys.argv:
    index = sys.argv.index('--mutation')
    MUTATION = sys.argv[index+1]
    del sys.argv[index:index+2]
# Explicit sibling-test adapter path, including under Python -I.
sys.path.insert(0, str(ROOT / 'tests'))
import check_scheduler_popup as ui
import check_schedule_ownership as ownership


@lru_cache(maxsize=None)
def text(path):
    if BASELINE:
        return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT,text=True)
    value = (ROOT/path).read_text()
    edits = {
        'once-scope': ('source.py', 'AND start_date IS ? AND type=?', 'AND ? IS NOT NULL AND ? IS NOT NULL'),
        'event-scope': ('source.py', 'WHERE channel IS ? AND program_title=? AND source=?',
                        'WHERE ? IS NOT NULL AND program_title=? AND ? IS NOT NULL'),
        'clicked-owner': ('notification.py', 'if self.database.isNotificationRequiredForProgramStart(program):', 'if False:'),
        'clicked-autoplay-owner': ('autoplay.py', 'if self.database.isAutoPlayRequiredForProgramStart(program):', 'if False:'),
        'selection': ('gui.py', 'if len(rules) == 1:', 'if rules:'),
        'explicit-rule': ('source.py', 'if rule is None:', 'if True:'),
    }
    if MUTATION:
        filename,before,after = edits[MUTATION]
        if path == filename:
            assert before in value, ('mutation not applied',MUTATION)
            value = value.replace(before,after)
    return value


ui.tree = lru_cache(maxsize=None)(lambda path: ast.parse(text(path)))
ui.METHODS |= {'_getNotificationRulesForProgram','_getAutoplayRulesForProgram'}
NOW, START = ui.NOW, ui.START
CLOCK = NS(datetime=ui.Clock,timedelta=datetime.timedelta)


class Capture:
    def __init__(self):
        self.calls, self.queued = [], {}

    def __call__(self, command):
        match = re.fullmatch(r'(AlarmClock|CancelAlarm)\((tvguide-[a-z]+-[0-9a-f]{64}-[a-z0-9]+),(.*)\)',command)
        assert match, command
        self.calls.append(command)
        action,name,_ = match.groups()
        if action == 'AlarmClock':
            self.queued[name] = command
        else:
            self.queued.pop(name,None)


class OnceCancellation(unittest.TestCase):
    def setUp(self):
        self.fixture = f = ui.SchedulerPopup()
        f.setUp()
        self.addCleanup(f.doCleanups)
        self.db = db = f.db
        for public,private in (
                ('getFullNotifications','_getFullNotifications'),('getFullAutoplays','_getFullAutoplays'),
                ('addNotification','_addNotification'),('removeNotification','_removeNotification'),
                ('addAutoplay','_addAutoplay'),('removeAutoplay','_removeAutoplay'),
                ('getNotificationRulesForProgram','_getNotificationRulesForProgram'),
                ('getAutoplayRulesForProgram','_getAutoplayRulesForProgram')):
            if hasattr(db,private):
                if public.startswith('getFull'):
                    setattr(db,public,lambda private=private:getattr(db,private)(5))
                else:
                    setattr(db,public,lambda *args,private=private:getattr(db,private)(*args))
        sqlite3.register_adapter(datetime.datetime,type(db).adapt_datetime)
        self.profile = tempfile.TemporaryDirectory(prefix='tvguide-once-test-')
        self.addCleanup(self.profile.cleanup)
        self.store = ownership.reminders.ReminderData(self.profile.name)
        self.capture = Capture()
        self.schedulers = {}
        for kind,name in (('notification','Notification'),('autoplay','Autoplay')):
            env = dict(datetime=CLOCK,time=NS(time=lambda:NOW.timestamp()),
                       alarm_name=ownership.safe.alarm_name,alarm_command=ownership.reminders.alarm_command,
                       event_key=ownership.reminders.event_key,encode_identity=ownership.autoplay.encode_identity,
                       strings=lambda phase,channel:phase+': '+channel,NOTIFICATION_5_MINS='Soon',NOTIFICATION_NOW='Now',
                       ADDON=NS(getSetting=lambda key:{'autoplays.before':'6','autoplays.after':'6','autoplays.stop':'true'}[key]),
                       xbmc=NS(executebuiltin=self.capture,LOGERROR=4,log=lambda *a:None))
            cls = ui.extract(kind+'.py',name,None,env)
            obj = cls.__new__(cls)
            obj.database,obj.reminders,obj.icon = db,self.store,'inert-icon.png'
            self.schedulers[kind] = obj

    def event(self,start=START,channel='one',source='active',new='New',title='Show'):
        end = start+datetime.timedelta(minutes=30 if source=='active' else 31)
        self.db.conn.execute('INSERT INTO programs(channel,title,start_date,end_date,source,updates_id,is_new) '
                             'VALUES (?,?,?,?,?,?,?)',(channel,title,start,end,source,1 if source=='active' else 2,new))
        return ui.Program(ui.Channel(channel,source+'/'+channel,'','','inert.mp4'),title,'',start,end,'Plot','',is_new=new)

    def rule(self,kind,p,rule_type=0,title=None,channel=None,start=None,source='active'):
        rule = (channel or p.channel.id,title or p.title,source,start or p.startDate,str(rule_type))
        self.db.conn.execute('INSERT INTO '+self.table(kind)+' VALUES(?,?,?,?,?)',rule)
        self.db.conn.commit()
        return rule

    @staticmethod
    def table(kind):
        return 'notifications' if kind=='notification' else 'autoplays'

    def rows(self,kind):
        return [tuple(r) for r in self.db.conn.execute('SELECT rowid,* FROM '+self.table(kind)+' ORDER BY rowid')]

    def records(self):
        return {p.name:p.read_bytes() for p in Path(self.store.directory).glob('*') if p.is_file()}

    def schedule(self):
        for source in ('other','active'):
            self.db.source.KEY = source
            self.schedulers['notification'].scheduleNotifications()
            self.schedulers['autoplay'].scheduleAutoplays()

    def cancel(self,kind,p,rule=None):
        method = getattr(self.schedulers[kind],'removeNotification' if kind=='notification' else 'removeAutoplay')
        # Original supports only Program: exercise it, then fail behavioral assertions.
        if 'rule' in inspect.signature(method).parameters:
            method(p,rule)
        else:
            method(p)

    def required(self,kind,p):
        return bool((self.db.isNotificationRequiredForProgramStart if kind=='notification'
                     else self.db.isAutoPlayRequiredForProgramStart)(p))

    def name(self,kind,p):
        return self.schedulers[kind].createAlarmClockName(p.title,p.startDate,p.channel.id)

    def test_independent_reminder_controls_and_idempotence(self):
        self.check_independent_once('notification')

    def test_independent_autoplay_controls_and_idempotence(self):
        self.check_independent_once('autoplay')

    def check_independent_once(self,kind):
        # Each test has a fresh FK-on DB, command capture and disposable JSON store:
        # no previous subcase can supply a stale registration that masks a loss.
        self.assertEqual(self.rows('notification'),[])
        self.assertEqual(self.rows('autoplay'),[])
        self.assertEqual(self.capture.queued,{})
        self.assertEqual(self.records(),{})
        p = self.event()
        q = self.event(start=START+datetime.timedelta(days=1))
        c = self.event(channel='two')
        s = self.event(source='other')
        for event,source in ((p,'active'),(q,'active'),(c,'active'),(s,'other')):
            self.rule(kind,event,source=source)
        opposite = 'autoplay' if kind=='notification' else 'notification'
        self.rule(opposite,p)
        self.schedule()
        original_opposite = self.rows(opposite)
        original_rules = self.rows(kind)
        original_queue,original_records = dict(self.capture.queued),self.records()
        self.assertEqual(len(original_queue),10)  # four selected-type events + opposite-type pair
        self.assertEqual(len(original_records),4 if kind=='notification' else 1)
        clicked_name = self.name(kind,p)
        expected_queue = {k:v for k,v in original_queue.items() if not k.startswith(clicked_name+'-')}
        expected_records = {k:v for k,v in original_records.items() if kind!='notification' or
                            k != ownership.reminders.event_key(clicked_name)+'.json'}
        self.cancel(kind,p)
        self.assertEqual([r[1:] for r in self.rows(kind)],
                         [('one','Show','active',q.startDate,'0'),('two','Show','active',START,'0'),
                          ('one','Show','other',START,'0')])
        self.assertEqual(self.rows(opposite),original_opposite)
        self.assertEqual(self.rows(kind),original_rules[1:])
        # Compare complete captured commands for every survivor, including same
        # title/start other channel/source and the opposite scheduler's callback.
        self.assertEqual(self.capture.queued,expected_queue)
        self.assertEqual(self.records(),expected_records)
        remaining = (self.rows(kind),dict(self.capture.queued),self.records())
        self.cancel(kind,p)
        self.assertEqual((self.rows(kind),self.capture.queued,self.records()),remaining)
        self.assertFalse(self.required(kind,p))
        self.assertTrue(self.required(kind,q))
        self.assertTrue(any(self.name(kind,q) in k for k in self.capture.queued))
        self.assertEqual(self.db.conn.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        self.assertEqual(list(self.db.conn.execute('PRAGMA foreign_key_check')),[])

    def test_once_overlap_shared_owner_inside_and_beyond_horizon(self):
        for kind in ('notification','autoplay'):
            for days in (1,8):
                for rule_type in ((1,2,3,4) if kind=='notification' else (1,2,3)):
                    with self.subTest(kind=kind,days=days,type=rule_type):
                        for table in ('notifications','autoplays'):
                            self.db.conn.execute('DELETE FROM '+table)
                        self.db.conn.execute('DELETE FROM programs')
                        p = self.event(start=START+datetime.timedelta(days=days))
                        once = self.rule(kind,p)
                        recurring = self.rule(kind,p,rule_type,title='Sh%' if rule_type==4 else None,
                                              channel='two' if rule_type==4 else None,
                                              start=p.startDate-datetime.timedelta(days=1))
                        self.schedule()
                        before_queue,before_records = dict(self.capture.queued),self.records()
                        self.cancel(kind,p,once)
                        self.assertEqual([r[1:] for r in self.rows(kind)],[recurring])
                        self.assertTrue(self.required(kind,p))
                        self.assertEqual(self.capture.queued,before_queue)
                        self.assertEqual(self.records(),before_records)
                        self.cancel(kind,p,once)
                        self.assertEqual([r[1:] for r in self.rows(kind)],[recurring])
                        self.assertEqual(self.capture.queued,before_queue)
                        self.assertEqual(self.records(),before_records)
                        g,popup,_ = self.fixture.guide(p,4002 if kind=='notification' else 4008)
                        popup.onInit()
                        self.assertEqual(popup.controls[4002 if kind=='notification' else 4008].label,
                                         "Don't Remind" if kind=='notification' else "Don't AutoPlay")

    def test_nonmatching_new_daily_do_not_retain_once_action(self):
        for kind in ('notification','autoplay'):
            for rule_type in (2,3):
                with self.subTest(kind=kind,type=rule_type):
                    self.db.conn.execute('DELETE FROM '+self.table(kind))
                    self.db.conn.execute('DELETE FROM programs')
                    p = self.event(new='')
                    once = self.rule(kind,p)
                    other = self.rule(kind,p,rule_type,start=START-datetime.timedelta(hours=1))
                    self.schedule()
                    self.cancel(kind,p,once)
                    self.assertEqual([r[1:] for r in self.rows(kind)],[other])
                    self.assertFalse(self.required(kind,p))
                    self.assertFalse(any(self.name(kind,p) in name for name in self.capture.queued))
                    if kind=='notification':
                        self.assertNotIn(self.name(kind,p),self.store.names())

    def test_explicit_recurring_rule_preserves_other_owners(self):
        for kind in ('notification','autoplay'):
            with self.subTest(kind=kind):
                self.db.conn.execute('DELETE FROM '+self.table(kind))
                self.db.conn.execute('DELETE FROM programs')
                p,q = self.event(),self.event(start=START+datetime.timedelta(hours=1))
                once = self.rule(kind,p)
                always = self.rule(kind,p,1)
                daily = self.rule(kind,p,3)
                self.schedule()
                self.cancel(kind,p,always)
                self.assertEqual([r[1:] for r in self.rows(kind)],[once,daily])
                self.assertTrue(self.required(kind,p))
                self.assertFalse(self.required(kind,q))
                self.assertFalse(any(self.name(kind,q) in k for k in self.capture.queued))
                self.assertTrue(any(self.name(kind,p) in k for k in self.capture.queued))

    def test_distinct_source_wide_wildcards_are_individually_selected(self):
        p = self.event()
        q = self.event(channel='two',start=START+datetime.timedelta(hours=1),title='Show special')
        first = self.rule('notification',p,4,title='Sh%',channel='two')
        second = self.rule('notification',p,4,title='S_ow')
        self.schedule()
        before = self.records()
        self.cancel('notification',p,first)
        self.assertEqual([r[1:] for r in self.rows('notification')],[second])
        self.assertTrue(self.required('notification',p))
        self.assertFalse(self.required('notification',q))
        self.assertEqual(self.store._read(ownership.reminders.event_key(self.name('notification',p))),
                         json.loads(before[ownership.reminders.event_key(self.name('notification',p))+'.json']))

    def test_actual_listing_context_selection_and_cancel(self):
        for kind,cid in (('notification',4002),('autoplay',4008)):
            for choice in (-1,0,1):
                with self.subTest(kind=kind,choice=choice):
                    self.db.conn.execute('DELETE FROM '+self.table(kind))
                    self.db.conn.execute('DELETE FROM programs')
                    p = self.event()
                    once,always = self.rule(kind,p),self.rule(kind,p,1)
                    self.schedule()
                    selected = self.db._getChannelListing(p.channel)[0]
                    self.assertFalse(selected.notificationScheduled)
                    self.assertFalse(selected.autoplayScheduled)
                    g,popup,_ = self.fixture.guide(selected,cid,[choice])
                    setattr(g,kind,self.schedulers[kind])
                    before_queue,before_records = dict(self.capture.queued),self.records()
                    g._showContextMenu(selected)
                    expected = [once,always] if choice==-1 else [always] if choice==0 else [once]
                    self.assertEqual([r[1:] for r in self.rows(kind)],expected)
                    self.assertEqual(self.capture.queued,before_queue)
                    self.assertEqual(self.records(),before_records)
                    self.assertEqual(g.redraws,[(0,NOW)])

    def test_duplicate_once_rows_are_one_logical_intent(self):
        for kind in ('notification','autoplay'):
            with self.subTest(kind=kind):
                self.db.conn.execute('DELETE FROM programs')
                self.db.conn.execute('DELETE FROM '+self.table(kind))
                p = self.event()
                once = self.rule(kind,p)
                self.rule(kind,p)
                later = self.rule(kind,p,start=START+datetime.timedelta(days=1))
                self.cancel(kind,p,once)
                self.assertEqual([r[1:] for r in self.rows(kind)],[later])

    def test_rule_query_predicates_duplicates_and_source_controls(self):
        p = self.event(new='')
        for kind in ('notification','autoplay'):
            with self.subTest(kind=kind):
                once = self.rule(kind,p)
                self.rule(kind,p)  # indistinguishable duplicate: one chooser item
                always = self.rule(kind,p,1)
                self.rule(kind,p,2)  # rerun: not a matching owner
                self.rule(kind,p,3,start=START-datetime.timedelta(hours=1))
                self.rule(kind,p,1,source='other')
                self.rule(kind,p,1,channel='two')
                self.rule(kind,p,start=START+datetime.timedelta(days=1))
                expected = [once,always]
                if kind=='notification':
                    expected.append(self.rule(kind,p,4,title='Sh%',channel='two'))
                name = 'getNotificationRulesForProgram' if kind=='notification' else 'getAutoplayRulesForProgram'
                self.assertTrue(hasattr(self.db,name),'missing explicit applicable-rule selector')
                before = self.rows(kind)
                self.assertEqual(getattr(self.db,name)(p),expected)
                self.assertEqual(self.rows(kind),before)

    def test_wildcard_context_choice_is_not_bulk_or_first_match(self):
        p = self.event()
        for choice in (-1,0,1,99):
            with self.subTest(choice=choice):
                self.db.conn.execute('DELETE FROM notifications')
                first = self.rule('notification',p,4,title='S_ow')
                second = self.rule('notification',p,4,title='Sh%',channel='two')
                self.rule('notification',p,4,title='Sh%',channel='two')
                self.schedule()
                g,_,_ = self.fixture.guide(p,4002,[choice])
                g.notification = self.schedulers['notification']
                before = self.rows('notification')
                queue,records = dict(self.capture.queued),self.records()
                g._showContextMenu(p)
                expected = before if choice in (-1,99) else [r for r in before if r[1:] != (first if choice==0 else second)]
                self.assertEqual(self.rows('notification'),expected)
                self.assertEqual(self.capture.queued,queue)
                self.assertEqual(self.records(),records)
                self.assertEqual(len(self.fixture.prompts),1)
                self.assertEqual(len(self.fixture.prompts[0][1]),2)

    def test_key_menu_uses_explicit_intent_and_safe_cancel(self):
        p = self.event()
        for kind in ('notification','autoplay'):
            for choice in (-1,0,1):
                with self.subTest(kind=kind,choice=choice):
                    self.db.conn.execute('DELETE FROM '+self.table(kind))
                    once,always = self.rule(kind,p),self.rule(kind,p,1)
                    self.schedule()
                    # Actual reconstructed programme carries scheduling flags for the key menu.
                    full = self.db.getFullNotifications if kind=='notification' else self.db.getFullAutoplays
                    selected = full()[0]
                    g,_,scope = self.fixture.guide(selected,4002,[0 if kind=='notification' else 1,choice])
                    setattr(g,kind,self.schedulers[kind])
                    keys = ('CLOSE','CATEGORIES_BAR','NEXT_DAY','PREV_DAY','PAGE_UP','PAGE_DOWN','GO_TO_NOW',
                            'GO_TO_FIRST_CHANNEL','CHANNEL_LISTING','STOP_AUTOPLAYWITH','PLAY_AUTOPLAYWITH',
                            'DELETE_PROGRAM_IMAGE','SCHEDULERS_MENU')
                    scope['COMMAND_ACTIONS'] = {k:([991] if k=='SCHEDULERS_MENU' else []) for k in keys}
                    g.focusPoint,g.controlAndProgramList = None,[]
                    g.getFocus = lambda: ui.popup_adapter.Control()
                    g.getFocusId = lambda:123
                    g._getProgramFromControl = lambda _:selected
                    g.onActionEPGMode(NS(getId=lambda:991))
                    expected = [once,always] if choice==-1 else [always] if choice==0 else [once]
                    self.assertEqual([r[1:] for r in self.rows(kind)],expected)
                    self.assertEqual(g.redraws,[(0,NOW)])

    def test_explicit_legacy_null_fields_and_stale_source_intent(self):
        p = self.event()
        for kind in ('notification','autoplay'):
            with self.subTest(kind=kind):
                once = self.rule(kind,p)
                # Old recurring rows need not have a meaningful saved start.
                # IS matches the exact NULL, not an invented date or another row.
                old = ('one','Show','active',None,'1')
                self.db.conn.execute('INSERT INTO '+self.table(kind)+' VALUES(?,?,?,?,?)',old)
                self.cancel(kind,p,old)
                self.assertEqual([r[1:] for r in self.rows(kind)],[once])
                other = self.rule(kind,p,source='other')
                self.schedule()
                before = self.rows(kind),dict(self.capture.queued),self.records()
                self.cancel(kind,p,other)
                self.assertEqual((self.rows(kind),self.capture.queued,self.records()),before)
        # Source-wide LIKE can have a NULL stored channel as well as a NULL start.
        old = (None,'Sh%','active',None,'4')
        self.db.conn.execute('INSERT INTO notifications VALUES(?,?,?,?,?)',old)
        self.cancel('notification',p,old)
        self.assertNotIn(old,[r[1:] for r in self.rows('notification')])

    def test_shared_legacy_token_and_phase_claim_survive_once_removal(self):
        p = self.event()
        once = self.rule('notification',p)
        self.rule('notification',p,1)
        legacy = ownership.safe.alarm_name('notification',p.title,p.startDate)
        token = self.store.save(legacy,'Original','Soon','Now','Original icon',START.timestamp())
        self.store.take(token,'5mins',START.timestamp()-300)
        self.schedule()
        before = self.records(),dict(self.capture.queued)
        self.cancel('notification',p,once)
        self.assertEqual((self.records(),self.capture.queued),before)
        self.assertEqual(self.store._read(ownership.reminders.event_key(legacy))['token'],token)

    def test_bare_once_intent_never_falls_through_to_recurring(self):
        p = self.event(start=START+datetime.timedelta(days=8))
        for kind in ('notification','autoplay'):
            with self.subTest(kind=kind):
                self.rule(kind,p)
                always = self.rule(kind,p,1)
                self.schedule()
                before = dict(self.capture.queued),self.records()
                self.cancel(kind,p)
                self.cancel(kind,p)
                self.assertEqual([r[1:] for r in self.rows(kind)],[always])
                self.assertEqual((self.capture.queued,self.records()),before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
