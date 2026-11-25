"""Issue #87 actual-caller regression and optional exact-baseline characterization.

Runs actual production method ASTs with inert effect captures. No Kodi/stubs,
providers, network or retained profile/settings data are imported/accessed.
No captured builtin establishes native focus/return/playback acceptance.
--source-ref REF runs candidate expectations against a local revision (negative
control); add --baseline to characterize the old behavior instead. The new pure
route helper is loaded from the selected worktree for both modes, never from Kodi.
"""
import argparse
import ast
from collections import defaultdict
from functools import lru_cache
from io import StringIO
from itertools import product
import os
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SOURCE_REF = None
BASELINE = False
KODI_SOURCE_DIR = None
VERSIONS = ('19.4', '20.5', '21.3', '22.0-RC2')
ROUTES = {
    'Favourites': 'ActivateWindow(10134)',
    'Simple Favourites': 'ActivateWindow(10001,plugin://plugin.program.simple.favourites,return)',
    'Video Favourites': 'ActivateWindow(10025,plugin://plugin.video.favourites,return)',
    'Super Favourites': 'ActivateWindow(10001,plugin://plugin.program.super.favourites,return)',
}
MEDIA = 'PlayMedia("special://home/issue87-fixture.mp4")'


@lru_cache(None)
def source(path):
    if SOURCE_REF:
        return subprocess.check_output(['git', 'show', SOURCE_REF + ':' + path],
                                       cwd=ROOT, text=True)
    return (ROOT / path).read_text(encoding='utf-8')


@lru_cache(None)
def tree(path):
    return ast.parse(source(path), filename=source_label(path))


def source_label(path):
    return SOURCE_REF + ':' + path if SOURCE_REF else path


def class_node(name):
    return next(n for n in tree('gui.py').body
                if isinstance(n, ast.ClassDef) and n.name == name)


def constants(name):
    return {n.targets[0].id: ast.literal_eval(n.value)
            for n in class_node(name).body if isinstance(n, ast.Assign)
            and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Constant)}


def method(path, owner, name, scope):
    cls = next(n for n in tree(path).body if isinstance(n, ast.ClassDef) and n.name == owner)
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), source_label(path), 'exec'), scope)
    return scope[name]


def pure_module(name):
    # Only these Kodi-free production helpers, never gui/streaming entry points.
    assert name in ('action_bar', 'playback_mapping', 'favourites_navigation')
    module = type(sys)(name)
    parsed = (ast.parse((ROOT / (name + '.py')).read_text())
              if name == 'favourites_navigation' else tree(name + '.py'))
    filename = name + '.py' if name == 'favourites_navigation' else source_label(name + '.py')
    exec(compile(parsed, filename, 'exec'), module.__dict__)
    return module


class Item:
    def __init__(self, label):
        self.label, self.properties = label, {}

    def setProperty(self, key, value):
        self.properties[key] = value

    def getProperty(self, key):
        return self.properties[key]

    def getLabel(self):
        return self.label


class Control:
    def __init__(self):
        self.items, self.label = [], ''

    def addItems(self, items):
        self.items.extend(items)

    def getSelectedItem(self):
        return self.items[0] if self.items else None

    def setLabel(self, label):
        self.label = label

    def getLabel(self):
        return self.label


def native_expected(version):
    return ('ActivateWindow(10134)' if BASELINE or version in VERSIONS[:2]
            else 'ActivateWindow(favouritesbrowser)')


