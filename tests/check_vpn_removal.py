"""Actual methods and scheduled module import, all I/O inert; no Kodi/stub imports.

Source overrides are used only by the private in-memory negative-control runner.
The full GUI module is deliberately not imported (existing fixture boundary).
"""
import ast
import builtins
import datetime
from functools import lru_cache
import importlib.util
import itertools
from pathlib import Path
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {}


def source(path):
    return SOURCES.get(path, (ROOT / path).read_text() if (ROOT / path).exists() else '')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


typed = load('typed_fixture', 'tests/check_typed_mappings.py')
auto = load('auto_fixture', 'tests/check_autoplay_data.py')


@lru_cache(maxsize=None)
def gui_tree(text):
    return ast.parse(text)


def method(name, scope):
    tree = gui_tree(source('gui.py'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'TVGuide')
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'gui.py:actual', 'exec'), scope)
    return scope[name]


MATRIX = list(itertools.product((False, True), ('false', 'true'), ('false', 'true'))) + [(False, '', '')]
MEDIA = (typed.URI, 'http://media.invalid/a.ts', 'https://media.invalid/a.mp4?q=%22日本語',
         '/media/News (HD).mp4', 'special://profile/clip.mp4',
         'http://media.invalid/list.m3u?q=a', 'https://media.invalid/list.m3u8?q=b')
HIGH = 'https://media.invalid/high.ts'
PLAYLIST = ('#EXT-X-STREAM-INF:BANDWIDTH=20,RESOLUTION=1x1\nhttp://media.invalid/low.ts\n'
            '#EXT-X-STREAM-INF:BANDWIDTH=900,RESOLUTION=2x2\n' + HIGH + '\n'
            '#EXT-X-STREAM-INF:BANDWIDTH=100,RESOLUTION=1x1\nhttp://media.invalid/mid.ts\n')


