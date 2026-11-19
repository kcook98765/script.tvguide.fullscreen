"""Pure payload/decision captures + extracted GUI adapters, not native Kodi tests.

Only the new stdlib-only module is loaded; never import gui/ActionEditor or stubs.
"""
import ast
import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from urllib.parse import parse_qs, urlsplit, quote, unquote_plus
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('metadata_search', ROOT / 'metadata_search.py')
metadata = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metadata)
TEXT = '''Doctor's Café, "日本語" (1999) \\ x),RunScript(INERT_MARKER),1,True &a=b+#%25&&'''
ADDON = dict(addonid=metadata.TMDBHELPER, installed=True, enabled=True, version='4.10.14')


class Dialog:
    def __init__(self, choice=0, query=TEXT):
        self.choice, self.query = choice, query
        self.calls = []

    def select(self, heading, labels):
        self.calls.append(('select', heading, labels))
        return self.choice

    def input(self, heading, defaultt):
        self.calls.append(('input', heading, defaultt))
        return self.query

    def ok(self, *args):
        self.calls.append(('ok',) + args)


class Capture:
    def __init__(self):
        self.calls = []
        self.addon = dict(ADDON)
        self.override = {}

    def __call__(self, raw):
        request = json.loads(raw)
        self.calls.append(request)
        assert request['id'] == len(self.calls)
        assert set(request) == {'jsonrpc', 'id', 'method', 'params'}
        method, params = request['method'], request['params']
        if method in self.override:
            return self.override[method](request)
        if method == 'Addons.GetAddonDetails':
            assert params == {'addonid': metadata.TMDBHELPER,
                              'properties': ['installed', 'enabled', 'version']}
            result = {'addon': self.addon}
        elif method == 'GUI.ActivateWindow':
            result = 'OK'
        else:
            raise AssertionError('Unexpected/unsafe dispatch: ' + method)
        return json.dumps(dict(jsonrpc='2.0', id=request['id'], result=result))

    def windows(self):
        return [r for r in self.calls if r['method'] != 'Addons.GetAddonDetails']


