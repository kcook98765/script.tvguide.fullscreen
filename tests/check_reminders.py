"""Bounded pure JSON/command captures + extracted reminder-method wiring.

No Kodi/stub imports or legacy module initialization. Nothing displays or runs
an alarm. Temp profile data is disposable; hostile examples are inert strings.
"""
import ast
from concurrent.futures import ThreadPoolExecutor
import datetime
import importlib.util
import json
from pathlib import Path
import re
import tempfile
from types import SimpleNamespace
from typing import List
import unittest

ROOT = Path(__file__).resolve().parents[1]


def pure(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


data = pure('reminder_data')
safe = pure('command_safety')
START = 1800000000
VALUES = ["Doctor's diary", 'He said "Hello"', 'News, Weather & Sport',
          'Film (1999)', 'Café — 日本語 📺', r'C:\Kodi\addons\icon.png',
          'x,RunScript(INERT_MARKER),1,True']


class Reminders(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='tvguide-reminder-test-')
        self.addCleanup(self.temp.cleanup)
        self.store = data.ReminderData(self.temp.name)
        self.name = safe.alarm_name('notification', VALUES[0], '2026-11-20 12:00:00')

    def save(self, value='Title'):
        return self.store.save(self.name, value, 'Soon: ' + value, 'Now: ' + value, value, START)

    def test_original_failures_and_exact_data(self):
        for value in VALUES:
            with self.subTest(value=value):
                if value != 'Café — 日本語 📺':
                    self.assertFalse(safe.is_builtin_data(value))
                    print('DETECTED old guard rejects:', repr(value))
                self.store.cancel(self.name)
                token = self.save(value)
                self.assertRegex(token, r'\A[0-9a-f]{96}\Z')
                raw = (Path(self.store.directory) / (token[:64] + '.json')).read_bytes()
                self.assertEqual(json.loads(raw.decode('utf-8'))['title'], value)
                for phase, minutes, now in [('5mins', 5, START - 300), ('now', 10, START)]:
                    command = data.alarm_command(self.name, token, phase, minutes)
                    self.assertEqual(command, 'AlarmClock(%s-%s,RunScript(%s,%s,%s),%d,True)' %
                                     (self.name, phase, data.CALLBACK, token, phase, minutes))
                    self.assertNotIn(value, command)
                    self.assertRegex(command, r'\AAlarmClock\(tvguide-notification-[0-9a-f]{64}-(5mins|now),'
                                     r'RunScript\(special://home/addons/script\.tvguide\.fullscreen/'
                                     r'reminder_callback\.py,[0-9a-f]{96},\1\),[0-9]+,True\)\Z')
                    calls = []
                    self.assertTrue(data.deliver(self.store, token, phase, now, lambda *args: calls.append(args)))
                    self.assertEqual(calls, [(value, ('Soon: ' if phase == '5mins' else 'Now: ') + value,
                                              value, 10000, True)])
                    print('PASS exact data/captured API call:', phase, repr(calls[0]))

    def test_duplicate_reconstruction_cancel_and_readd(self):
        token = self.save()
        self.assertIsNotNone(self.store.take(token, '5mins', START - 300))
        # A new service instance/reconstructed alarms reuse identity and claims.
        self.store = data.ReminderData(self.temp.name)
        self.assertEqual(self.save(), token)
        self.assertIsNone(self.store.take(token, '5mins', START - 300))
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.store.take(token, 'now', START), range(2)))
        self.assertEqual(sum(result is not None for result in results), 1)
        self.store.cancel(self.name)
        self.assertIsNone(self.store.take(token, 'now', START))
        replacement = self.save()
        self.assertNotEqual(replacement, token)
        self.assertIsNone(self.store.take(token, 'now', START))
        self.assertIsNotNone(self.store.take(replacement, 'now', START))
        self.assertEqual(self.store.clear(), [self.name])
        self.assertIsNone(self.store.take(replacement, '5mins', START - 300))

    def test_invalid_phase_token_time_and_bounded_json(self):
        token = self.save()
        for bad in ['', '../x', 'a' * 95, 'a' * 96 + '\n', 'x,RunScript(INERT_MARKER)', None]:
            self.assertIsNone(self.store.take(bad, 'now', START))
            with self.assertRaises(ValueError):
                data.alarm_command(self.name, bad, 'now', 10)
        for phase in ['../now', 'now,RunScript(INERT_MARKER)', 'stop', 'NOW', '']:
            self.assertIsNone(self.store.take(token, phase, START))
            with self.assertRaises(ValueError):
                data.alarm_command(self.name, token, phase, 10)
        for phase, now in [('5mins', START - 361), ('now', START - 61)]:
            self.assertIsNone(self.store.take(token, phase, now))
        for minutes in [-1, True, '10', 1.5]:
            with self.assertRaises(ValueError):
                data.alarm_command(self.name, token, 'now', minutes)
        with self.assertRaises(ValueError):
            data.alarm_command('other-name', token, 'now', 10)
        with self.assertRaises(ValueError):
            data.alarm_command('tvguide-notification-' + '0' * 64, token, 'now', 10)
        with self.assertRaises(ValueError):
            self.save('x' * 16001)
        path = Path(self.store.directory) / (token[:64] + '.json')
        original = json.loads(path.read_text())
        for changed in [dict(original, title=7), dict(original, start=True),
                        dict(original, start=float('nan')), dict(original, start=10 ** 400),
                        dict(original, action='exec'),
                        dict(original, token='b' * 96)]:
            path.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):
                self.store.take(token, 'now', START)
        for raw in [b'\xff', b'[]', b'{bad', b'[' * 2000 + b']' * 2000,
                    b' ' * (data.MAX_BYTES + 1)]:
            path.write_bytes(raw)
            with self.assertRaises((ValueError, UnicodeError)):
                self.store.take(token, 'now', START)
        self.store.cancel(self.name)  # Even malformed data can be cancelled.
        token = self.save()
        self.store.prune_completed(START + 601)
        self.assertEqual(self.store.names(), [self.name])  # Pending is not expired.
        self.assertTrue(data.deliver(self.store, token, 'now', START + 86400, lambda *args: None))
        self.assertTrue(data.deliver(self.store, token, '5mins', START + 86400, lambda *args: None))
        self.store.prune_completed(START + 86401)
        self.assertEqual(self.store.names(), [])
        self.assertIsNone(self.store.take(token, 'now', START + 601))
        token = self.store.save(self.name, 'Title', 'Soon', 'Now', 'Icon', START, False)
        self.assertIsNone(self.store.take(token, '5mins', START - 300))
        self.assertTrue(data.deliver(self.store, token, 'now', START + 86400, lambda *args: None))
        self.store.prune_completed(START + 86401)
        self.assertEqual(self.store.names(), [])

    def test_cleanup_keeps_inflight_phase(self):
        token = self.save()
        self.assertTrue(data.deliver(self.store, token, '5mins', START - 300, lambda *args: None))
        calls = []

        def notify(*args):
            self.store.prune_completed(START + 1)
            self.assertEqual(self.store.names(), [self.name])
            calls.append(args)

        self.assertTrue(data.deliver(self.store, token, 'now', START + 1, notify))
        self.assertEqual(len(calls), 1)
        self.store.prune_completed(START + 2)
        self.assertEqual(self.store.names(), [])

    def test_scheduler_method_captures(self):
        # Only this reviewed class is compiled, not notification.py's imports or
        # __main__/DB init. The constructor is NOT executed on the host.
        tree = ast.parse((ROOT / 'notification.py').read_text())
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'Notification')
        clock = datetime.datetime(2026, 11, 20, 12)

        class Clock(datetime.datetime):
            @classmethod
            def now(cls):
                return clock

        calls = []
        env = dict(datetime=SimpleNamespace(datetime=Clock), alarm_name=safe.alarm_name,
                   alarm_command=data.alarm_command, xbmc=SimpleNamespace(executebuiltin=calls.append),
                   strings=lambda phase, channel: '%s: %s' % (phase, channel),
                   NOTIFICATION_5_MINS='Soon', NOTIFICATION_NOW='Now',
                   time=SimpleNamespace(time=lambda: clock.timestamp()))
        exec(compile(ast.Module(body=[cls], type_ignores=[]), 'notification.py:class-only', 'exec'), env)
        n = env['Notification'].__new__(env['Notification'])
        n.reminders, n.icon = self.store, r'C:\Kodi\icon.png'
        title, channel = VALUES[0], VALUES[2]
        start = clock + datetime.timedelta(minutes=10, seconds=30)
        program = SimpleNamespace(title=title, channel=SimpleNamespace(title=channel, id='not-display-id'), startDate=start)
        programs = [program]
        n.database = SimpleNamespace(getFullNotifications=lambda: list(programs),
                                     addNotification=lambda p, t: programs.append(p),
                                     removeNotification=lambda p: programs.__setitem__(
                                         slice(None), [item for item in programs if item.title != p.title]),
                                     clearAllNotifications=programs.clear)
        n.scheduleNotifications()
        name = n.createAlarmClockName(title, start)
        record = self.store._read(data.event_key(name))
        token = record['token']
        self.assertEqual(record['5mins'], 'Soon: ' + channel)
        self.assertEqual(calls, [data.alarm_command(name, token, '5mins', 5),
                                 data.alarm_command(name, token, 'now', 10)])
        recurring = SimpleNamespace(title=title, channel=program.channel, startDate=start + datetime.timedelta(days=1))
        survivor = SimpleNamespace(title='Other title', channel=program.channel, startDate=start)
        n.addNotification(recurring, 1)
        n.addNotification(survivor, 0)
        n.removeNotification(program)
        self.assertEqual(calls[-2:], ['CancelAlarm(%s-5mins,True)' % name, 'CancelAlarm(%s-now,True)' % name])
        recurring_name = n.createAlarmClockName(recurring.title, recurring.startDate)
        self.assertIn('CancelAlarm(%s-now,True)' % recurring_name, calls)
        self.assertEqual(self.store.names(), [n.createAlarmClockName(survivor.title, survivor.startDate)])
        self.assertIsNone(self.store.take(token, 'now', start.timestamp()))
        calls.clear()
        n.addNotification(program, 0)
        n.clearNotifications()
        self.assertEqual(programs, [])
        self.assertEqual(self.store.names(), [])
        calls.clear()
        n._scheduleNotification(channel, title, clock + datetime.timedelta(minutes=2))
        self.assertEqual(len(calls), 1)
        self.assertIn(',now),2,True)', calls[0])
        calls.clear()
        n._scheduleNotification(channel, title, clock - datetime.timedelta(seconds=1))
        self.assertEqual(calls, [])

    def test_fixed_callback_wiring(self):
        text = (ROOT / 'reminder_callback.py').read_text()
        tree = ast.parse(text)
        imports = {alias.name for n in ast.walk(tree) if isinstance(n, ast.Import) for alias in n.names}
        self.assertEqual(imports, {'sys', 'time', 'xbmc', 'xbmcaddon', 'xbmcgui', 'xbmcvfs'})
        self.assertNotIn('executebuiltin', text)
        self.assertIn('xbmcgui.Dialog().notification', text)
        self.assertIn("getAddonInfo('profile')", text)
        self.assertIn('len(argv) != 3', text)
        self.assertIn('valid_token(argv[1])', text)
        self.assertIn('argv[2] not in PHASES', text)
        calls, addon_calls = [], []

        def addon(identifier):
            addon_calls.append(identifier)
            return SimpleNamespace(getAddonInfo=lambda key: self.temp.name if key == 'profile' else None)

        env = dict(List=List, valid_token=data.valid_token, PHASES=data.PHASES,
                   ReminderData=data.ReminderData, deliver=data.deliver,
                   xbmcaddon=SimpleNamespace(Addon=addon),
                   xbmcvfs=SimpleNamespace(translatePath=lambda path: path),
                   xbmcgui=SimpleNamespace(Dialog=lambda: SimpleNamespace(notification=lambda *args: calls.append(args))),
                   time=SimpleNamespace(time=lambda: START),
                   xbmc=SimpleNamespace(LOGERROR=4, log=lambda *args: calls.append(('LOG', args))))
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
        exec(compile(ast.Module(body=[main], type_ignores=[]), 'reminder_callback.py:main-only', 'exec'), env)
        token = self.save(VALUES[-1])
        for argv in [[], ['callback'], ['callback', '../x', 'now'],
                     ['callback', token, 'other'], ['callback', token, 'now', 'extra']]:
            env['main'](argv)
        self.assertEqual(addon_calls, [])
        env['main'](['callback', token, 'now'])
        env['main'](['callback', token, 'now'])  # Duplicate does not display.
        self.assertEqual(addon_calls, ['script.tvguide.fullscreen'] * 2)
        self.assertEqual(calls, [(VALUES[-1], 'Now: ' + VALUES[-1], VALUES[-1], 10000, True)])


if __name__ == '__main__':
    unittest.main(verbosity=2)
