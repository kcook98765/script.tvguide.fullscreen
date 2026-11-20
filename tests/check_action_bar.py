"""Focused caller tests using disposable local profiles; no Kodi/stub imports."""
import ast
import importlib.util
import json
from pathlib import Path
import runpy
import sys
import tempfile
from types import SimpleNamespace
from typing import Any, Dict, List
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('action_bar', ROOT / 'action_bar.py')
assert SPEC is not None and SPEC.loader is not None
bar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bar)


class ActionBarTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'actions.json'
        self.commands: List[str] = []
        self.logs: List[Any] = []
        self.notices: List[Any] = []
        self.position = 0
        self.items: List[Any] = []
        self.control = SimpleNamespace(
            getSelectedPosition=lambda: self.position, reset=self.items.clear,
            addItems=self.items.extend, selectItem=lambda i: None)
        self.xbmc = SimpleNamespace(executebuiltin=self.commands.append,
                                    log=lambda *args: self.logs.append(args), LOGWARNING=2)
        self.vfs = SimpleNamespace(translatePath=lambda p: str(self.path))
        self.dialog = SimpleNamespace(notification=lambda *a: self.notices.append(a))
        self.gui = SimpleNamespace(Dialog=lambda: self.dialog, ListItem=self.item)
        self.scope: Dict[str, Any] = dict(action_bar=bar, xbmcvfs=self.vfs, xbmc=self.xbmc, xbmcgui=self.gui)
        tree = ast.parse((ROOT / 'gui.py').read_text())
        guide = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'TVGuide')
        methods = {n.name: n for n in guide.body if isinstance(n, ast.FunctionDef)}
        nodes: List[ast.stmt] = [methods[n] for n in ('loadActions', 'saveActions', 'onClick')]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual-gui-methods>', 'exec'), self.scope)
        self.display = next(n for n in ast.walk(guide) if isinstance(n, ast.If)
                            and ast.unparse(n.test) == 'self.has_action_bar'
                            and any(isinstance(child, ast.For) and
                                    ast.unparse(child.iter) == 'self.actions'
                                    for child in ast.walk(n)))
        self.ui = SimpleNamespace(C_MAIN_LOADING_CANCEL=1, C_MAIN_MOUSE_EXIT=2,
                                  C_MAIN_MENUBAR_BUTTON_EXIT=3, C_MAIN_ACTIONS=7100,
                                  isClosing=False, getControl=lambda c: self.control,
                                  has_action_bar=True, action_index=0)

    @staticmethod
    def item(label):
        item = SimpleNamespace(label=label)
        item.setArt = lambda art: setattr(item, 'art', art)
        return item

    def load(self):
        self.scope['loadActions'](self.ui)

    def click(self, position):
        self.position = position
        self.scope['onClick'](self.ui, 7100)

    def reset(self):
        with patch.dict(sys.modules, action_bar=bar, xbmcvfs=self.vfs, xbmcgui=self.gui):
            runpy.run_path(str(ROOT / 'actions.py'), run_name='__main__')

    def test_legacy_reorder_subset_display_save_reload_and_reset(self):
        legacy = [[' É té, [B]Now[/B] (TV)!\t\n\r😀 ', 'Action(Number2)', 'special://profile/My art (1),é.png'],
                  ['Find', 'Action(Number4)', 'https://example.invalid/icon?q=a,b'],
                  ['Exit', 'Action(Close)', '']]
        original = json.dumps(legacy).encode()
        self.path.write_bytes(original)
        self.load()
        self.assertEqual(self.path.read_bytes(), original)  # no implicit migration
        self.assertEqual([r[1] for r in self.ui.actions], ['now', 'search', 'quit'])
        exec(compile(ast.Module(body=[self.display], type_ignores=[]), '<actual-display>', 'exec'),
             dict(self.scope, self=self.ui))
        self.assertEqual([(i.label, i.art['icon']) for i in self.items],
                         [(r[0], r[2]) for r in legacy])
        self.click(0)
        self.assertEqual(self.commands, ['Action(Number2)'])
        self.assertTrue(self.scope['saveActions'](self.ui))
        saved = self.ui.actions
        self.load()
        self.assertEqual(self.ui.actions, saved)
        self.reset()
        self.assertEqual(self.notices[-1][1], 'Action Bar Reset')
        self.load()
        self.assertEqual(self.ui.actions, bar.defaults())
        bundled = json.loads((ROOT / 'resources/actions.json').read_text())
        self.assertEqual([[label, bar.command_at(bar.defaults(), i), icon]
                          for i, (label, key, icon) in enumerate(bar.defaults())], bundled)
        # Startup must not overwrite the user's file, even before gui loads it.
        startup = ast.parse((ROOT / 'addon.py').read_text())
        self.assertFalse(any(isinstance(n, ast.Constant) and n.value == bar.PROFILE
                             for n in ast.walk(startup)))

    def test_unknown_commands_never_reach_execution_or_rewrite_original(self):
        rows = [['bad', 'RunScript(evil.py)', ''], ['bad2', 'Action(Stop),Quit()', ''],
                ['bad3', 'unknown-id', ''], ['Good', 'Action(Stop)', '']]
        original = json.dumps(rows).encode()
        self.path.write_bytes(original)
        self.load()
        self.assertEqual(self.ui.actions, [['Good', 'stop', '']])
        self.assertIn('unsupported', self.logs[-1][0])
        self.assertEqual(self.path.read_bytes(), original)
        self.click(0)
        self.assertEqual(self.commands, ['Action(Stop)'])
        self.commands.clear()
        for row in rows[:3] + [['raw-known', 'Action(Stop)', ''], ['wrong-type', [], '']]:
            self.ui.actions = [row]
            self.click(0)
        self.assertEqual(self.commands, [])
        # Reintroduce the original raw resolver at the real caller boundary;
        # an inert output capture must detect it (never invoke Kodi).
        self.ui.actions = [rows[0]]
        with patch.object(bar, 'command_at', side_effect=lambda rows, pos: rows[pos][1]):
            self.click(0)
        with self.assertRaises(AssertionError):
            self.assertEqual(self.commands, [])
        self.assertEqual(self.commands, ['RunScript(evil.py)'])
        print('DETECTED unsafe original raw-command dispatch control')

    def test_missing_malformed_bounds_empty_and_cancelled_stale_indices(self):
        self.load()
        self.assertEqual(self.ui.actions, bar.defaults())
        self.assertFalse(self.path.exists())
        for data in (b'{', b'null', b'[[1,"stop",""]]', b'\xff', b'[' * 2000,
                     b'[["\\ud800", "stop", ""]]', b'[["Stop", "stop", "\\udfff"]]',
                     json.dumps([['x', 'stop', '']] * 33).encode(),
                     json.dumps([['x' * 1025, 'stop', '']]).encode(), b' ' * 65537):
            self.path.write_bytes(data)
            self.load()
            self.assertEqual(self.ui.actions, bar.defaults())
            self.assertEqual(self.path.read_bytes(), data)
            self.assertIn('malformed', self.logs[-1][0])
        self.path.write_text('[]')
        self.load()
        self.assertEqual(self.ui.actions, [])  # deliberately hide all
        for position in (-1, 0, 99, None, True):
            self.click(position)
        self.ui.actions = bar.defaults()
        for position in (-1, len(self.ui.actions), None, False):
            self.click(position)
        self.assertEqual(self.commands, [])

    def test_save_and_reset_failures_are_not_success_or_data_loss(self):
        original = b'[["Keep", "stop", ""]]'
        self.path.write_bytes(original)
        self.load()
        with patch.object(bar.os, 'replace', side_effect=OSError('denied')):
            self.assertFalse(self.scope['saveActions'](self.ui))
            self.assertEqual(self.notices[-1][1], 'Action bar save failed')
            self.reset()
            self.assertEqual(self.notices[-1][1], 'Action Bar Reset failed')
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])
        self.assertFalse(bar.save(str(self.path), [['bad', 'RunScript(evil.py)', '']]))
        self.assertEqual(self.path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main(verbosity=2)