class Search(unittest.TestCase):
    def make(self, choice=0, query=TEXT, module=metadata):
        rpc, dialog = Capture(), Dialog(choice, query)
        return rpc, dialog, module.MetadataSearch(rpc, dialog)

    def assert_dispatch(self, rpc, media_type, query):
        self.assertEqual(len(rpc.windows()), 1)
        request = rpc.windows()[0]
        self.assertEqual(request['method'], 'GUI.ActivateWindow')
        self.assertEqual(request['params'], {
            'window': 'videos', 'parameters': [
                'plugin://plugin.video.themoviedb.helper/?info=search&tmdb_type='
                + media_type + '&query=' + quote(query, safe=''), 'return']})
        uri = request['params']['parameters'][0]
        self.assertEqual(urlsplit(uri).netloc, metadata.TMDBHELPER)
        self.assertEqual(parse_qs(urlsplit(uri).query), {
            'info': ['search'], 'tmdb_type': [media_type], 'query': [query]})
        # Model the reviewed receivers' parameter split boundary, as data only.
        # Encoded &, = and && cannot create another receiver action/parameter.
        self.assertEqual(len(urlsplit(uri).query.split('&')), 3)
        self.assertNotIn('&&', uri)

    def test_movie_tv_exact_payload_and_original_default_text(self):
        for choice, media_type in enumerate(('movie', 'tv')):
            for version in ('4.10.14', '5.4.16'):
                rpc, dialog, search = self.make(choice)
                rpc.addon['version'] = version
                self.assertTrue(search.run(TEXT))
                self.assert_dispatch(rpc, media_type, TEXT)
                self.assertEqual(dialog.calls[1][2], TEXT)
                self.assertEqual([r['method'] for r in rpc.calls],
                                 ['Addons.GetAddonDetails'] * 2 + ['GUI.ActivateWindow'])
                self.assertFalse(any(c[0] == 'ok' for c in dialog.calls))

    def test_delimiters_unicode_and_command_looking_titles_are_data(self):
        for query in (TEXT, 'a=b&info=play&&paths=x', '%26info%3Dplay',
                      'ActivateWindow(Videos,x)', 'C:\\Movies\\"a", (b)',
                      "L'été + 日本語", ' leading and trailing ',
                      'Café\tSpecial\nPart 2\rTonight'):
            rpc, dialog, search = self.make(query=query)
            self.assertTrue(search.run(query))
            self.assert_dispatch(rpc, 'movie', query)

    def test_receiver_quote_normalization_is_explicit_not_exact_title_parity(self):
        for query in (TEXT, 'Café\tSpecial\nPart 2\rTonight', ''''Quoted title' ''',
                      '''"Title with boundary quotes"'''):
            uri = metadata.search_uri(metadata.TMDBHELPER, 'tv', query)
            paramstring = uri.split('?', 1)[1]
            # Reviewed TMDbHelper4 parser, reproduced as data semantics, not imported.
            received4 = {unquote_plus(k): unquote_plus(v)
                         for k, v in (p.split('=') for p in paramstring.split('&'))}
            self.assertEqual(received4['query'], query)
            # jurialmunkey0.2.2/0.2.28 (TMDbHelper5) strips boundary quotes.
            received5 = {k: v.strip("'").strip('"') for k, v in received4.items()}
            self.assertEqual(received5['query'], query.strip("'").strip('"'))
            self.assertEqual(set(received5), {'info', 'tmdb_type', 'query'})

    def test_unknown_provider_and_media_refused_without_dispatch(self):
        for provider in ('plugin.video.other', 'script.extendedinfo', TEXT, '', None):
            rpc, dialog, search = self.make()
            self.assertFalse(search.run(TEXT, provider=provider))
            self.assertEqual(rpc.calls, [])
            self.assertIn('Unsupported', dialog.calls[-1][-1])
            with self.assertRaises(ValueError):
                metadata.search_uri(provider, 'movie', TEXT)
        for media in ('episode', 'play', '', None):
            with self.assertRaises(ValueError):
                metadata.search_uri(metadata.TMDBHELPER, media, TEXT)

    def test_cancel_choices_or_keyboard_never_opens_provider(self):
        for choice in (-1, 2, True, None, '0'):
            rpc, dialog, search = self.make(choice)
            self.assertFalse(search.run(TEXT))
            self.assertEqual(rpc.calls, [])
        rpc, dialog, search = self.make(query='')
        self.assertFalse(search.run(TEXT))
        self.assertEqual(rpc.windows(), [])

    def test_missing_disabled_mismatched_or_unsupported_provider(self):
        for change in ({'installed': False}, {'enabled': False}, {'enabled': 1},
                       {'installed': None}, {'addonid': 'plugin.video.other'},
                       {'version': '4.10.13'}, {'version': '5.4.15'},
                       {'version': '6.0.0'}, {'version': None}, {'version': '5.4.16-fork'}):
            rpc, dialog, search = self.make()
            rpc.addon.update(change)
            self.assertFalse(search.run(TEXT))
            self.assertEqual(rpc.windows(), [])
            self.assertTrue(any(c[0] == 'ok' and 'TMDbHelper' in c[-1] for c in dialog.calls))
        rpc, dialog, search = self.make()
        rpc.override['Addons.GetAddonDetails'] = lambda r: json.dumps({
            'jsonrpc': '2.0', 'id': r['id'], 'error': {'code': -32602, 'message': 'absent'}})
        self.assertFalse(search.run(TEXT))
        self.assertIn('installed and enabled', dialog.calls[-1][-1])
        self.assertEqual(rpc.windows(), [])

    def test_invalid_or_empty_query_refused_not_punctuation_denied(self):
        for query in (' ', '\t\n\r', 'x' * 1025, '\x00', 'a\x01b', '\ud800', None, 123):
            rpc, dialog, search = self.make(query=query)
            self.assertFalse(search.run(TEXT))
            self.assertEqual(rpc.windows(), [])
            self.assertIn('title', dialog.calls[-1][-1])

    def test_provider_rechecked_after_keyboard(self):
        rpc, dialog, search = self.make()
        def keyboard(heading, defaultt):
            rpc.addon['enabled'] = False
            return TEXT
        dialog.input = keyboard
        self.assertFalse(search.run(TEXT))
        self.assertEqual(len(rpc.calls), 2)
        self.assertEqual(rpc.windows(), [])

    def test_errors_bad_responses_and_uncertain_dispatch_never_retry_or_claim_results(self):
        def lost(request):
            raise RuntimeError('simulated response loss')
        for method in ('Addons.GetAddonDetails', 'GUI.ActivateWindow'):
            for response in (lost, lambda r: 'invalid json', lambda r: 'null',
                             lambda r: json.dumps(dict(jsonrpc='2.0', id=999, result='OK')),
                             lambda r: json.dumps(dict(jsonrpc='2.0', id=r['id'], result=None)),
                             lambda r: json.dumps(dict(jsonrpc='2.0', id=r['id'],
                                                       error={'message': TEXT}))):
                rpc, dialog, search = self.make()
                rpc.override[method] = response
                self.assertFalse(search.run(TEXT))
                self.assertEqual(len(rpc.windows()), int(method == 'GUI.ActivateWindow'))
                self.assertEqual(dialog.calls[-1][0], 'ok')
                self.assertNotIn(TEXT, dialog.calls[-1][-1])

    def test_oracle_negative_controls_detect_unsafe_dispatch_and_data_loss(self):
        source = (ROOT / 'metadata_search.py').read_text()
        cases = [("self._rpc('GUI.ActivateWindow',", "self._rpc('Addons.ExecuteAddon',", 'dispatch'),
                 ("('query', query)]", "('query', query.replace(',', ''))]", 'data'),
                 ("addon.get('enabled') is not True", 'False', 'disabled'),
                 ("if type(choice) is not int or choice not in (0, 1):", 'if False:', 'cancel')]
        for old, new, mode in cases:
            self.assertEqual(source.count(old), 1)
            scope = {}
            exec(compile(source.replace(old, new), '<inert-search-negative>', 'exec'), scope)
            rpc, dialog, search = self.make(choice=-1 if mode == 'cancel' else 0,
                                            module=SimpleNamespace(**scope))
            if mode == 'disabled':
                rpc.addon['enabled'] = False
            accepted = search.run(TEXT)
            with self.assertRaises(AssertionError):
                if mode in ('disabled', 'cancel'):
                    self.assertEqual(rpc.windows(), [])
                else:
                    self.assertTrue(accepted)
                    self.assert_dispatch(rpc, 'movie', TEXT)
            print('DETECTED unsafe/data-loss search control:', mode)

    def test_real_gui_adapters_search_menu_and_keymap(self):
        text = (ROOT / 'gui.py').read_text()
        guide = next(n for n in ast.parse(text).body if isinstance(n, ast.ClassDef)
                     and n.name == 'TVGuide')
        methods = {n.name: n for n in guide.body if isinstance(n, ast.FunctionDef)}
        nodes = [copy.deepcopy(methods[n]) for n in ('lookupMetadata', 'programSearchSelect')]
        for node in nodes:
            node.body = [n for n in node.body if not isinstance(n, ast.ImportFrom)]
        dialog, rpc = Dialog(), Capture()
        scope = {'MetadataSearch': metadata.MetadataSearch,
                 'xbmc': SimpleNamespace(executeJSONRPC=rpc),
                 'xbmcgui': SimpleNamespace(Dialog=lambda: dialog)}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<metadata-gui-adapter>', 'exec'), scope)
        program = SimpleNamespace(title=TEXT)
        ui = SimpleNamespace(currentProgram=None, focusedProgram=program)
        self.assertTrue(scope['lookupMetadata'](ui))
        self.assert_dispatch(rpc, 'movie', TEXT)
        calls = []
        for name in ('programSearch', 'descriptionSearch', 'categorySearch', 'channelSearch'):
            setattr(ui, name, lambda n=name: calls.append(n))
        ui.lookupMetadata = lambda p: calls.append(('provider', p))
        for choice in range(4):
            dialog.choice = choice
            scope['programSearchSelect'](ui, program)
        self.assertEqual(calls, ['programSearch', 'descriptionSearch', 'categorySearch', 'channelSearch'])
        dialog.choice = 4
        scope['programSearchSelect'](ui, program)
        self.assertEqual(calls[-1], ('provider', program))
        for marker in ('elif action.getId() in COMMAND_ACTIONS["EXTENDED_INFO"]:',
                       'elif buttonClicked == PopupMenu.C_POPUP_EXTENDED:'):
            block = text[text.index(marker):].split('\n')[:3]
            self.assertIn('self.lookupMetadata(program)', '\n'.join(block))
        self.assertIn('self.programSearchSelect(program)', text)
        for skin in ('Default', 'CatBar'):
            root = ET.parse(ROOT / ('resources/skins/' + skin + '/720p/script-tvguide-menu.xml'))
            control = next(n for n in root.iter('control') if n.get('id') == '4013')
            self.assertEqual(control.findtext('label'), 'TMDbHelper lookup…')
            self.assertEqual([n.text for n in control.findall('visible')], ['true'])
        # Other skins (Dark has no 4013) retain lookup via their iSearch menu.
        editor = ast.parse((ROOT / 'ActionEditor.py').read_text())
        function = next(n for n in editor.body if isinstance(n, ast.FunctionDef)
                        and n.name == 'getCommandActions')
        file = SimpleNamespace(read=lambda: '{"EXTENDED_INFO":[15]}', close=lambda: None)
        scope = {'COMMANDS': {'EXTENDED_INFO': []}, 'ACTIONS': {}, 'json': json,
                 'xbmcvfs': SimpleNamespace(File=lambda *args: file)}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<metadata-keymap>', 'exec'), scope)
        self.assertEqual(scope['getCommandActions'](), {'EXTENDED_INFO': [15]})


if __name__ == '__main__':
    unittest.main(verbosity=2)
