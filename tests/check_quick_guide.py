"""Actual, scoped GUI/DB AST captures; no Kodi/stub/entrypoint imports.

Native controls, playback and metadata RPC are inert adapters, not runtime proof.
"""
import ast
from collections import defaultdict
import datetime
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from check_control_identity import Control
from check_metadata_search import Capture, Dialog, metadata

ROOT = Path(__file__).resolve().parents[1]


@lru_cache()
def source_tree(path):
    return ast.parse((ROOT / path).read_text(), feature_version=(3, 8))


def extract(path, name, methods, env):
    tree = source_tree(path)
    original = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            try:
                env[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    body = [n for n in original.body if isinstance(n, ast.FunctionDef) and n.name in methods]
    for node in original.body:
        if isinstance(node, ast.Assign):
            try:
                ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            body.append(node)
    cls = ast.ClassDef(name=name, bases=[], keywords=[], body=body, decorator_list=[])
    points = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Point']
    module = ast.fix_missing_locations(ast.Module(body=points + [cls], type_ignores=[]))
    exec(compile(module, path, 'exec'), env)
    return env[name]


def make_guide():
    commands = defaultdict(list, PLAY=[7], CLOSE=[10], MENU=[11], CHANNEL_LISTING=[12],
                           PAGE_UP=[13], UP=[3])
    env = dict(datetime=datetime, COMMAND_ACTIONS=commands,
               ADDON=NS(getSetting=lambda _: 'false'),
               xbmc=NS(log=lambda *a: None, LOGERROR=4, LOGDEBUG=0),
               timedelta_total_seconds=lambda d: d.total_seconds(),
               colors=NS(color_name={'white': 'white'}), remove_formatting=lambda s: 'white')
    cls = extract('gui.py', 'TVGuide', {
        'onActionQuickEPGMode', '_sameControl', '_getProgramFromControl',
        '_getQuickProgramFromControl', '_findQuickControlAt', 'playOrChoose',
        '_quickUp', '_quickMoveUp', 'onFocus', 'setControlLabel', 'lookupMetadata'}, env)
    obj = cls()
    obj.quickFocusPoint = NS(x=400, y=220)
    obj.quickEpgView = NS(left=200, right=1100, top=0, bottom=300)
    obj.quickChannelIdx = 0
    obj.quickViewStartDate = datetime.datetime(2026, 11, 21, 12)
    obj.controlAndProgramList = []
    obj.quickControlAndProgramList = []
    obj.has_cat_bar = False
    obj.mode = 'QUICKEPG'
    obj.getFocus = lambda: Control(9002)
    obj.osdProgram = NS(channel=NS(id='A'), title='Stale A')
    obj.currentProgram = obj.osdProgram
    obj.effects = []
    obj._hideQuickEpg = lambda: obj.effects.append('hide')
    obj.setQuickFocus = lambda c: obj.effects.append(('focus', c.getId()))
    return obj, env


def programme(title='Selected B', dates=True):
    start = datetime.datetime(2026, 11, 21, 12) if dates else None
    return NS(title=title, sub_title='Episode', categories='', season='', episode='',
              startDate=start, endDate=start + datetime.timedelta(hours=1) if dates else None,
              description='', channel=NS(id='B', title='Channel B', logo=None),
              imageSmall='', imageLarge='', is_movie='')


class QuickGuide(unittest.TestCase):
    def selected(self, program):
        obj, env = make_guide()
        obj.quickControlAndProgramList = [NS(control=Control(9002), program=program)]
        return obj, env

    def action(self, obj, value=7):
        obj.onActionQuickEPGMode(NS(getId=lambda: value))

    def test_play_uses_selected_before_hiding_not_stale_or_initial_osd(self):
        chosen = programme()
        stale_a = programme('Stale A')
        stale_a.channel.id = 'A'
        for stale in (stale_a, None, chosen):
            with self.subTest(stale=stale):
                obj, _ = self.selected(chosen)
                obj.osdProgram = stale
                def hide():
                    obj.effects.append('hide')
                    obj.quickControlAndProgramList.clear()
                obj._hideQuickEpg = hide
                obj.playOrChoose = lambda p: obj.effects.append(p)
                self.action(obj)
                self.assertEqual(obj.effects, ['hide', chosen])

    def test_no_focus_no_item_and_focus_repair_never_play(self):
        for focus, entries in ((None, []), (Control(9999), []),
                               (Control(9002), [NS(control=Control(9002), program=None)])):
            obj, _ = make_guide()
            obj.getFocus = lambda: focus
            obj.quickControlAndProgramList = entries
            obj.playOrChoose = lambda p: obj.effects.append(p)
            self.action(obj)
            self.assertEqual(obj.effects, [])
        obj, _ = self.selected(programme())
        def missing():
            raise RuntimeError('no native focus')
        obj.getFocus = missing
        obj.playOrChoose = lambda p: self.fail('focus repair must not play')
        self.action(obj)
        self.assertEqual(obj.effects, [('focus', 9002)])
        obj.quickControlAndProgramList.clear()
        obj.effects.clear()
        self.action(obj)
        self.assertEqual(obj.effects, [])

    def test_dateless_channel_placeholder_reaches_existing_router(self):
        for chosen in (programme('', dates=False), NS(channel=NS(id='B'))):
            for stale in (None, programme('Stale A')):
                with self.subTest(chosen=chosen, stale=stale):
                    obj, _ = self.selected(chosen)
                    obj.osdProgram = stale
                    obj.player = NS(isPlaying=lambda: False)
                    obj.playChannel = lambda channel, p: obj.effects.append((channel, p)) or True
                    self.action(obj)
                    self.assertEqual(obj.effects, ['hide', (chosen.channel, chosen)])

    def test_listing_context_and_back_preserved(self):
        chosen = programme()
        for action, expected in ((10, 'hide'), (11, chosen), (12, chosen.channel)):
            obj, _ = self.selected(chosen)
            obj.showListing = obj._showContextMenu = obj.effects.append
            self.action(obj, action)
            self.assertEqual(obj.effects, [expected])

    def test_up_wrap_uses_actual_db_final_page_for_arrow_page_and_wheel(self):
        dbcls = extract('source.py', 'Database', {'_getQuickEPGView'}, {'datetime': datetime})
        db = dbcls()
        db._updateChannelAndProgramListCaches = lambda *a: None
        db._getProgramList = lambda *a: []
        for total in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9):
            for mode in ('arrow', 'page', 'wheel', 'scroll'):
                with self.subTest(total=total, mode=mode):
                    obj, env = make_guide()
                    obj.database = NS(getNumberOfChannels=lambda: total)
                    obj._findQuickControlAbove = lambda p: None
                    db._getChannelList = lambda **kw: list(range(total))
                    captures = []
                    obj.onRedrawQuickEPG = lambda start, date, **kw: captures.append(
                        (start, db._getQuickEPGView(start, date, None, False, None), kw))
                    if mode == 'arrow':
                        self.action(obj, 3)
                    elif mode == 'page':
                        self.action(obj, 13)
                    elif mode == 'wheel':
                        self.action(obj, env['ACTION_MOUSE_WHEEL_UP'])
                    else:
                        obj._quickMoveUp(1, scrollEvent=True)
                    expected = ((total - 1) // 3) * 3 if total else 0
                    requested, (actual, channels, _), kw = captures[-1]
                    self.assertEqual((requested, actual), (expected, expected))
                    self.assertEqual(channels, list(range(total))[expected:expected + 3])
                    self.assertEqual('focusFunction' in kw, mode != 'scroll')

    def test_up_within_page_and_existing_control_does_not_wrap(self):
        obj, _ = make_guide()
        obj.quickChannelIdx = 6
        obj.database = NS(getNumberOfChannels=lambda: self.fail('must not query count'))
        calls = []
        obj.onRedrawQuickEPG = lambda start, *a, **kw: calls.append(start)
        obj._findQuickControlAbove = lambda p: None
        obj._quickUp(NS(x=0, y=0))
        obj._quickMoveUp(3)
        obj._quickMoveUp(1)
        self.assertEqual(calls, [3, 3, 5])
        obj._findQuickControlAbove = lambda p: Control(9001)
        obj._quickUp(NS(x=0, y=0))
        self.assertEqual(calls, [3, 3, 5])
        self.assertEqual(obj.effects, [('focus', 9001)])

    def focus_capture(self, obj):
        labels = {}
        def control(cid):
            return NS(setLabel=lambda text: labels.update({cid: text}),
                      setColorDiffuse=lambda c: None, setPercent=lambda p: None)
        obj.setControlText = obj.setControlImage = obj.setControlVisible = lambda *a: None
        obj.formatTime = lambda t: '12:00'
        obj.formatDateTodayTomorrow = lambda t: 'Today'
        obj.percent = lambda *a: 0
        obj.category = 'All Channels'
        obj.C_MAIN_IMAGE = 7023  # Existing non-alternative image slot; image calls are inert.
        obj.tvdb_urls = {}
        obj.focusPoint = NS(x=0, y=0)
        obj._findControlBelow = obj._findControlOnRight = obj._findControlAbove = lambda p: None
        # Use real ID association methods with fresh control wrappers.
        obj.getControl = lambda cid: Control(cid) if cid == 9002 else control(cid)
        return labels

    def test_actual_focus_callers_clear_time_and_main_subtitle(self):
        for mode in ('EPG', 'QUICKEPG'):
            with self.subTest(mode=mode):
                chosen = programme()
                obj, env = self.selected(chosen)
                labels = self.focus_capture(obj)
                obj.mode = mode
                env['ADDON'].getSetting = lambda key: 'true' if key == 'epg.subtitle' else 'false'
                obj.controlAndProgramList = [NS(control=Control(9002), program=chosen)]
                obj.onFocus(9002)
                time = obj.C_MAIN_TIME if mode == 'EPG' else obj.C_QUICK_EPG_TIME
                self.assertTrue(labels[time])
                if mode == 'EPG':
                    self.assertEqual(labels[obj.C_MAIN_SUBTITLE], 'Episode')
                chosen.startDate = chosen.endDate = None
                chosen.title = chosen.sub_title = ''
                obj.onFocus(9002)
                self.assertEqual(labels[time], '')
                if mode == 'EPG':
                    self.assertEqual(labels[obj.C_MAIN_SUBTITLE], '')
                    self.assertEqual(labels[obj.C_MAIN_TIME_AND_DAY], '')

    def test_label_none_missing_optional_and_unicode(self):
        obj, _ = make_guide()
        labels = []
        obj.getControl = lambda cid: NS(setLabel=labels.append) if cid == 1 else None
        for text in ('Café 日本語', '', None, ' ', 'Next'):
            obj.setControlLabel(1, text)
            obj.setControlLabel(999, text)
        self.assertEqual(labels, ['Café 日本語', '', ' ', 'Next'])

    def test_quick_focus_drives_actual_metadata_adapter_with_cancel_and_empty_controls(self):
        for title, choice in (('Selected B', 0), ('Selected B', -1), ('', 0)):
            with self.subTest(title=title, choice=choice):
                chosen = programme(title)
                obj, env = self.selected(chosen)
                self.focus_capture(obj)
                rpc, dialog = Capture(), Dialog(choice=choice, query=title)
                env['xbmc'].executeJSONRPC = rpc
                env['xbmcgui'] = NS(Dialog=lambda: dialog)
                obj.onFocus(9002)
                with patch.dict('sys.modules', metadata_search=metadata):
                    obj.lookupMetadata()
                if choice < 0 or not title:
                    self.assertEqual(rpc.windows(), [])
                else:
                    self.assertEqual(dialog.calls[1][2], title)
                    uri = rpc.windows()[0]['params']['parameters'][0]
                    self.assertEqual(parse_qs(urlsplit(uri).query)['query'], [title])
                self.assertIs(obj.focusedProgram, chosen)
                obj.onFocus(9999)
                self.assertIsNone(obj.focusedProgram)


if __name__ == '__main__':
    unittest.main()