class FavouritesNavigation(unittest.TestCase):
    def guide(self, value, version='21.3', available=True):
        events, reads = [], []
        bar = pure_module('action_bar')

        def get_setting(key):
            reads.append(key)
            return value if key == 'favourites' else ''

        def get_addons(**kwargs):
            self.assertEqual(kwargs, dict(type='xbmc.python.pluginsource', installed=True, enabled=True))
            events.append(('provider-check', kwargs))
            return {'addons': [{'addonid': addon} for addon in (
                'plugin.program.simple.favourites', 'plugin.video.favourites',
                'plugin.program.super.favourites')] if available else []}

        scope = dict(action_bar=bar, favourites_navigation=pure_module('favourites_navigation'),
                     MODE_EPG='EPG',
                     ADDON=NS(getSetting=get_setting,
                     setSetting=lambda *a: events.append(('setting', a))),
                     xbmc=NS(executebuiltin=lambda command: events.append(('builtin', command)),
                             getInfoLabel=lambda label: version),
                     xbmcgui=NS(Dialog=lambda: NS(ok=lambda *a: events.append(('notice', a)))),
                     RPC=NS(addons=NS(get_addons=get_addons)))
        ui = NS(**constants('TVGuide'), isClosing=False, mode='EPG', getFocusId=lambda: 9001,
                category='All Channels',
                categories=['All Channels'], tvdb_urls={}, actions=bar.defaults(),
                _hideControl=lambda c: events.append(('hide', c)),
                database=NS(setCategory=lambda c: events.append(('category', c))),
                getControl=lambda c: NS(getSelectedPosition=lambda: 0),
                close=lambda: events.append(('guide.close',)))
        # An unexpected playback/navigation call fails, rather than silently passing.
        ui.player = NS()
        if any(isinstance(n, ast.FunctionDef) and n.name == 'openFavourites'
               for n in class_node('TVGuide').body):
            open_favourites = method('gui.py', 'TVGuide', 'openFavourites', scope)
            ui.openFavourites = lambda native=False: open_favourites(ui, native)
        return ui, scope, events, reads

    def click(self, value, context=False, version='21.3', available=True):
        ui, scope, events, reads = self.guide(value, version, available)
        if context:
            popup_click = method('gui.py', 'PopupMenu', 'onClick', scope)

            class Popup:
                def __init__(self, database, program, remind, autoplay, autoplaywith,
                             category, categories):
                    self.program, self.category, self.categories = program, category, categories

                def close(self):
                    events.append(('popup.close',))

                def doModal(self):
                    events.append(('popup.modal',))
                    popup_click(self, self.C_POPUP_FAVOURITES)
                    events.append(('popup.return',))

            for key, constant in constants('PopupMenu').items():
                setattr(Popup, key, constant)
            scope['PopupMenu'] = Popup
            program = NS(title='Fixture', imageSmall='fixture.png', notificationScheduled=False,
                         autoplayScheduled=False, autoplaywithScheduled=False)
            method('gui.py', 'TVGuide', '_showContextMenu', scope)(ui, program)
        else:
            method('gui.py', 'TVGuide', 'onClick', scope)(ui, ui.C_MAIN_MOUSE_FAVOURITES)
        return ui, events, reads

    def test_declared_default_is_literal_not_enum_index(self):
        node = ET.fromstring(source('resources/settings.xml')).find(".//setting[@id='favourites']")
        self.assertEqual(node.get('type'), 'select')
        self.assertEqual(node.get('default'), 'Favourites')
        self.assertEqual(node.get('values').split('|'), list(ROUTES))
        self.assertIsNone(node.get('lvalues'))

    def test_main_and_returned_context_dispatch_all_four_fixed_routes(self):
        for version, value, context in product(VERSIONS, ROUTES, (False, True)):
            expected = native_expected(version) if value == 'Favourites' else ROUTES[value]
            with self.subTest(version=version, value=value, context=context):
                ui, events, reads = self.click(value, context, version)
                self.assertEqual([e for e in events if e[0] == 'builtin'], [('builtin', expected)])
                self.assertEqual(reads, ['favourites'])
                self.assertEqual(ui.category, 'All Channels')
                self.assertNotIn(('guide.close',), events)
                self.assertFalse(any(e[0] == 'setting' and e[1][0] == 'favourites' for e in events))
                if context:
                    self.assertLess(events.index(('popup.close',)), events.index(('popup.return',)))
                    self.assertLess(events.index(('popup.return',)), events.index(('builtin', expected)))

    def test_unknown_and_command_text_reject_but_unset_uses_default(self):
        for value in ('0', '1', '2', '3', '', 'Favorites', 'RunScript(INERT)',
                      'Favourites),Quit()', None):
            for context in (False, True):
                with self.subTest(value=value, context=context):
                    _, events, reads = self.click(value, context)
                    expected = ([('builtin', native_expected('21.3'))]
                                if not BASELINE and value in ('', None) else [])
                    self.assertEqual([e for e in events if e[0] == 'builtin'], expected)
                    self.assertEqual(reads, ['favourites'])

    def test_action_bar_is_a_separate_native_only_path_even_with_provider_selected(self):
        for version, value in product(VERSIONS, ROUTES):
            ui, scope, events, reads = self.guide(value, version)
            bar = scope['action_bar']
            ui.actions, unsupported = bar.normalize([['Keep label', 'ActivateWindow(10134)', '']])
            self.assertEqual(unsupported, 0)
            ui.getControl = lambda c: NS(getSelectedPosition=lambda: 0)
            method('gui.py', 'TVGuide', 'onClick', scope)(ui, ui.C_MAIN_ACTIONS)
            self.assertEqual(events, [('builtin', native_expected(version))])
            self.assertEqual(reads, [])
            ui.actions = [['Untrusted', 'RunScript(INERT)', '']]
            events.clear()
            scope['onClick'](ui, ui.C_MAIN_ACTIONS)
            self.assertEqual(events, [])

    def test_unset_uses_native_on_every_release_without_writing_selection(self):
        for version, value, context in product(VERSIONS, ('', None), (False, True)):
            _, events, _ = self.click(value, context, version)
            self.assertEqual([e for e in events if e[0] == 'builtin'],
                             [] if BASELINE else [('builtin', native_expected(version))])
            self.assertFalse(any(e[0] == 'provider-check' for e in events))
            self.assertFalse(any(e[0] == 'setting' and e[1][0] == 'favourites' for e in events))

    def test_exact_tag_window_identifiers_and_names(self):
        if KODI_SOURCE_DIR is None:
            self.skipTest('Use --kodi-source-dir with the supplied exact-tag source copies')
        for lane in ('matrix', 'nexus', 'omega', 'piers'):
            folder = KODI_SOURCE_DIR / ('kodi-' + lane)
            ids = (folder / 'WindowIDs.h').read_text()
            names = (folder / 'WindowTranslator.cpp').read_text()
            dialog = re.search(r'^#define\s+WINDOW_DIALOG_FAVOURITES\s+10134\b', ids, re.M)
            browser = re.search(r'^#define\s+WINDOW_FAVOURITES\s+10060\b', ids, re.M)
            self.assertEqual(bool(dialog), lane in ('matrix', 'nexus'))
            self.assertEqual(bool(browser), lane != 'matrix')
            self.assertEqual('{"favourites", WINDOW_DIALOG_FAVOURITES}' in names, bool(dialog))
            self.assertEqual('{"favouritesbrowser", WINDOW_FAVOURITES}' in names, bool(browser))

    def test_unavailable_or_unconfirmed_provider_explains_without_native_fallback(self):
        if BASELINE:
            self.skipTest('Baseline had no provider availability handling')
        for value in list(ROUTES)[1:]:
            for context in (False, True):
                _, events, _ = self.click(value, context, available=False)
                self.assertFalse(any(e[0] == 'builtin' for e in events))
                self.assertEqual(len([e for e in events if e[0] == 'notice']), 1)
        ui, scope, events, _ = self.guide('Simple Favourites')

        def failed_query(**kwargs):
            raise RuntimeError('inert response failure')

        scope['RPC'].addons.get_addons = failed_query
        method('gui.py', 'TVGuide', 'onClick', scope)(ui, ui.C_MAIN_MOUSE_FAVOURITES)
        self.assertEqual([e[0] for e in events], ['notice'])

    def test_helper_defaults_names_versions_and_closed_commands(self):
        helper = pure_module('favourites_navigation')
        for version in VERSIONS:
            expected = ('ActivateWindow(10134)' if version in VERSIONS[:2]
                        else 'ActivateWindow(favouritesbrowser)')
            for value in ('Favourites', '', None):
                self.assertEqual(helper.route(value, version + ' Git:fixture'), (expected, None))
        for version in ('', 'unknown', None, '21),Quit()'):
            self.assertEqual(helper.native_command(version), 'ActivateWindow(10134)')
        for value in ('0', '1', 'Favorites', ' Favourites', 'Favourites\n',
                      'ActivateWindow(10060)', 'RunScript(INERT)', [], False):
            self.assertEqual(helper.route(value, '21.3'), (None, None))

    def test_window_classes_and_skin_entry_points_are_not_interchangeable(self):
        self.assertEqual(ast.unparse(class_node('TVGuide').bases[0]), 'xbmcgui.WindowXML')
        for name in ('PopupMenu', 'StreamSetupDialog'):
            self.assertEqual(ast.unparse(class_node(name).bases[0]), 'xbmcgui.WindowXMLDialog')
        for skin, expected in (('Default', (1, 1, 0)), ('Dark', (0, 0, 0)), ('CatBar', (1, 1, 1))):
            main = ET.fromstring(source('resources/skins/' + skin + '/720p/script-tvguide-main.xml'))
            popup = ET.fromstring(source('resources/skins/' + skin + '/720p/script-tvguide-menu.xml'))
            self.assertEqual((len(main.findall(".//control[@id='4316'][@type='button']")),
                              len(popup.findall(".//control[@id='4012'][@type='button']")),
                              len(main.findall(".//control[@id='7100'][@type='list']"))), expected)

    def streams(self, xml, exists=True):
        reads = []

        def memory_open(path, encoding):
            self.assertEqual(path, 'special://profile/favourites.xml')
            self.assertEqual(encoding, 'utf-8')
            reads.append(path)
            return StringIO(xml)

        scope = dict(ElementTree=ET, open=memory_open,
                     os=NS(path=NS(join=os.path.join, exists=lambda path: exists)),
                     xbmcvfs=NS(translatePath=lambda path: path))
        service = NS()
        load = method('streaming.py', 'StreamsService', 'loadFavourites', scope)
        service.loadFavourites = lambda: load(service)
        return service, reads

    def setup_dialog(self, xml):
        service, reads = self.streams(xml)
        events, controls = [], {}
        service.getAddons = lambda: []

        def control(key):
            return controls.setdefault(key, Control())

        class Player:
            playing = False

            def isPlaying(self):
                return self.playing

            def play(self, **kwargs):
                events.append(('play', kwargs))
                self.playing = True

            def stop(self):
                events.append(('stop',))
                self.playing = False

        ui = NS(**constants('StreamSetupDialog'), streamingService=service,
                getControl=control, updateAddonInfo=lambda: None,
                channel=NS(title='Fixture', logo=''), player=Player(),
                close=lambda: events.append(('close',)),
                database=NS(getStreamUrl=lambda ch: None,
                    setCustomStreamUrl=lambda *a: events.append(('primary', a)),
                    setAltCustomStreamUrl=lambda *a: events.append(('alternative', a))))
        scope = dict(StreamSetupDialog=ui, xbmcgui=NS(ListItem=Item, Dialog=lambda: NS(
            notification=lambda *a, **kw: events.append(('notice', a, kw)))),
            RPC=NS(addons=NS(get_addons=lambda **kw: {})),
            remove_formatting=lambda value: value, strings=lambda value: value,
            PREVIEW_STREAM='preview', STOP_PREVIEW='stop-preview',
            xbmc=NS(executeJSONRPC=lambda request: self.fail('Unexpected RPC: ' + request)))
        method('gui.py', 'StreamSetupDialog', 'onInit', scope)(ui)
        method('gui.py', 'StreamSetupDialog', 'onFocus', scope)(ui, ui.C_STREAM_FAVOURITES_TAB)
        return ui, scope, events, reads

    def test_discovery_missing_empty_malformed_and_exact_match(self):
        for xml, exists in (('', False), ('<favourites/>', True), ('<broken', True)):
            service, reads = self.streams(xml, exists)
            self.assertEqual(service.loadFavourites(), [])
            self.assertEqual(len(reads), int(exists))
        root = ET.Element('favourites')
        for name, value in (('Fixture', MEDIA), ('Untrusted', 'RunScript(INERT)')):
            ET.SubElement(root, 'favourite', name=name).text = value
        service, _ = self.streams(ET.tostring(root, encoding='unicode'))
        self.assertEqual(service.loadFavourites(), [('Fixture', MEDIA), ('Untrusted', 'RunScript(INERT)')])
        scope = {}
        detect = method('streaming.py', 'StreamsService', 'detectStream', scope)
        self.assertEqual(detect(service, NS(title='Fixture')), MEDIA)

    def test_stream_setup_empty_and_populated_preview_link_alternative_cancel(self):
        for populated in (False, True):
            root = ET.Element('favourites')
            if populated:
                ET.SubElement(root, 'favourite', name='Fixture').text = MEDIA
            ui, scope, events, reads = self.setup_dialog(ET.tostring(root, encoding='unicode'))
            self.assertEqual(len(reads), 1)
            items = ui.getControl(ui.C_STREAM_FAVOURITES).items
            self.assertEqual([(i.getLabel(), i.getProperty('stream')) for i in items],
                             [('Fixture', MEDIA)] if populated else [])
            self.assertEqual(ui.getControl(ui.C_STREAM_VISIBILITY_MARKER).getLabel(), 'favourites')
            click = method('gui.py', 'StreamSetupDialog', 'onClick', scope)
            with patch.dict(sys.modules, playback_mapping=pure_module('playback_mapping')):
                click(ui, ui.C_STREAM_FAVOURITES_PREVIEW)
                if populated:
                    self.assertEqual(events, [('play', dict(item='special://home/issue87-fixture.mp4', windowed=True))])
                    click(ui, ui.C_STREAM_FAVOURITES_PREVIEW)
                    self.assertEqual(events[-1], ('stop',))
                else:
                    self.assertEqual(events, [])
            events.clear()
            click(ui, ui.C_STREAM_FAVOURITES_ALT)
            self.assertEqual([e for e in events if e[0] != 'notice'],
                             [('alternative', (ui.channel, 'Fixture', MEDIA))] if populated else [])
            events.clear()
            click(ui, ui.C_STREAM_FAVOURITES_OK)
            self.assertEqual(events, ([('primary', (ui.channel, MEDIA))] if populated else []) + [('close',)])
            events.clear()
            click(ui, ui.C_STREAM_FAVOURITES_CANCEL)
            self.assertEqual(events, [('close',)])


