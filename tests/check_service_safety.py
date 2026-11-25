"""Focused AST-extracted service paths; no Kodi/stub/legacy module imports.

Baseline deletions are inspected as data ONLY. Current main/callback paths use
inert API captures and disposable sentinel files, not real SQLite/profile data.
"""
import ast
import datetime
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = '6d1b9162289ccc20c3ba089302dc3a149150d0be'
TEXT = (ROOT / 'service.py').read_text()
TREE = ast.parse(TEXT, feature_version=(3, 8))
NOW = datetime.datetime(2026, 11, 20, 12, 0)
FOLDER_COMMAND = 'RunScript(special://home/addons/script.tvguide.fullscreen/ReloadAddonFolders.py)'


def execute(nodes, namespace):
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<service-path-capture>', 'exec'), namespace)


def helper():
    namespace = {'datetime': datetime}
    execute([next(n for n in TREE.body if isinstance(n, ast.FunctionDef)
                  and n.name == '_time_left')], namespace)
    return namespace['_time_left']


class Settings:
    def __init__(self, values):
        self.values = dict(values)
        self.writes = []

    def getSetting(self, key):
        return self.values.get(key, '')

    def setSetting(self, key, value):
        self.writes.append((key, value))
        self.values[key] = value

    def getAddonInfo(self, key):
        return {'version': 'test-version', 'path': 'inert-addon-path'}[key]


def capture(values, abort_on_wait=True, abort_before_trigger=False, stop_after_update=True):
    addon = Settings(dict({'last.background.update': str(NOW.timestamp())}, **values))
    calls, waits, logs, deletes = [], [], [], []

    class Monitor:
        polls = 0

        def abortRequested(self):
            self.polls += 1
            return (abort_before_trigger and self.polls >= 2) or (stop_after_update and 'update' in calls)

        def waitForAbort(self, seconds):
            waits.append(seconds)
            return abort_on_wait

    with tempfile.TemporaryDirectory(prefix='service-sentinels-') as directory:
        root = Path(directory)
        sentinels = {name: b'untouched-' + name.encode() for name in ('source.db-journal', 'db.lock', 'source.db')}
        for name, data in sentinels.items():
            (root / name).write_bytes(data)

        def delete(path):
            deletes.append(path)
            (root / path.rsplit('/', 1)[-1]).unlink()

        namespace = {
            '__name__': '__main__', 'datetime': SimpleNamespace(datetime=SimpleNamespace(now=lambda: NOW)),
            '_time_left': helper(), 'time': SimpleNamespace(time=lambda: NOW.timestamp()),
            'xbmcaddon': SimpleNamespace(Addon=lambda _: addon),
            'xbmc': SimpleNamespace(Monitor=Monitor, LOGDEBUG=0,
                                    log=lambda *args: logs.append(args),
                                    executebuiltin=lambda command: calls.append(command)),
            'xbmcvfs': SimpleNamespace(delete=delete),
            'source': SimpleNamespace(SourceNotConfiguredException=type('NotConfigured', (Exception,), {})),
            'Service': lambda: calls.append('update'),
        }
        main = next(n for n in TREE.body if isinstance(n, ast.If))
        execute(main.body, namespace)
        assert not deletes, deletes
        assert {name: (root / name).read_bytes() for name in sentinels} == sentinels
    assert not any('Uncaught exception' in str(log) for log in logs), logs
    return addon, calls, waits


