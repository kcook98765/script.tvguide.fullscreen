"""Pure decision/JSON-RPC captures, never Kodi, stubs, a backend or native PASS.

Run with the isolated interpreter's -I -B. Only pvr_recording's stdlib-only
module is loaded; GUI methods are AST-extracted, not legacy-module imported.
"""
import ast
import copy
import datetime
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('pvr_recording', ROOT / 'pvr_recording.py')
pvr = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pvr)
TEXT = 'Café, "News" (日本語) \\ x,RunScript(INERT_MARKER),1,True'
NOW = datetime.datetime(2026, 11, 19, 12, tzinfo=datetime.timezone.utc)
CLIENT = dict(clientid=3, label='Backend ' + TEXT, supportsrecordings=True,
              supportstimers=True, supportsepg=True)
CHANNEL = dict(channelid=41, clientid=3, label=TEXT, channel=TEXT,
               channeltype='tv', isrecording=False)
BROADCAST = dict(broadcastid=901, clientid=3, title=TEXT, label=TEXT,
                 starttime='2026-11-19 13:00:00', endtime='2026-11-19 14:00:00',
                 hastimer=False)
TIMER = dict(timerid=77, clientid=3, channelid=41, title=TEXT, label=TEXT,
             starttime='2026-11-19 13:00:00', endtime='2026-11-19 14:00:00',
             state='scheduled', istimerrule=False, isreadonly=False, isreminder=False)
MUTATIONS = {'PVR.Record', 'PVR.AddTimer', 'PVR.DeleteTimer'}


class Dialog:
    def __init__(self, choices=(0, 0), confirm=True):
        self.choices = iter(choices)
        self.confirm = confirm
        self.calls = []

    def select(self, heading, labels):
        self.calls.append(('select', heading, labels))
        return next(self.choices)

    def yesno(self, heading, message):
        self.calls.append(('confirm', heading, message))
        return self.confirm

    def ok(self, *args):
        self.calls.append(('ok',) + args)


class Capture:
    def __init__(self):
        self.calls = []
        self.available = True
        self.clients = [copy.deepcopy(CLIENT)]
        self.channels = [copy.deepcopy(CHANNEL)]
        self.broadcasts = [copy.deepcopy(BROADCAST)]
        self.timers = [copy.deepcopy(TIMER)]
        self.override = {}

    def __call__(self, raw):
        request = json.loads(raw)
        assert set(request) == {'jsonrpc', 'id', 'method', 'params'}
        assert request['jsonrpc'] == '2.0'
        assert request['id'] == len(self.calls) + 1
        self.calls.append(request)
        method, params = request['method'], request['params']
        if method in self.override:
            return self.override[method](request)
        if method == 'PVR.GetProperties':
            assert params == {'properties': ['available']}
            result = {'available': self.available}
        elif method == 'PVR.GetClients':
            assert params == {}
            result = {'clients': self.clients}
        elif method == 'PVR.GetChannels':
            assert params['properties'] == pvr.CHANNEL_FIELDS
            assert params['channelgroupid'] in ('alltv', 'allradio')
            result = {'channels': self.channels if params['channelgroupid'] == 'alltv' else []}
        elif method == 'PVR.GetChannelDetails':
            assert params == {'channelid': 41, 'properties': pvr.CHANNEL_FIELDS}
            result = {'channeldetails': self.channels[0]}
        elif method == 'PVR.GetBroadcasts':
            assert params == {'channelid': 41, 'properties': pvr.BROADCAST_FIELDS}
            result = {'broadcasts': self.broadcasts}
        elif method == 'PVR.GetBroadcastDetails':
            assert params == {'broadcastid': 901, 'properties': pvr.BROADCAST_FIELDS}
            result = {'broadcastdetails': next(b for b in self.broadcasts
                                               if b['broadcastid'] == params['broadcastid'])}
        elif method == 'PVR.GetTimers':
            assert params == {'properties': pvr.TIMER_FIELDS}
            result = {'timers': self.timers}
        elif method == 'PVR.GetTimerDetails':
            assert params == {'timerid': 77, 'properties': pvr.TIMER_FIELDS}
            result = {'timerdetails': self.timers[0]}
        elif method in MUTATIONS:
            result = 'OK'
        else:
            raise AssertionError('Unexpected method ' + method)
        return json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': result})

    def mutations(self):
        return [(r['method'], r['params']) for r in self.calls if r['method'] in MUTATIONS]


def reply(request, result):
    return json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': result})