class FocusControl:
    def __init__(self, control_id, x=100):
        self.control_id, self.x = control_id, x

    def getId(self):
        return self.control_id

    def getPosition(self):
        return self.x, 200

    def getWidth(self):
        return 80

    def getHeight(self):
        return 40


class FocusWindow:
    def setFocus(self, control):
        self.events.append(('focus', control.getId()))
        self.focus_id = control.getId()


def focus_guide(value='Favourites', version='20.5', focus_id=4316):
    """Actual caller/focus methods; inert modal snapshots focus at dispatch.

    This contract capture is not Kodi's modal-stack implementation or native
    acceptance. No Kodi modules, profiles, providers or network are accessed.
    """
    scope = dict(FocusWindow=FocusWindow, debug=lambda *_: None,
                 favourites_navigation=pure_module('favourites_navigation'),
                 COMMAND_ACTIONS=defaultdict(list, LEFT=[1], RIGHT=[2], UP=[3], DOWN=[4],
                                             MENU=[117, 101]))
    for node in tree('gui.py').body:
        if isinstance(node, ast.Assign):
            try:
                literal = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    scope[target.id] = literal
    methods = {'onClick', 'openFavourites', 'setFocus', '_findControlAt',
               '_sameControl', '_getProgramFromControl', 'onActionEPGMode'}
    body = [node for node in class_node('TVGuide').body
            if isinstance(node, ast.Assign) or
            isinstance(node, ast.FunctionDef) and node.name in methods]
    captured = ast.ClassDef(name='TVGuide', bases=[ast.Name(id='FocusWindow', ctx=ast.Load())],
                            keywords=[], body=body, decorator_list=[])
    points = [node for node in tree('gui.py').body
              if isinstance(node, ast.ClassDef) and node.name == 'Point']
    module = ast.fix_missing_locations(ast.Module(body=points + [captured], type_ignores=[]))
    exec(compile(module, source_label('gui.py'), 'exec'), scope)
    ui = scope['TVGuide']()
    ui.events, ui.focus_id, ui.mode, ui.isClosing = [], focus_id, 'EPG', False
    ui.focusPoint = scope['Point']()
    ui.focusPoint.x, ui.focusPoint.y = 220, 220
    ui.controlAndProgramList = [NS(control=FocusControl(9001), program=object()),
                               NS(control=FocusControl(9002, 200), program=object())]
    ui.getFocusId = lambda: ui.focus_id

    def get_focus():
        if not ui.focus_id:
            raise RuntimeError('Non-Existent Control 0')
        # Return a fresh wrapper, not the object retained in the guide.
        return FocusControl(ui.focus_id, 200 if ui.focus_id == 9002 else 100)

    ui.getFocus = get_focus
    ui._showContextMenu = lambda program: ui.events.append(('context', program))
    for direction in ('left', 'right', 'up', 'down'):
        setattr(ui, '_' + direction,
                lambda point, name=direction: ui.events.append((name, point.x, point.y)))

    def dispatch(command):
        ui.events.append(('builtin', command, ui.focus_id))
        ui.saved_modal_focus = ui.focus_id

    scope.update(ADDON=NS(getSetting=lambda key: value),
                 xbmc=NS(getInfoLabel=lambda _: version, executebuiltin=dispatch),
                 RPC=NS(addons=NS(get_addons=lambda **_: {'addons': [
                     {'addonid': 'plugin.program.simple.favourites'}]})))
    return ui


