"""Inert captures of actual caller bodies; no Kodi imports, profiles or network."""
import ast
from functools import lru_cache
import importlib.util
from io import StringIO
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def load_adapter():
    spec = importlib.util.spec_from_file_location('playback_mapping', ROOT / 'playback_mapping.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=None)
def tree_for(path):
    return ast.parse((ROOT / path).read_text(), filename=path)


def body(path, owner, name, scope):
    tree = tree_for(path)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == owner)
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), path, 'exec'), scope)
    return scope[name]


class Regression(unittest.TestCase):
    def test_original_silent_acceptance_is_gone(self):
        source = (ROOT / 'gui.py').read_text()
        self.assertFalse("if url.startswith('@') or url.startswith('ActivateWindow'):" in source)
        self.assertIn('route_mapping', source)


class Capture:
    def __init__(self):
        self.calls, self.messages = [], []
        self.addons = [dict(addonid='plugin.video.demo', type='xbmc.python.pluginsource')]
        self.failure = None
        self.content = 'video'

    def execute(self, raw):
        request = json.loads(raw)
        self.calls.append(request)
        method = request['method']
        if method == self.failure:
            raise ValueError('PRIVATE_URI_MUST_NOT_LEAK')
        if method == 'Addons.GetAddons':
            assert request['params'] == dict(type='xbmc.python.pluginsource', content=self.content,
                                             installed=True, enabled=True)
            result = dict(addons=self.addons)
        elif method == 'GUI.ActivateWindow':
            result = 'OK'
        else:
            raise AssertionError('Unexpected mutation: ' + method)
        return json.dumps(dict(jsonrpc='2.0', id=request['id'], result=result))


URI = "plugin://plugin.video.demo/folder/?title=Café,日本語 (a)&q='x'%22&x=%2C#part"
FOLDER = 'ActivateWindow(10025,"' + URI + '",return)'


