"""Focused pure/AST captures, not Kodi execution or legacy/stub imports.

Only autoplay_data/command_safety are imported. Reviewed class/functions are
extracted without their module imports, globals initialization or __main__.
All commands and Player calls below are inert captures, not a Kodi emulator.
"""
import ast
import base64
import datetime
import importlib.util
from pathlib import Path
import re
import sqlite3
import subprocess
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = 'c96189c7a7a9d5ad20f8946d280166be0aa15e69'
VALUES = ["Doctor's channel", 'News, Weather', 'Film (HD)', 'He said "hi"',
          r'C:\TV\station', 'Café — 日本語 📺', 'x,RunScript(INERT_MARKER),1,True',
          '@ActivateWindow(INERT_MARKER)', 'v1_an_old_channel', 'line\nzero\x00end']


def pure(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


data, safe = pure('autoplay_data'), pure('command_safety')


def extracted(path, name, env):
    tree = ast.parse((ROOT / path).read_text())
    node = next(n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), path + ':extracted', 'exec'), env)
    return env[name]


def packet(value):
    return 'v1_' + base64.urlsafe_b64encode(value).decode('ascii').rstrip('=')


class AutoPlay(unittest.TestCase):
    def scheduler(self):
        self.clock = datetime.datetime(2026, 11, 20, 12)
        now = self.clock

        class Clock(datetime.datetime):
            @classmethod
            def now(cls):
                return now

        self.calls, self.logs = [], []
        self.settings = {'autoplays.before': '2', 'autoplays.after': '3', 'autoplays.stop': 'true'}
        env = dict(datetime=SimpleNamespace(datetime=Clock), alarm_name=safe.alarm_name,
                   encode_identity=data.encode_identity,
                   xbmc=SimpleNamespace(executebuiltin=self.calls.append, LOGERROR=4,
                                        log=lambda *args: self.logs.append(args)),
                   ADDON=SimpleNamespace(getSetting=lambda key: self.settings[key]))
        cls = extracted('autoplay.py', 'Autoplay', env)
        self.n = cls.__new__(cls)
        self.programs, self.added = [], []
        self.n.database = SimpleNamespace(
            getFullAutoplays=lambda: list(self.programs),
            addAutoplay=lambda p, t: (self.programs.append(p), self.added.append((p, t))),
            removeAutoplay=lambda p: self.programs.__setitem__(slice(None), [
                item for item in self.programs if (item.title, item.channel.id) != (p.title, p.channel.id)]),
            clearAllAutoplays=self.programs.clear)
        return self.n

    def program(self, channel='Station', days=0, title='Show, (HD)'):
        start = self.clock + datetime.timedelta(days=days, minutes=10, seconds=30)
        return SimpleNamespace(channel=SimpleNamespace(id=channel), title=title,
                               startDate=start, endDate=start + datetime.timedelta(minutes=30))

    def callbacks(self):
        self.effects, self.markers = [], {}
        effects, markers = self.effects, self.markers
        addon = SimpleNamespace(getSetting=lambda key: markers.get(key, ''),
                                setSetting=lambda key, val: (effects.append(('setting', key, val)),
                                                             markers.__setitem__(key, val)))
        # Real stdlib SQLite query, in-memory only. No provider/guide DB init.
        conn = sqlite3.connect(':memory:')
        self.addCleanup(conn.close)
        conn.execute('CREATE TABLE custom_stream_url(channel TEXT, stream_url TEXT)')
        self.db = conn

        def connect(*args, **kwargs):
            effects.append(('connect', args, kwargs))
            return SimpleNamespace(cursor=conn.cursor, close=lambda: effects.append(('close',)))

        env = dict(callback_identity=data.callback_identity,
                   xbmc=SimpleNamespace(LOGERROR=4, log=lambda *args: effects.append(('log', args)),
                                        Player=lambda: SimpleNamespace(play=lambda **kw: effects.append(('play', kw))),
                                        executebuiltin=lambda value: effects.append(('builtin', value)),
                                        getCondVisibility=lambda cond: False),
                   xbmcaddon=SimpleNamespace(Addon=lambda **kw: (effects.append(('addon',)), addon)[1]),
                   xbmcvfs=SimpleNamespace(translatePath=lambda path: (effects.append(('path', path)), path)[1]),
                   sqlite3=SimpleNamespace(connect=connect, PARSE_DECLTYPES=sqlite3.PARSE_DECLTYPES))
        return extracted('play.py', 'main', dict(env)), extracted('stop.py', 'main', dict(env))

    def test_producer_roundtrip_timing_reconstruction_and_optional_stop(self):
        n = self.scheduler()
        for value in VALUES:
            self.calls.clear()
            p = self.program(channel=value)
            n.addAutoplay(p, 0)
            name = n.createAlarmClockName(p.title, p.startDate)
            token = data.encode_identity(value, str(p.startDate))
            self.assertEqual(data.decode_identity(token), (value, str(p.startDate)))
            self.assertEqual(self.calls, [
                'AlarmClock(%s-start,RunScript(special://home/addons/script.tvguide.fullscreen/play.py,%s),8,True)' % (name, token),
                'AlarmClock(%s-stop,RunScript(special://home/addons/script.tvguide.fullscreen/stop.py,%s),43,True)' % (name, token)])
            for command in self.calls:
                self.assertRegex(command, r'\AAlarmClock\(tvguide-autoplay-[0-9a-f]{64}-(start|stop),'
                                 r'RunScript\(special://home/addons/script\.tvguide\.fullscreen/'
                                 r'(play|stop)\.py,v1_[A-Za-z0-9_-]+\),[0-9]+,True\)\Z')
                self.assertNotIn(value, command)
                self.assertNotIn(str(p.startDate), command)
            print('PASS exact encoded producer data:', repr(value))
        # Service reconstruction emits identical commands for existing DB events.
        self.calls.clear()
        self.programs[:] = [p]
        n.scheduleAutoplays()
        reconstructed = list(self.calls)
        self.calls.clear()
        n._scheduleAutoplay(p.channel.id, p.title, p.startDate, p.endDate)
        self.assertEqual(self.calls, reconstructed)
        self.settings['autoplays.stop'] = 'false'
        self.calls.clear()
        n.scheduleAutoplays()
        self.assertEqual(self.calls, reconstructed[:1])
        # Preserve old floor rounding, negative padding and past-start skip.
        self.calls.clear()
        n._scheduleAutoplay('Station', 'Soon', self.clock + datetime.timedelta(seconds=30), p.endDate)
        self.assertTrue(self.calls[0].endswith(',-2,True)'))
        self.calls.clear()
        n._scheduleAutoplay('Station', 'Past', self.clock - datetime.timedelta(seconds=1), p.endDate)
        self.assertEqual(self.calls, [])
        n._scheduleAutoplay('x' * (data.MAX_BYTES + 1), 'Oversize', p.startDate, p.endDate)
        self.assertEqual(self.calls, [])
        self.assertEqual(len(self.logs), 1)

    def test_callbacks_exact_parameterized_lookup_media_and_ownership(self):
        play, stop = self.callbacks()
        start = '2026-11-20 12:10:30.123456'
        url = 'plugin://demo/a,b(HD)"quoted"\\Café'
        for value in VALUES:
            self.db.execute('INSERT INTO custom_stream_url VALUES (?, ?)', (value, url))
            argv = ['callback.py', data.encode_identity(value, start)]
            self.effects.clear()
            play(argv)
            self.assertEqual(self.markers, {'playing.channel': value, 'playing.start': start})
            self.assertIn(('play', {'item': url}), self.effects)
            self.assertFalse(any(e[0] == 'builtin' for e in self.effects))
            self.effects.clear()
            stop(['stop.py', data.encode_identity(value, 'other start')])
            stop(['stop.py', data.encode_identity('other channel', start)])
            self.assertFalse(any(e[0] in ('setting', 'builtin', 'play') for e in self.effects))
            self.effects.clear()
            stop(argv)
            self.assertEqual(self.effects[-1], ('builtin', 'PlayerControl(Stop)'))
            self.assertEqual(self.markers, {'playing.channel': '', 'playing.start': ''})
        # Legacy parsed data remains supported, even if an ID looks encoded.
        token_id = data.encode_identity('not the channel', start)
        self.db.execute('INSERT INTO custom_stream_url VALUES (?, ?)', (token_id, url))
        play(['play.py', token_id, start])
        self.assertEqual(self.markers['playing.channel'], token_id)
        stop(['stop.py', token_id, start])
        self.assertEqual(self.markers['playing.channel'], '')
        # Unknown mapping changes no playback markers and does not play.
        self.effects.clear()
        play(['play.py', data.encode_identity('unmapped', start)])
        self.assertFalse(any(e[0] in ('setting', 'builtin', 'play') for e in self.effects))
        # Raw command-looking mappings are only Player data, never interpreted.
        for mapping in ['@RunScript(INERT_MARKER)', 'ActivateWindow(INERT_MARKER)',
                        'RunScript(INERT_MARKER)']:
            self.db.execute('DELETE FROM custom_stream_url')
            self.db.execute('INSERT INTO custom_stream_url VALUES (?, ?)', ('Station', mapping))
            self.effects.clear()
            play(['play.py', data.encode_identity('Station', start)])
            self.assertIn(('play', {'item': mapping}), self.effects)
            self.assertFalse(any(e[0] == 'builtin' for e in self.effects))

    def test_actual_emitted_arguments_reach_fixed_callbacks_as_data(self):
        n = self.scheduler()
        play, stop = self.callbacks()
        for value in VALUES:
            self.db.execute('INSERT INTO custom_stream_url VALUES (?, ?)', (value, 'plugin://demo/media,a(b)'))
            p = self.program(channel=value)
            self.calls.clear()
            n._scheduleAutoplay(value, p.title, p.startDate, p.endDate)
            for command in self.calls:
                match = re.fullmatch(r'AlarmClock\(tvguide-autoplay-[0-9a-f]{64}-(?:start|stop),'
                                     r'RunScript\(special://home/addons/script\.tvguide\.fullscreen/'
                                     r'(play|stop)\.py,(v1_[A-Za-z0-9_-]+)\),[0-9]+,True\)', command)
                self.assertIsNotNone(match)
                callback, token = match.groups()
                self.effects.clear()
                (play if callback == 'play' else stop)([callback + '.py', token])
                if callback == 'play':
                    self.assertEqual(self.markers, {'playing.channel': value, 'playing.start': str(p.startDate)})
                    self.assertIn(('play', {'item': 'plugin://demo/media,a(b)'}), self.effects)
                else:
                    self.assertEqual(self.effects[-1], ('builtin', 'PlayerControl(Stop)'))

    def test_malformed_bounded_canonical_no_side_effects(self):
        play, stop = self.callbacks()
        malformed = ['', 'v2_WzEsImEiLCJiIl0', 'v1_!', 'v1_A', 'v1_abc=',
                     'v1_a,b', 'v1_abc\n', 'v1_' + 'a' * (data.MAX_TOKEN + 1)]
        for raw in [b'\xff', b'{}', b'[true,"a","b"]', b'[2,"a","b"]',
                    b'[1,4,"b"]', b'[1,"a",null]', b'[1,"","b"]',
                    b'[1,"a","b","extra"]', b'[ 1,"a","b"]',
                    b'[1,"\\u0061","b"]', b'[' * 2000 + b']' * 2000,
                    b' ' * (data.MAX_BYTES + 1)]:
            malformed.append(packet(raw))
        # Same decoded bytes but nonzero base64 pad bits must not be accepted.
        canonical = data.encode_identity('a', 'b')
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
        self.assertTrue(len(canonical[3:]) % 4)
        malformed.append(canonical[:-1] + alphabet[alphabet.index(canonical[-1]) + 1])
        for argv in ([['cb', token] for token in malformed]
                     + [[], ['cb'], ['cb', 'a', 'b', 'extra'], ['cb', '', 'start'],
                        ['cb', 'x' * (data.MAX_BYTES + 1), 'start']]):
            for callback in [play, stop]:
                self.effects.clear()
                callback(argv)
                self.assertEqual([e[0] for e in self.effects], ['log'], repr(argv)[:100])
        for value in VALUES:
            # Even command-looking start identity is data, never grammar.
            self.assertEqual(data.callback_identity(['cb', data.encode_identity(value, value)]), (value, value))
        with self.assertRaises(ValueError):
            data.encode_identity('é' * data.MAX_BYTES, 'start')

    def test_remove_recurring_and_clear_cancel_selected_occurrences(self):
        n = self.scheduler()
        p, repeat, other = self.program(), self.program(days=1), self.program(title='Other show')
        for program, kind in [(p, 0), (repeat, 1), (other, 3)]:
            n.addAutoplay(program, kind)
        self.assertEqual([kind for _, kind in self.added], [0, 1, 3])
        self.calls.clear()
        n.removeAutoplay(p)
        self.assertEqual(self.programs, [other])
        for program in (p, repeat):
            for phase in ('start', 'stop'):
                self.assertIn('CancelAlarm(%s-%s,True)' % (n.createAlarmClockName(program.title, program.startDate), phase), self.calls)
        self.calls.clear()
        n.clearAutoplays()
        self.assertEqual(self.programs, [])
        self.assertEqual(self.calls, ['CancelAlarm(%s-%s,True)' %
                                     (n.createAlarmClockName(other.title, other.startDate), phase)
                                     for phase in ('start', 'stop')])
        self.calls.clear()
        n.scheduleAutoplays()
        self.assertEqual(self.calls, [])

    def test_db_rows_and_retained_selection_service_gui_contracts(self):
        # Keep the actual recurrence selection, not a reimplementation of it.
        baseline = ast.parse(subprocess.check_output(['git', 'show', BASE + ':source.py'], cwd=ROOT))
        source = ast.parse((ROOT / 'source.py').read_text())
        def selection(tree):
            return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_getFullAutoplays')
        self.assertEqual(ast.dump(selection(source)), ast.dump(selection(baseline)))
        gui = (ROOT / 'gui.py').read_text()
        self.assertIn('times = ["once","always","new","daily"]', gui)
        self.assertIn('self.autoplay.addAutoplay(program, when)', gui)
        self.assertIn('self.autoplay.removeAutoplay(program)', gui)
        self.assertIn('n.scheduleAutoplays()', (ROOT / 'service.py').read_text())
        autoplay = (ROOT / 'autoplay.py').read_text()
        self.assertIn("Autoplay(database, ADDON.getAddonInfo('path')).clearAutoplays()", autoplay)
        self.assertIn("ADDON.setSetting('playing.channel','')", autoplay)
        self.assertIn("ADDON.setSetting('playing.start','')", autoplay)
        db = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == 'Database')
        nodes = [n for n in db.body if isinstance(n, ast.FunctionDef) and n.name in
                 ('_addAutoplay', '_removeAutoplay', '_clearAllAutoplays')]
        env = {}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'DB:three-methods-only', 'exec'), env)
        conn = sqlite3.connect(':memory:')
        self.addCleanup(conn.close)
        conn.execute('CREATE TABLE autoplays(channel, program_title, source, start_date, type)')
        holder = SimpleNamespace(conn=conn, source=SimpleNamespace(KEY='fixture'))
        p = SimpleNamespace(channel=SimpleNamespace(id=VALUES[0]), title='Title', startDate='date')
        for kind in (0, 1, 3):
            env['_addAutoplay'](holder, p, kind)
        self.assertEqual(conn.execute('SELECT channel, type FROM autoplays').fetchall(),
                         [(VALUES[0], k) for k in (0, 1, 3)])
        env['_removeAutoplay'](holder, p)
        self.assertEqual(conn.execute('SELECT * FROM autoplays').fetchall(), [])
        env['_addAutoplay'](holder, p, 0)
        env['_clearAllAutoplays'](holder)
        self.assertEqual(conn.execute('SELECT * FROM autoplays').fetchall(), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