class FavouritesFocus(unittest.TestCase):
    def setUp(self):
        if BASELINE:
            self.skipTest('Focus correction is not part of the original route baseline')

    def click(self, ui):
        ui.onClick(ui.C_MAIN_MOUSE_FAVOURITES)

    def test_saved_programme_is_focused_before_legacy_modal_snapshot(self):
        for version, value in product(('19.4', '20.5'), ('Favourites', '', None)):
            with self.subTest(version=version, value=value):
                ui = focus_guide(value, version)
                self.click(ui)
                self.assertEqual(ui.events, [('focus', 9002),
                    ('builtin', 'ActivateWindow(10134)', 9002)])
                self.assertEqual((ui.focusPoint.x, ui.focusPoint.y), (220, 220))

    def test_modelled_back_preserves_arrow_and_repeated_context_dispatch(self):
        ui = focus_guide()
        self.click(ui)
        # Model the transient button losing focus when hidden on return. This
        # checks pre-dispatch ordering, not native modal-stack acceptance.
        ui.focus_id = 0 if ui.saved_modal_focus == 4316 else ui.saved_modal_focus
        ui.events.clear()
        for action_id in (1, 2, 3, 4, 117, 101, 101):
            ui.onActionEPGMode(NS(getId=lambda: action_id))
        self.assertEqual(ui.events[:4], [(name, 240, 220)
                                        for name in ('left', 'right', 'up', 'down')])
        self.assertEqual(ui.events[4:], [('context', ui.controlAndProgramList[1].program)] * 3)

    def test_programme_category_action_bar_and_other_tools_are_untouched(self):
        for focus in (9002, 7000, 7100, 4312, 0):
            with self.subTest(focus=focus):
                ui = focus_guide(focus_id=focus)
                self.click(ui)
                self.assertEqual(ui.events, [('builtin', 'ActivateWindow(10134)', focus)])

    def test_provider_browser_and_other_guide_modes_are_untouched(self):
        for value, version, mode, command in (
                ('Simple Favourites', '20.5', 'EPG', ROUTES['Simple Favourites']),
                ('Favourites', '21.3', 'EPG', 'ActivateWindow(favouritesbrowser)'),
                ('Favourites', '22.0-RC2', 'EPG', 'ActivateWindow(favouritesbrowser)'),
                ('Favourites', '20.5', 'QUICKEPG', 'ActivateWindow(10134)'),
                ('Favourites', '20.5', 'TV', 'ActivateWindow(10134)')):
            with self.subTest(value=value, version=version, mode=mode):
                ui = focus_guide(value, version)
                ui.mode = mode
                self.click(ui)
                self.assertEqual(ui.events, [('builtin', command, 4316)])

    def test_empty_or_unmatched_saved_point_does_not_guess_first_programme(self):
        for empty in (False, True):
            ui = focus_guide()
            if empty:
                ui.controlAndProgramList.clear()
            else:
                ui.focusPoint.x = 1000
            self.click(ui)
            self.assertEqual(ui.events, [('builtin', 'ActivateWindow(10134)', 4316)])

    def test_unavailable_control_does_not_prevent_existing_dispatch(self):
        for failing_method in ('getFocusId', 'setFocus'):
            with self.subTest(method=failing_method):
                ui = focus_guide()

                def unavailable(*_):
                    raise RuntimeError('Control is unavailable')

                setattr(ui, failing_method, unavailable)
                self.click(ui)
                self.assertEqual(ui.events, [('builtin', 'ActivateWindow(10134)', 4316)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-ref', help='Read production files at this local Git ref')
    parser.add_argument('--baseline', action='store_true', help='Characterize old behavior, not candidate acceptance')
    parser.add_argument('--kodi-source-dir', type=Path, help='Directory with supplied kodi-{lane} exact-tag copies')
    options, remaining = parser.parse_known_args()
    SOURCE_REF = options.source_ref
    BASELINE = options.baseline
    KODI_SOURCE_DIR = options.kodi_source_dir
    if BASELINE and not SOURCE_REF:
        parser.error('--baseline requires an explicit --source-ref')
    print('BASELINE CHARACTERIZATION' if BASELINE else 'CANDIDATE REGRESSION',
          'source:', SOURCE_REF or 'selected worktree', flush=True)
    unittest.main(argv=[__file__] + remaining, verbosity=2)