class Mappings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter = load_adapter()
        sys.modules['playback_mapping'] = cls.adapter

    def route(self, value, capture=None, **kwargs):
        capture = capture or Capture()
        return self.adapter.route_mapping(value, capture.execute, capture.messages.append, **kwargs)

    def test_play_and_exact_old_formats_preserve_data(self):
        for uri in (URI, 'https://example.invalid/日本語,a(b)?q="x"&s=%22',
                    '/media/News (2026), "a".mp4', r'C:\Media\News (2026).mp4',
                    'PlayMediaConcert.mp4', 'RunPlugin Demo.mp4', 'RunAddon.mp4'):
            cap = Capture()
            self.assertEqual(self.route(uri, cap), (uri, False))
            self.assertEqual(cap.calls, [])
        for value, uri in [('PlayMedia("' + URI + '")', URI),
                           ('PlayMedia(https://example.invalid/a%2Cb)', 'https://example.invalid/a%2Cb')]:
            self.assertEqual(self.route(value), (uri, False))

    def test_paramified_windows_and_escaped_quotes_roundtrip_as_player_data(self):
        # Literal producer captures, plus roundtrip against the two replacements
        # in all four tagged StringUtils::Paramify implementations.
        captured = r'PlayMedia("C:\\Media\\A \"quoted\", (日本語).mp4")'
        uri = 'C:\\Media\\A "quoted", (日本語).mp4'
        self.assertEqual(self.route(captured), (uri, False))
        for original in (uri, '\\\\server\\share\\', URI + '&q="yes"&path=\\x'):
            quoted = '"' + original.replace('\\', '\\\\').replace('"', '\\"') + '"'
            self.assertEqual(self.route('PlayMedia(' + quoted + ')'), (original, False))
        cap, events, scope, ui, settings = self.ui(captured)
        call = body('gui.py', 'TVGuide', 'playChannel', scope)
        call(ui, NS(title='Windows'))
        self.assertIn(('play', dict(item=uri, windowed=True)), events)
        self.assertEqual(cap.calls, [])
        # A quoted comma/action-looking suffix stays one media location, never
        # an executable second argument; actual extra arguments remain refused.
        text = 'x"),RunScript(INERT),PlayMedia("y'
        quoted = '"' + text.replace('"', '\\"') + '"'
        self.assertEqual(self.route('PlayMedia(' + quoted + ')'), (text, False))
        for malformed in (r'PlayMedia("C:\Media\film.mp4")',
                          'PlayMedia("x",resume)', 'PlayMedia("x"),RunScript(INERT)',
                          r'PlayMedia("x\")'):
            cap = Capture()
            self.assertEqual(self.route(malformed, cap), (None, False))
            self.assertEqual(cap.calls, [])

    def test_program_folder_uses_only_fixed_programs_executable_pair(self):
        for window in ('10001', 'Programs'):
            cap = Capture()
            cap.content = 'executable'
            value = 'ActivateWindow(' + window + ',"' + URI + '",return)'
            self.assertEqual(self.route(value, cap), (None, True))
            self.assertEqual(cap.calls[-1]['params'], dict(window='programs',
                                                         parameters=[URI, 'return']))
            cap = Capture()
            cap.content, cap.addons = 'executable', []
            self.assertEqual(self.route(value, cap), (None, False))
            self.assertEqual(len(cap.calls), 1)

    def test_folder_is_vector_not_player_or_executeaddon(self):
        for value in (FOLDER, 'ActivateWindow(Videos,plugin://plugin.video.demo/,return)'):
            cap = Capture()
            mapping = self.adapter.parse_mapping(value)
            self.assertEqual(mapping.kind, self.adapter.Kind.OPEN_FOLDER)
            self.assertEqual(self.route(value, cap), (None, True))
            self.assertEqual(cap.calls[-1]['params'], dict(window='videos',
                             parameters=[mapping.uri, 'return']))
            self.assertEqual([c['method'] for c in cap.calls],
                             ['Addons.GetAddons', 'GUI.ActivateWindow'])
            self.assertEqual(cap.messages, [])

    def test_actions_unknown_and_ambiguous_legacy_never_dispatch(self):
        cases = ['@' + URI, '@https://example.invalid/a', 'RunPlugin(' + URI + ')',
                 'ActivateWindow(Music,"' + URI + '",return)',
                 'ActivateWindow(10025,plugin://plugin.video.demo/a,b,return)',
                 FOLDER + ',RunScript(INERT)', 'ActivateWindow(',
                 'PlayMedia("x",resume)', 'PlayMedia("")', 'XBMC.RunScript(INERT)',
                 None, '', URI + '\n', '@@' + URI]
        for value in cases:
            with self.subTest(value=value):
                cap = Capture()
                self.assertEqual(self.route(value, cap), (None, False))
                self.assertEqual(cap.calls, [])
                self.assertEqual(len(cap.messages), 1)
        self.assertEqual(self.adapter.parse_mapping('@' + URI).kind,
                         self.adapter.Kind.RUN_ADDON)

    def test_inventory_and_response_failures_no_retry_or_secret_echo(self):
        for addons in ([], [dict(addonid='plugin.video.demo', type='xbmc.python.script')],
                       [dict(addonid='plugin.video.other', type='xbmc.python.pluginsource')]):
            cap = Capture()
            cap.addons = addons
            self.assertEqual(self.route(FOLDER, cap), (None, False))
            self.assertEqual(len(cap.calls), 1)
        for method, count in [('Addons.GetAddons', 1), ('GUI.ActivateWindow', 2)]:
            cap = Capture()
            cap.failure = method
            self.assertEqual(self.route(FOLDER, cap), (None, False))
            self.assertEqual(len(cap.calls), count)
            self.assertNotIn('PRIVATE_URI', str(cap.messages))
        for response in ('null', '{}', '{broken',
                         '{"jsonrpc":"2.0","id":99,"result":"OK"}',
                         '{"jsonrpc":"2.0","id":1,"error":{"message":"PRIVATE_URI"}}'):
            messages = []
            self.assertEqual(self.adapter.route_mapping(FOLDER, lambda raw: response,
                                                       messages.append), (None, False))
            self.assertNotIn('PRIVATE_URI', str(messages))

    def ui(self, value, choice=0):
        cap, events = Capture(), []
        settings = {'play.alt.fallback': 'true', 'play.alt.continue': 'true',
                    'play.minimized': 'false', 'playback.timeout': '0',
                    'playback.osd.timeout': '0'}
        player = NS(isPlaying=lambda: True, stop=lambda: events.append('stop'),
                    play=lambda **kw: events.append(('play', kw)))
        dialog = NS(ok=lambda *args: cap.messages.append(args), select=lambda *args: choice,
                    notification=lambda *args, **kw: None)
        scope = dict(xbmc=NS(executeJSONRPC=cap.execute),
                     xbmcgui=NS(Dialog=lambda: dialog, NOTIFICATION_ERROR=1),
                     ADDON=NS(getSetting=lambda key: settings.get(key, ''),
                              setSetting=lambda *args: events.append('setting')),
                     json=json, re=re, time=NS(sleep=lambda delay: None), MODE_OSD=2,
                     threading=NS(Timer=lambda *args: NS(start=lambda: events.append('timer'))))
        ui = NS(database=NS(getStreamUrl=lambda ch: value, getAltStreamUrl=lambda ch: [],
                            getCurrentProgram=lambda ch: None), currentChannel=None,
                player=player, alt_urls=[value], mode=1, osdActive=False, tryingToPlay=True,
                vpnswitch=True, vpndefault=True, osdEnabled=True,
                api=NS(filterAndSwitch=lambda *args: events.append('vpn-plugin'),
                       defaultVPN=lambda *args: events.append('vpn-default')),
                clear_catchup=lambda: events.append('clear'),
                channelIdx=0, viewStartDate=None,
                onRedrawEPG=lambda *args: None,
                _hideEpg=lambda: events.append('hide'), _hideQuickEpg=lambda: events.append('hide-quick'),
                _showOsd=lambda: None, _hideOsd=lambda: None)
        ui.waitForPlayBackStopped = lambda *args: None
        return cap, events, scope, ui, settings

    def test_actual_primary_and_fallback_route_before_playback_effects(self):
        for method in ('playChannel', 'waitForPlayBackStopped'):
            for value, expected in ((FOLDER, True), ('@' + URI, False), ('ActivateWindow(', False)):
                cap, events, scope, ui, settings = self.ui(value)
                call = body('gui.py', 'TVGuide', method, scope)
                result = call(ui, NS(title='Demo')) if method == 'playChannel' else call(ui, 'Demo')
                self.assertIs(result, expected)
                self.assertEqual(events, [])
                self.assertIsNone(ui.currentChannel)
            for value in (URI, 'https://example.invalid/a'):
                cap, events, scope, ui, settings = self.ui(value)
                call = body('gui.py', 'TVGuide', method, scope)
                call(ui, NS(title='Demo')) if method == 'playChannel' else call(ui, 'Demo')
                self.assertIn(('play', dict(item=value, windowed=True)), events)
                self.assertIn('vpn-plugin' if value == URI else 'vpn-default', events)
                self.assertIn('hide', events)
                self.assertEqual(cap.calls, [])

    def test_actual_selection_cancel_and_reject_do_not_redetect(self):
        for choice in (-1, 1, 99, True):
            cap, events, scope, ui, settings = self.ui(URI, choice)
            settings['play.alt.fallback'] = 'false'
            ui.database.getAltStreamUrl = lambda ch: [('@' + URI, 'Action')]
            scope['xbmcaddon'] = NS(Addon=lambda *args: NS(getAddonInfo=lambda key: 'Demo'))
            call = body('gui.py', 'TVGuide', 'playChannel', scope)
            self.assertIs(call(ui, NS(title='Demo')), False)
            self.assertEqual(events, [])
            self.assertEqual(cap.calls, [])
        cap, events, scope, ui, settings = self.ui(None)
        call = body('gui.py', 'TVGuide', 'playChannel', scope)
        self.assertIsNone(call(ui, NS(title='Demo')))
        # Actual entry caller must auto-detect only a missing mapping, not False.
        source = (ROOT / 'gui.py').read_text()
        self.assertIn('self.playChannel(program.channel, program) is None:', source)
        # The already-playing-channel shortcut must not hide before routing a
        # newly saved folder/action/invalid mapping for that same channel.
        for value in (FOLDER, '@' + URI, 'ActivateWindow('):
            cap, events, scope, ui, settings = self.ui(value)
            settings['play.always.choose'] = 'false'
            channel = NS(id='demo', title='Demo')
            ui.currentChannel = channel
            play = body('gui.py', 'TVGuide', 'playChannel', scope)
            ui.playChannel = lambda ch, program: play(ui, ch, program)
            choose = body('gui.py', 'TVGuide', 'playOrChoose', scope)
            choose(ui, NS(channel=channel))
            self.assertEqual(events, [])

    def test_actual_preview_keeps_existing_player_for_folder_or_rejection(self):
        for value, expected in ((FOLDER, True), ('@' + URI, False)):
            cap, events, scope, ui, settings = self.ui(value)
            tree = tree_for('gui.py')
            cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'StreamSetupDialog')
            for attr in {n.attr for n in ast.walk(cls) if isinstance(n, ast.Attribute)
                         and n.attr.startswith('C_STREAM_')}:
                setattr(ui, attr, attr)
            ui.VISIBLE_STRM = 'strm'
            ui.VISIBLE_ADDONS, ui.VISIBLE_BROWSE, ui.VISIBLE_FAVOURITES = 'addons', 'browse', 'favourites'
            ui.getControl = lambda key: NS(getLabel=lambda: 'strm')
            ui.strmFile = value
            call = body('gui.py', 'StreamSetupDialog', 'onClick', scope)
            self.assertIs(call(ui, ui.C_STREAM_STRM_PREVIEW), expected)
            self.assertEqual(events, [])

    def test_actual_scheduled_guard_precedes_settings_vpn_and_player(self):
        tree = ast.parse((ROOT / 'play.py').read_text())
        block = next(n for n in tree.body if isinstance(n, ast.If) and isinstance(n.test, ast.Name)
                     and n.test.id == 'row')
        for value in (FOLDER, '@' + URI, 'RunScript(INERT)'):
            cap = Capture()
            scope = dict(row=(value,), sys=sys, route_mapping=self.adapter.route_mapping,
                         xbmc=NS(executeJSONRPC=cap.execute, LOGWARNING=2,
                                 log=lambda message, level: cap.messages.append(message)))
            with self.assertRaises(SystemExit) as raised:
                exec(compile(ast.Module(body=[block], type_ignores=[]), 'play.py', 'exec'), scope)
            self.assertEqual(raised.exception.code, 1)
            self.assertEqual(cap.calls, [])
            self.assertEqual(len(cap.messages), 1)
        cap, events, scope, ui, settings = self.ui(URI)
        scope.update(row=(URI,), route_mapping=self.adapter.route_mapping,
                     channel='demo', start='2000-01-01',
                     xbmc=NS(executeJSONRPC=cap.execute, getCondVisibility=lambda key: False,
                             Player=lambda: ui.player))
        exec(compile(ast.Module(body=[block], type_ignores=[]), 'play.py', 'exec'), scope)
        self.assertEqual(events, ['setting', 'setting', ('play', dict(item=URI))])
        self.assertEqual(cap.calls, [])

    def test_python38_grammar_and_favourite_import_keeps_wrappers(self):
        for name in ('playback_mapping.py', 'gui.py', 'streaming.py', 'play.py'):
            ast.parse((ROOT / name).read_text(), feature_version=(3, 8))
        self.assertNotIn('value = value[', (ROOT / 'streaming.py').read_text())
        root = ET.Element('favourites')
        values = [FOLDER, 'PlayMedia("' + URI + '")', 'RunScript(INERT)']
        for value in values:
            ET.SubElement(root, 'favourite', name='Synthetic').text = value
        scope = dict(ElementTree=ET, open=lambda *args, **kw: StringIO(ET.tostring(root, encoding='unicode')),
                     os=NS(path=NS(join=lambda *parts: 'synthetic-only', exists=lambda path: True)),
                     xbmcvfs=NS(translatePath=lambda path: path))
        call = body('streaming.py', 'StreamsService', 'loadFavourites', scope)
        self.assertEqual(call(NS()), [('Synthetic', value) for value in values])


if __name__ == '__main__':
    unittest.main()