class Recording(unittest.TestCase):
    def make(self, choices=(0, 0), confirm=True, module=pvr):
        rpc, dialog = Capture(), Dialog(choices, confirm)
        return rpc, dialog, module.PVRRecording(rpc, dialog, lambda: NOW)

    def assert_no_acceptance(self, rpc, dialog):
        self.assertEqual(rpc.mutations(), [])
        self.assertFalse(any(c[0] == 'ok' and 'Kodi accepted' in str(c) for c in dialog.calls))

    def test_exact_record_now_data_and_non_toggle(self):
        rpc, dialog, recorder = self.make()
        self.assertTrue(recorder.run('now', TEXT))
        self.assertEqual(rpc.mutations(), [('PVR.Record', {'channel': 41, 'record': True})])
        self.assertIn(TEXT, dialog.calls[0][2][0])
        confirmation = next(c[2] for c in dialog.calls if c[0] == 'confirm')
        self.assertIn(TEXT, confirmation)
        self.assertIn('does not schedule', confirmation)
        self.assertEqual(json.loads(json.dumps({'text': TEXT}))['text'], TEXT)
        # Every RPC parameter is fixed structure/IDs, never programme/guide text.
        self.assertNotIn(TEXT, json.dumps(rpc.calls, ensure_ascii=False))

    def test_exact_future_and_manual_selection_not_xmltv_matching(self):
        rpc, dialog, recorder = self.make(choices=(0, 1))
        rpc.broadcasts.insert(0, dict(BROADCAST, broadcastid=900, title='Different title'))
        self.assertTrue(recorder.run('future', 'XMLTV id 888; title is not a broadcast ID'))
        self.assertEqual(rpc.mutations(), [('PVR.AddTimer', {
            'broadcastid': 901, 'timerrule': False, 'reminder': False})])
        self.assertIn('UTC', next(c[2] for c in dialog.calls if c[0] == 'confirm'))
        self.assertEqual(sum(r['method'] == 'PVR.GetBroadcastDetails' for r in rpc.calls), 1)

    def test_cancel_at_every_choice_and_confirmation(self):
        for action, choices in [('menu', (-1,)), ('now', (-1,)),
                                ('future', (0, -1)), ('timers', (-1,)), ('stop', (-1,))]:
            with self.subTest(action=action):
                rpc, dialog, recorder = self.make(choices)
                self.assertFalse(recorder.run(action))
                self.assert_no_acceptance(rpc, dialog)
        for action in ('now', 'future', 'timers', 'stop'):
            rpc, dialog, recorder = self.make(confirm=False)
            rpc.timers[0]['state'] = 'recording'
            self.assertFalse(recorder.run(action))
            self.assert_no_acceptance(rpc, dialog)

    def test_backend_absent_and_capability_not_recordings_alone(self):
        for change in ('unavailable', 'no clients', 'no recordings', 'no timers', 'no epg'):
            for action in ('now', 'future', 'timers'):
                if change == 'no epg' and action != 'future':
                    continue
                rpc, dialog, recorder = self.make()
                if change == 'unavailable':
                    rpc.available = False
                elif change == 'no clients':
                    rpc.clients = []
                else:
                    key = {'no recordings': 'supportsrecordings', 'no timers': 'supportstimers',
                           'no epg': 'supportsepg'}[change]
                    rpc.clients[0][key] = False
                self.assertFalse(recorder.run(action))
                self.assert_no_acceptance(rpc, dialog)
                self.assertTrue(any('backend' in str(c) for c in dialog.calls))

    def test_invalid_real_ids_and_out_of_range_selection(self):
        for bad in (None, True, False, 0, -1, 2**31, '41', 4.1, TEXT):
            self.assertFalse(pvr.valid_id(bad))
            for action, collection, key in [('now', 'channels', 'channelid'),
                                             ('now', 'clients', 'clientid'),
                                             ('future', 'broadcasts', 'broadcastid'),
                                             ('timers', 'timers', 'timerid')]:
                rpc, dialog, recorder = self.make()
                getattr(rpc, collection)[0][key] = bad
                self.assertFalse(recorder.run(action))
                self.assert_no_acceptance(rpc, dialog)
        for bad in (-1, 9999, True, '0', None):
            rpc, dialog, recorder = self.make(choices=(bad,))
            self.assertFalse(recorder.run('now'))
            self.assert_no_acceptance(rpc, dialog)

    def test_past_invalid_time_duplicate_or_other_backend_broadcasts(self):
        for changed in ({'starttime': '2026-11-19 11:00:00'},
                        {'starttime': '2026-11-19 12:00:00'}, {'starttime': 'invalid'},
                        {'endtime': '2026-11-19 12:30:00'}, {'hastimer': True},
                        {'hastimer': None}, {'clientid': 4}, {'clientid': True}):
            rpc, dialog, recorder = self.make()
            rpc.broadcasts[0].update(changed)
            self.assertFalse(recorder.run('future'))
            self.assert_no_acceptance(rpc, dialog)
        rpc, dialog, recorder = self.make()
        rpc.channels[0]['isrecording'] = True
        self.assertFalse(recorder.run('now'))
        self.assert_no_acceptance(rpc, dialog)

    def test_exact_timer_cancellation_and_owned_stop_not_channel_stop(self):
        for action, state in [('timers', 'scheduled'), ('stop', 'recording')]:
            rpc, dialog, recorder = self.make()
            rpc.timers[0]['state'] = state
            rpc.timers.append(dict(TIMER, timerid=78, title='Other recording', state='recording'))
            self.assertTrue(recorder.run(action))
            self.assertEqual(rpc.mutations(), [('PVR.DeleteTimer', {'timerid': 77})])
            confirmation = next(c[2] for c in dialog.calls if c[0] == 'confirm')
            self.assertIn('outside this guide', confirmation)
            self.assertIn('id 77', confirmation)
            if action == 'stop':
                self.assertIn('Stop this recording', confirmation)

    def test_rules_reminders_readonly_and_unknown_timers_view_only(self):
        for changed in ({'istimerrule': True}, {'isreminder': True}, {'isreadonly': True},
                        {'istimerrule': None}, {'isreadonly': 0}, {'state': 'unknown'},
                        {'channelid': -1}):
            rpc, dialog, recorder = self.make()
            rpc.timers[0].update(changed)
            self.assertFalse(recorder.run('timers'))
            self.assert_no_acceptance(rpc, dialog)
            self.assertIn('[view only]', dialog.calls[0][2][0])

    def test_stale_details_backend_or_elapsed_time_refuse(self):
        for action, method, key, item, field, value in [
                ('now', 'PVR.GetChannelDetails', 'channeldetails', CHANNEL, 'clientid', 4),
                ('now', 'PVR.GetChannelDetails', 'channeldetails', CHANNEL, 'channelid', True),
                ('future', 'PVR.GetBroadcastDetails', 'broadcastdetails', BROADCAST, 'title', 'Changed'),
                ('future', 'PVR.GetBroadcastDetails', 'broadcastdetails', BROADCAST, 'hastimer', True),
                ('timers', 'PVR.GetTimerDetails', 'timerdetails', TIMER, 'istimerrule', True),
                ('stop', 'PVR.GetTimerDetails', 'timerdetails', TIMER, 'state', 'scheduled')]:
            rpc, dialog, recorder = self.make()
            rpc.timers[0]['state'] = 'recording' if action == 'stop' else 'scheduled'
            rpc.override[method] = lambda r: reply(r, {key: dict(item, **{field: value})})
            self.assertFalse(recorder.run(action))
            self.assert_no_acceptance(rpc, dialog)
        for action in ('now', 'future', 'timers'):
            rpc, dialog, recorder = self.make()
            count = [0]
            def changed_clients(request):
                count[0] += 1
                return reply(request, {'clients': [CLIENT] if count[0] == 1 else []})
            rpc.override['PVR.GetClients'] = changed_clients
            self.assertFalse(recorder.run(action))
            self.assert_no_acceptance(rpc, dialog)
        rpc, dialog, recorder = self.make()
        times = iter([NOW, NOW.replace(hour=13)])
        recorder.now = lambda: next(times)
        self.assertFalse(recorder.run('future'))
        self.assert_no_acceptance(rpc, dialog)

    def test_rpc_errors_malformed_or_lost_replies_never_success_or_retry(self):
        def lost(request):
            raise RuntimeError('simulated transport loss')
        responses = [lambda r: json.dumps({'jsonrpc': '2.0', 'id': r['id'],
                                          'error': {'code': -32100, 'message': TEXT}}),
                     lambda r: 'not json', lambda r: reply(r, None),
                     lambda r: json.dumps({'jsonrpc': '2.0', 'id': 999, 'result': 'OK'}), lost]
        for action, mutation in [('now', 'PVR.Record'), ('future', 'PVR.AddTimer'),
                                 ('timers', 'PVR.DeleteTimer')]:
            for response in responses:
                rpc, dialog, recorder = self.make()
                rpc.override[mutation] = response
                self.assertFalse(recorder.run(action))
                self.assertEqual(len(rpc.mutations()), 1)  # uncertain dispatch is not retried
                self.assertFalse(any('Kodi accepted' in str(c) for c in dialog.calls))
            for read in ('PVR.GetProperties', 'PVR.GetClients',
                         'PVR.GetTimers' if action == 'timers' else 'PVR.GetChannels'):
                rpc, dialog, recorder = self.make()
                rpc.override[read] = responses[0]
                self.assertFalse(recorder.run(action))
                self.assert_no_acceptance(rpc, dialog)

    def test_oracle_negative_controls_reject_unintended_mutations(self):
        # Deliberately break one real decision/payload at a time, in memory only.
        source = (ROOT / 'pvr_recording.py').read_text()
        cases = [("record=True)", "record=False)", 'now', True,
                  [('PVR.Record', {'channel': 41, 'record': True})]),
                 ('timerrule=False, reminder=False)', 'timerrule=True, reminder=False)', 'future', True,
                  [('PVR.AddTimer', {'broadcastid': 901, 'timerrule': False, 'reminder': False})]),
                 ("timerid=timer['timerid'])", "timerid=78)", 'timers', True,
                  [('PVR.DeleteTimer', {'timerid': 77})]),
                 ("if not self.dialog.yesno('Confirm Kodi PVR recording', question):",
                  "if False:", 'now', False, [])]
        for old, new, action, confirm, expected in cases:
            self.assertEqual(source.count(old), 1)
            scope = {}
            exec(compile(source.replace(old, new), '<inert-pvr-negative-control>', 'exec'), scope)
            rpc, dialog, recorder = self.make(confirm=confirm, module=SimpleNamespace(**scope))
            recorder.run(action)
            with self.assertRaises(AssertionError):
                self.assertEqual(rpc.mutations(), expected)
            print('DETECTED unintended mutation control:', action, new)

    def test_extracted_gui_adapters_and_entry_surfaces(self):
        source = (ROOT / 'gui.py').read_text()
        tree = ast.parse(source)
        guide = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'TVGuide')
        names = {'playWithChannel', 'stopWith', 'showAutoplaywiths', 'showFullAutoplaywiths'}
        nodes = [copy.deepcopy(n) for n in guide.body if isinstance(n, ast.FunctionDef) and n.name in names]
        calls = []
        class Recorder:
            def __init__(self, execute, dialog):
                pass
            def run(self, *args, **kwargs):
                calls.append((args, kwargs))
        # Replace only the local import of the pure module; no Kodi/legacy import.
        for node in nodes:
            node.body = [n for n in node.body if not isinstance(n, ast.ImportFrom)]
        scope = {'PVRRecording': Recorder,
                 'xbmc': SimpleNamespace(executeJSONRPC=None),
                 'xbmcgui': SimpleNamespace(Dialog=lambda: None)}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<gui-adapters>', 'exec'), scope)
        ui = SimpleNamespace(**{name: None for name in names})
        ui.showFullAutoplaywiths = lambda: scope['showFullAutoplaywiths'](ui)
        scope['playWithChannel'](ui, SimpleNamespace(title=TEXT),
                                  SimpleNamespace(title=TEXT, startDate='guide-time'))
        self.assertIn(TEXT, calls[-1][1]['guide_hint'])
        scope['stopWith'](ui)
        self.assertEqual(calls[-1], (('stop',), {}))
        scope['showAutoplaywiths'](ui)
        self.assertEqual(calls[-1], (('timers',), {}))
        # Entry decisions stay in the real GUI source; AST only, no WindowXML.
        self.assertIn('action.getId() == ACTION_RECORD', source)
        self.assertIn("schedulers = [remind,autoplay,'Record (Kodi PVR)…']", source)
        self.assertIn('"AutoPlays", "PVR timers / cancel"', source)
        context = source[source.index('elif buttonClicked == PopupMenu.C_POPUP_AUTOPLAYWITH:'):]
        self.assertTrue(context.split('\n')[1].strip() == 'self.playWithChannel(program.channel, program)')
        editor = ast.parse((ROOT / 'ActionEditor.py').read_text())
        function = next(n for n in editor.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'getCommandActions')
        aliases = {'PLAY_AUTOPLAYWITH': [170], 'STOP_AUTOPLAYWITH': [13],
                   'AUTOPLAYWITHS': [14], 'EXTENDED_INFO': [15]}
        file = SimpleNamespace(read=lambda: json.dumps(aliases), close=lambda: None)
        namespace = {'COMMANDS': {key: [] for key in aliases}, 'ACTIONS': {}, 'json': json,
                     'xbmcvfs': SimpleNamespace(File=lambda *args: file)}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<keymap-adapter>', 'exec'), namespace)
        result = namespace['getCommandActions']()
        self.assertEqual(result, aliases)  # Metadata alias now opens fixed provider choices.


if __name__ == '__main__':
    unittest.main(verbosity=2)