class Removal(unittest.TestCase):
    def setUp(self):
        self.mapping_patch = patch.dict(sys.modules, playback_mapping=typed.load_adapter())
        self.mapping_patch.start()
        self.addCleanup(self.mapping_patch.stop)

    def boundary(self, scope, settings, installed, connect, default):
        """Capture rather than raise: original broad except must not hide effects."""
        forbidden = []
        settings.update({'vpnmgr.connect': connect, 'vpnmgr.default': default})
        addon = scope['ADDON']
        get, put = addon.getSetting, addon.setSetting

        def read(key):
            if key.startswith('vpn') or key == 'alternative.playback':
                forbidden.append(('read', key))
            return get(key)

        def write(key, value):
            if key.startswith('vpn'):
                forbidden.append(('write', key))
            return put(key, value)

        addon.getSetting, addon.setSetting = read, write
        scope['xbmc'].getCondVisibility = lambda cond: (forbidden.append(('detect', cond)), installed)[1]
        api = NS(**{name: (lambda *a, _name=name: forbidden.append((_name, a)))
                    for name in ('filterAndSwitch', 'defaultVPN', 'connectTo', 'disconnect',
                                 'getConnected', 'isFiltered', 'refreshLists', 'setAPICommand')})
        scope['VPNAPI'] = lambda: (forbidden.append(('construct',)), api)[1]
        return forbidden, api

    def gui(self, name, url, state, windowed=True, playlist=PLAYLIST, enabled='true', choice=0):
        cap, events, scope, ui, settings = typed.Mappings().ui(url, choice)
        forbidden, api = self.boundary(scope, settings, *state)
        # Stale object state must not matter either; current instances have none.
        ui.vpnswitch = state[1] == 'true'
        ui.vpndefault = state[2] == 'true'
        ui.api = api
        ui.osdEnabled = windowed
        settings.update({'m3u.read': enabled, 'alternative.playback': 'true'})
        reads = []
        scope['xbmcvfs'] = NS(File=lambda *args: (reads.append(args), NS(read=lambda: playlist))[1])
        ui.onRedrawEPG = lambda *args: events.append('redraw')
        ui._hideOsd = lambda: events.append('hide-osd')
        scope['xbmcaddon'] = NS(Addon=lambda *args: NS(getAddonInfo=lambda key: 'Demo'))
        return cap, events, scope, ui, settings, forbidden, reads

    def invoke(self, name, scope, ui):
        return method(name, scope)(ui, NS(title='Demo')) if name == 'playChannel' else method(name, scope)(ui, 'Demo')

    def test_actual_gui_media_matrix_no_manager_effects(self):
        for name, state, url, windowed in itertools.product(
                ('playChannel', 'waitForPlayBackStopped'), MATRIX, MEDIA, (False, True)):
            with self.subTest(method=name, state=state, url=url, windowed=windowed):
                cap, events, scope, ui, settings, forbidden, reads = self.gui(name, url, state, windowed)
                self.invoke(name, scope, ui)
                m3u = '.m3u' in url
                self.assertEqual([e for e in events if isinstance(e, tuple) and e[0] == 'play'],
                                 [('play', dict(item=HIGH if m3u else url, windowed=windowed))])
                self.assertEqual(reads, [(url, 'rb')] if m3u else [])
                self.assertEqual(forbidden, [])
                self.assertEqual(cap.calls, [])
                self.assertEqual(events.count('timer'), 1)
                if name == 'playChannel':
                    self.assertLess(events.index('stop'), events.index('clear'))
                    self.assertLess(events.index('clear'), next(i for i, e in enumerate(events) if isinstance(e, tuple)))
                else:
                    self.assertEqual(ui.alt_urls, [])

    def test_actual_m3u_disabled_and_no_match(self):
        for name, url, enabled, playlist in itertools.product(
                ('playChannel', 'waitForPlayBackStopped'), MEDIA[-2:], ('false', 'true'), ('# no variants\n', PLAYLIST)):
            with self.subTest(method=name, url=url, enabled=enabled, playlist=playlist):
                cap, events, scope, ui, settings, forbidden, reads = self.gui(
                    name, url, (True, 'true', 'true'), playlist=playlist, enabled=enabled)
                self.invoke(name, scope, ui)
                expected = HIGH if enabled == 'true' and playlist == PLAYLIST else url
                self.assertIn(('play', dict(item=expected, windowed=True)), events)
                self.assertEqual(reads, [(url, 'rb')] if enabled == 'true' else [])
                self.assertEqual(forbidden, [])

    def test_actual_chosen_alternate_and_retry_queue(self):
        primary, alternate, last = MEDIA[1], MEDIA[0], MEDIA[2]
        cap, events, scope, ui, settings, forbidden, reads = self.gui('playChannel', primary, (True, 'true', 'true'), choice=1)
        settings['play.alt.fallback'] = 'false'
        ui.database.getAltStreamUrl = lambda ch: [(alternate, 'Chosen'), (last, 'Last')]
        self.invoke('playChannel', scope, ui)
        self.assertIn(('play', dict(item=alternate, windowed=True)), events)
        self.assertEqual(ui.alt_urls, [primary, last])
        events.clear()
        self.invoke('waitForPlayBackStopped', scope, ui)
        self.assertIn(('play', dict(item=primary, windowed=True)), events)
        self.assertEqual(ui.alt_urls, [last])
        self.assertEqual(events.count('timer'), 1)
        self.assertEqual(forbidden, [])

    def test_actual_retry_exit_and_stop_return(self):
        for condition in ('playing', 'cancelled', 'disabled', 'exhausted', 'rejected', 'folder', 'minimized'):
            with self.subTest(condition=condition):
                cap, events, scope, ui, settings, forbidden, reads = self.gui('waitForPlayBackStopped', MEDIA[0], (True, 'true', 'true'))
                if condition in ('playing', 'cancelled'):
                    settings['playback.timeout'] = '1'
                    ui.player.isPlaying = lambda: condition == 'playing'
                    ui.tryingToPlay = condition != 'cancelled'
                if condition == 'disabled':
                    settings['play.alt.continue'] = 'false'
                if condition == 'exhausted':
                    ui.alt_urls = []
                if condition in ('rejected', 'folder'):
                    ui.alt_urls = ['@' + MEDIA[0] if condition == 'rejected' else typed.FOLDER]
                if condition == 'minimized':
                    settings['play.minimized'] = 'true'
                self.invoke('waitForPlayBackStopped', scope, ui)
                self.assertEqual(forbidden, [])
                self.assertEqual('redraw' in events, condition in ('disabled', 'exhausted', 'rejected'))
                self.assertEqual('timer' in events, condition == 'minimized')
                self.assertEqual(any(isinstance(e, tuple) and e[0] == 'play' for e in events), condition == 'minimized')
                if condition == 'minimized':
                    self.assertNotIn('hide', events)

    def test_actual_constructor_no_manager_state_or_probe(self):
        for state in MATRIX:
            with self.subTest(state=state):
                events = []
                settings = {'nextup.time': '5', 'nextup.showTime': '3', 'enable.osd': 'true'}
                scope = dict(ADDON=NS(getSetting=lambda k: settings.get(k, ''), setSetting=lambda *a: None,
                                     getAddonInfo=lambda k: 'inert-profile'),
                             xbmc=NS(Player=lambda: 'inert-player'),
                             xbmcvfs=NS(translatePath=lambda p: p, File=lambda *a: NS(
                                 read=lambda: 'channel=News\nother=Sports\n', close=lambda: events.append('close'))),
                             Point=NS, EPGView=NS, ImageCache=lambda p: ('cache', p),
                             MODE_EPG=1, datetime=datetime)
                forbidden, api = self.boundary(scope, settings, *state)
                cls = type('TVGuide', (object,), {'loadActions': lambda self: events.append('actions')})
                scope['TVGuide'] = cls
                cls.__init__ = method('__init__', scope)
                ui = cls()
                self.assertEqual(forbidden, [])
                self.assertFalse({'api', 'vpnswitch', 'vpndefault'}.intersection(vars(ui)))
                self.assertEqual(events, ['actions', 'close'])
                self.assertEqual(ui.player, 'inert-player')
                self.assertEqual(ui.tvdb_urls, ('cache', 'inert-profile'))
                self.assertEqual(ui.categories, ['News', 'Sports'])
                self.assertIsNone(ui.current_channel_id)
                self.assertTrue(ui.osdEnabled)
                self.assertEqual(ui.upNextTime, 5)
                self.assertEqual(ui.viewStartDate.minute % 30, 0)

    def test_existing_preview_default_player_toggle_and_primary_minimized(self):
        for playing in (False, True):
            cap, events, scope, ui, settings, forbidden, reads = self.gui('playChannel', MEDIA[0], (False, '', ''))
            ui.player.isPlaying = lambda: playing
            cls = next(n for n in typed.tree_for('gui.py').body if isinstance(n, ast.ClassDef) and n.name == 'StreamSetupDialog')
            for attr in {n.attr for n in ast.walk(cls) if isinstance(n, ast.Attribute) and n.attr.startswith('C_STREAM_')}:
                setattr(ui, attr, attr)
            ui.VISIBLE_STRM = 'strm'
            ui.VISIBLE_ADDONS, ui.VISIBLE_BROWSE, ui.VISIBLE_FAVOURITES = 'addons', 'browse', 'favourites'
            ui.getControl = lambda key: NS(getLabel=lambda: 'strm', setLabel=lambda value: None)
            ui.strmFile = MEDIA[0]
            scope.update(strings=lambda value: value, PREVIEW_STREAM=1, STOP_PREVIEW=2)
            typed.body('gui.py', 'StreamSetupDialog', 'onClick', scope)(ui, ui.C_STREAM_STRM_PREVIEW)
            self.assertEqual(events, ['stop'] if playing else [('play', dict(item=MEDIA[0], windowed=True))])
            self.assertEqual(forbidden, [])
        cap, events, scope, ui, settings, forbidden, reads = self.gui('playChannel', MEDIA[1], (False, '', ''))
        settings['play.minimized'] = 'true'
        self.invoke('playChannel', scope, ui)
        self.assertIn(('play', dict(item=MEDIA[1], windowed=True)), events)
        self.assertNotIn('hide', events)
        self.assertNotIn('timer', events)

    def scheduled(self, state):
        fixture = auto.AutoPlay()
        self.addCleanup(fixture.doCleanups)
        play, unused = fixture.callbacks()
        scope = play.__globals__
        scope['ADDON'] = scope['xbmcaddon'].Addon()
        settings = {'vpnmgr.connect': state[1], 'vpnmgr.default': state[2]}
        scope['ADDON'].getSetting = lambda k: settings.get(k, '')
        forbidden, api = self.boundary(scope, settings, *state)
        # Execute the entire real scheduled module with only inert Kodi modules.
        # This covers its imports, unlike the deliberately extracted GUI bodies.
        modules = {k: scope[k] for k in ('xbmc', 'xbmcaddon', 'xbmcvfs', 'sqlite3')}
        modules.update(autoplay_data=auto.data, playback_mapping=auto.mapping,
                       vpnapi=NS(VPNAPI=lambda: (forbidden.append(('construct',)), api)[1]))
        original_import = builtins.__import__

        def capture_import(name, *args, **kwargs):
            if name == 'vpnapi':
                forbidden.append(('import', name))
            return original_import(name, *args, **kwargs)

        with patch.dict(sys.modules, modules), patch('builtins.__import__', capture_import):
            env = {'__name__': 'inert_scheduled_import'}
            exec(compile(source('play.py'), 'play.py:module', 'exec'), env)
        fixture.effects.clear()
        return fixture, env['main'], forbidden

    def test_actual_scheduled_module_media_matrix_verbatim(self):
        for state in MATRIX:
            fixture, play, forbidden = self.scheduled(state)
            channel, start = 'Café, station', '2000-01-01 12:00:00'
            for url, legacy in itertools.product(MEDIA, (False, True)):
                with self.subTest(state=state, url=url, legacy=legacy):
                    fixture.db.execute('DELETE FROM custom_stream_url')
                    fixture.db.execute('INSERT INTO custom_stream_url VALUES (?, ?)', (channel, url))
                    fixture.effects.clear()
                    argv = ['play.py', channel, start] if legacy else ['play.py', auto.data.encode_identity(channel, start)]
                    play(argv)
                    self.assertEqual([e[0] for e in fixture.effects],
                                     ['addon', 'path', 'connect', 'close', 'setting', 'setting', 'play'])
                    self.assertEqual(fixture.effects[-1], ('play', dict(item=url)))
                    self.assertEqual(fixture.markers, {'playing.channel': channel, 'playing.start': start})
                    self.assertEqual(forbidden, [])

    def test_import_state_settings_and_python38_absence(self):
        self.assertFalse(source('vpnapi.py'))
        for path in ('gui.py', 'play.py'):
            tree = ast.parse(source(path), filename=path, feature_version=(3, 8))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    self.assertNotEqual(node.module, 'vpnapi')
                if isinstance(node, ast.Name):
                    self.assertNotEqual(node.id, 'VPNAPI')
                if isinstance(node, ast.Attribute):
                    self.assertNotIn(node.attr, ('vpnswitch', 'vpndefault', 'filterAndSwitch', 'defaultVPN'))
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    self.assertNotIn('service.vpn.manager', node.value)
                    self.assertNotIn('vpnmgr.', node.value)
                    self.assertNotIn('VPN_Manager_', node.value)
        xml = ET.fromstring(source('resources/settings.xml'))
        self.assertFalse(any(c.get('label') == 'VPN' for c in xml))
        self.assertNotIn('vpn', source('resources/settings.xml').lower())


if __name__ == '__main__':
    unittest.main()