class ServiceSafety(unittest.TestCase):
    def test_original_defects_as_bounded_negative_controls(self):
        baseline = subprocess.check_output(['git', 'show', BASE + ':service.py'], cwd=ROOT, text=True)
        tree = ast.parse(baseline)
        main = next(n for n in tree.body if isinstance(n, ast.If))
        # These actual unconditional statements are DATA, never executed.
        deletes = [n for n in main.body if isinstance(n, ast.Expr)
                   and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute)
                   and n.value.func.attr == 'delete']
        self.assertEqual(len(deletes), 2)
        for node in deletes:
            print('DETECTED baseline ownership-blind startup call:', ast.get_source_segment(baseline, node))
        loop = next(n for n in ast.walk(main) if isinstance(n, ast.While))
        schedule = loop.body[0]
        for values, error in [({'service.time': ''}, NameError),
                              ({'service.time': 'bad'}, IndexError),
                              ({'service.time': '25:00'}, ValueError),
                              ({'service.type': '0', 'service.interval': 'bad'}, ValueError),
                              ({'service.type': '0', 'service.interval': '1',
                                'last.background.update': 'bad'}, ValueError)]:
            namespace = {'ADDON': Settings(values), 'datetime': datetime,
                         'xbmc': SimpleNamespace(log=lambda *args: None, LOGDEBUG=0)}
            with self.assertRaises(error):
                execute([schedule] + ast.parse('timeLeft').body, namespace)
            print('DETECTED baseline schedule failure:', values, error.__name__)
        namespace = {'ADDON': Settings({'service.type': 'Period', 'service.time': '03:33'}),
                     'datetime': datetime}
        execute([schedule], namespace)
        self.assertNotIn('waitTime', namespace)  # Legacy period default took daily branch.
        print('DETECTED baseline Period default selects daily branch')
        triggered = []
        # At zero delay the old tail dispatches even with an already requested
        # abort. Extract only that tail into a one-iteration loop (break is legal).
        namespace = {'timeLeft': 0, 'ADDON': Settings({}), 'time': SimpleNamespace(time=lambda: 1),
                     'monitor': SimpleNamespace(abortRequested=lambda: True),
                     'xbmc': SimpleNamespace(log=lambda *args: None, LOGDEBUG=0),
                     'Service': lambda: triggered.append('update')}
        one = ast.For(target=ast.Name(id='_', ctx=ast.Store()),
                      iter=ast.Tuple(elts=[ast.Constant(value=0)], ctx=ast.Load()),
                      body=loop.body[1:], orelse=[])
        execute([ast.fix_missing_locations(one)], namespace)
        self.assertEqual(triggered, ['update'])
        print('DETECTED baseline zero-wait dispatch despite requested abort')

    def test_period_and_daily_arithmetic(self):
        remaining = helper()
        last = str(NOW.timestamp())
        for kind in ('0', 'Period', '', 'unknown'):
            for interval, seconds in [('0', 7200), ('1', 21600), ('2', 43200), ('3', 86400),
                                      ('', 21600), ('bad', 21600), ('9', 21600)]:
                self.assertEqual(remaining(kind, interval, '', last, NOW), seconds)
        for kind in ('1', 'Time'):
            self.assertEqual(remaining(kind, '', '13:30', '', NOW), 5400)
            self.assertEqual(remaining(kind, '', '03:33', '', NOW), 55980)
            self.assertEqual(remaining(kind, '', '12:00', '', NOW), 0)
            self.assertEqual(remaining(kind, '', '1:02', '', NOW), 46920)
        self.assertEqual(remaining('0', '1', '', str((NOW - datetime.timedelta(days=2)).timestamp()), NOW), 0)

    def test_malformed_fallbacks(self):
        remaining = helper()
        for value in ('', 'bad', '12', '25:00', '12:60', ':', 'nan:inf'):
            self.assertEqual(remaining('1', '', value, '', NOW), 55980)
        for value in ('', 'bad', 'nan', 'inf', '-inf', '1e300', '-1e300'):
            self.assertEqual(remaining('0', '1', '', value, NOW), 0)

    def test_startup_sentinels_and_abort(self):
        # Full main-body captures, including both settings disabled and autostart.
        for values in ({}, {'autostart': 'false', 'background.service': 'false'},
                       {'autostart': 'true'}, {'background.service': 'true', 'service.type': 'Period'},
                       {'background.service': 'true', 'service.type': '1', 'service.time': 'bad'}):
            _, calls, _ = capture(values)
            self.assertEqual(calls, ['RunAddon(script.tvguide.fullscreen)'] if values.get('autostart') == 'true' else [])
        addon, calls, waits = capture({'background.service': 'true', 'background.startup': 'true',
                                      'service.addon.folders': 'true', 'service.type': '0'})
        self.assertEqual(calls, ['update', FOLDER_COMMAND])
        self.assertEqual(waits, [])
        self.assertIn('last.background.update', dict(addon.writes))
        values = {'background.service': 'true', 'service.type': '0', 'service.interval': 'bad',
                  'last.background.update': 'bad', 'service.addon.folders': 'true'}
        addon, calls, waits = capture(values, abort_on_wait=False)
        self.assertEqual(calls, ['update', FOLDER_COMMAND])
        self.assertEqual(waits, [])  # Already due; no added delay or polling loop.
        self.assertEqual([key for key, _ in addon.writes], ['version', 'last.background.update'])
        _, calls, waits = capture(values, stop_after_update=False)
        self.assertEqual(calls, ['update', FOLDER_COMMAND])
        self.assertEqual(waits, [21600])  # Fresh history restores a real abortable interval.
        _, calls, waits = capture(values, abort_before_trigger=True)
        self.assertEqual(calls, [])  # Abort arriving on the zero-wait path.
        _, calls, waits = capture({'background.service': 'true', 'service.type': '1', 'service.time': 'bad'})
        self.assertEqual(calls, [])
        self.assertEqual(len(waits), 1)
        self.assertGreater(waits[0], 0)

    def test_retained_callbacks_and_ownership_source(self):
        for relative in ('service.py', 'tests/check_service_safety.py', 'tests/check_command_data.py'):
            ast.parse((ROOT / relative).read_text(), filename=relative, feature_version=(3, 8))
        klass = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Service')
        callback = next(n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == 'onCachesUpdated')
        calls = []
        addon = Settings({'notifications.enabled': 'true', 'autoplays.enabled': 'true', 'background.notify': 'true'})
        namespace = {'ADDON': addon,
                     'notification': SimpleNamespace(Notification=lambda *args: SimpleNamespace(scheduleNotifications=lambda: calls.append('reminder'))),
                     'autoplay': SimpleNamespace(Autoplay=lambda *args: SimpleNamespace(scheduleAutoplays=lambda: calls.append('autoplay'))),
                     'xbmcgui': SimpleNamespace(Dialog=lambda: SimpleNamespace(notification=lambda *args: calls.append(args))),
                     'xbmc': SimpleNamespace(log=lambda *args: None, LOGINFO=1)}
        execute([callback], namespace)
        namespace['onCachesUpdated'](SimpleNamespace(database=SimpleNamespace(close=lambda arg: calls.append(('close', arg)))))
        self.assertEqual(calls, ['reminder', 'autoplay', ('close', None), ('TV Guide Fullscreen', 'Finished Updating')])
        # Trace the existing marker lifecycle, without calling any DB code. This
        # is not a claim of atomic lock acquisition or crash-safe marker cleanup.
        text = (ROOT / 'source.py').read_text()
        self.assertIn("if xbmcvfs.exists(lock):\n            return", text)
        self.assertIn("xbmcvfs.File(lock,'wb')", text)
        # Cleanup is now inside finally, including XMLTV cancellation/rollback.
        self.assertIn('finally:\n            self.updateInProgress = False\n            c.close()\n            xbmcvfs.delete(lock)', text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
