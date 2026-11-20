"""Focused guide-method captures; no Kodi, stubs or legacy module imports.

Each getControl/getFocus capture returns a fresh wrapper for an attached ID,
as Nexus's Python binding does. Only selected AST methods execute, against inert
controls/callbacks; this is not native UI or playback acceptance.
"""
import ast
from collections import defaultdict
import datetime
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
TREE = ast.parse((ROOT / 'gui.py').read_text(), feature_version=(3, 8))


class Control:
    def __init__(self, control_id):
        self.control_id = control_id

    def getId(self):
        return self.control_id

    def getPosition(self):
        return (100, 200)

    def getWidth(self):
        return 80

    def getHeight(self):
        return 40


class MissingControl:
    def getId(self):
        raise RuntimeError('Control is unavailable')


class WindowCapture:
    def setFocus(self, control):
        self.native_focus = control


def guide_class():
    namespace = {'WindowCapture': WindowCapture, 'datetime': datetime,
                 'debug': lambda *_: None,
                 'ADDON': SimpleNamespace(getSetting=lambda _: 'false'),
                 'COMMAND_ACTIONS': defaultdict(list, UP=[3], CHANNEL_LISTING=[99])}
    # Literal action/mode constants only: never execute imports or startup code.
    for node in TREE.body:
        if isinstance(node, ast.Assign):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    namespace[target.id] = value
    guide = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'TVGuide')
    methods = {'_sameControl', '_getProgramFromControl', '_getQuickProgramFromControl',
               'setFocus', 'setQuickFocus', 'onActionEPGMode', 'onActionQuickEPGMode'}
    body = [n for n in guide.body if isinstance(n, ast.Assign)
            or isinstance(n, ast.FunctionDef) and n.name in methods]
    # Capture the unchanged programme-selection tail, excluding unrelated buttons.
    click = next(n for n in guide.body if isinstance(n, ast.FunctionDef) and n.name == 'onClick')
    start = next(i for i, n in enumerate(click.body) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'program' for t in n.targets))
    click.body = click.body[start:]
    body.append(click)
    captured = ast.ClassDef(name='TVGuide', bases=[ast.Name(id='WindowCapture', ctx=ast.Load())],
                            keywords=[], body=body, decorator_list=[])
    points = [n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Point']
    module = ast.fix_missing_locations(ast.Module(body=points + [captured], type_ignores=[]))
    exec(compile(module, '<guide-control-capture>', 'exec'), namespace)
    return namespace['TVGuide'], namespace['Point']


Guide, Point = guide_class()


class ControlIdentity(unittest.TestCase):
    def setUp(self):
        self.guide = Guide()
        self.program = SimpleNamespace(channel=object(), startDate=None, endDate=None)
        self.stored = Control(9001)
        self.guide.controlAndProgramList = [SimpleNamespace(control=self.stored, program=self.program)]
        self.guide.quickControlAndProgramList = [SimpleNamespace(control=Control(9002), program=self.program)]
        self.guide.focusPoint = Point()
        self.guide.quickFocusPoint = Point()
        self.guide.getControl = lambda control_id: Control(control_id)

    def test_fresh_wrappers_resolve_programme_in_both_guides(self):
        for quick, control_id in [(False, 9001), (True, 9002)]:
            with self.subTest(quick=quick):
                fresh = self.guide.getControl(control_id)
                stored = (self.guide.quickControlAndProgramList if quick else
                          self.guide.controlAndProgramList)[0].control
                self.assertIsNot(stored, fresh)
                self.assertNotEqual(stored, fresh)
                lookup = self.guide._getQuickProgramFromControl if quick else self.guide._getProgramFromControl
                self.assertIs(lookup(fresh), self.program)

    def test_existing_wrapper_still_resolves(self):
        self.assertIs(self.guide._getProgramFromControl(self.stored), self.program)
        stored = self.guide.quickControlAndProgramList[0].control
        self.assertIs(self.guide._getQuickProgramFromControl(stored), self.program)

    def test_different_missing_and_unattached_ids_do_not_match(self):
        for lookup, entries in [(self.guide._getProgramFromControl, self.guide.controlAndProgramList),
                                (self.guide._getQuickProgramFromControl, self.guide.quickControlAndProgramList)]:
            for candidate in [Control(9999), None, object(), MissingControl(), Control(0), Control(-1), Control(None)]:
                with self.subTest(candidate=candidate):
                    self.assertIsNone(lookup(candidate))
            for invalid in [0, -1, None]:
                with self.subTest(unattached=invalid):
                    entries[:] = [SimpleNamespace(control=Control(invalid), program=self.program)]
                    self.assertIsNone(lookup(Control(invalid)))
                    self.assertIsNone(lookup(entries[0].control))
            entries[:] = [SimpleNamespace(control=None, program=self.program),
                          SimpleNamespace(control=MissingControl(), program=self.program),
                          SimpleNamespace(control=self.stored, program=self.program)]
            self.assertIs(lookup(Control(9001)), self.program)
            entries.clear()
            self.assertIsNone(lookup(Control(9001)))

    def test_selection_dispatches_associated_programme(self):
        calls = []
        self.guide.playOrChoose = calls.append
        for mode, control_id in [('EPG', 9001), ('QUICKEPG', 9002)]:
            with self.subTest(mode=mode):
                self.guide.mode = mode
                self.guide.onClick(control_id)
                self.assertEqual(calls, [self.program])
                calls.clear()
                self.guide.onClick(9999)
                self.assertEqual(calls, [])

    def test_focus_tracks_fresh_wrapper_in_both_guides(self):
        for quick, control_id in [(False, 9001), (True, 9002)]:
            with self.subTest(quick=quick):
                focus = self.guide.setQuickFocus if quick else self.guide.setFocus
                point = self.guide.quickFocusPoint if quick else self.guide.focusPoint
                fresh = self.guide.getControl(control_id)
                focus(fresh)
                self.assertEqual((point.x, point.y), (100, 220))
                self.assertIs(self.guide.native_focus, fresh)
                focus(Control(9999))
                self.assertEqual((point.x, point.y), (100, 220))

    def test_action_navigation_uses_focused_programme_centre(self):
        for quick, control_id in [(False, 9001), (True, 9002)]:
            with self.subTest(quick=quick):
                calls = []
                self.guide.getFocus = lambda: Control(control_id)
                self.guide.getFocusId = lambda: control_id
                self.guide._up = self.guide._quickUp = lambda p: calls.append((p.x, p.y))
                action = self.guide.onActionQuickEPGMode if quick else self.guide.onActionEPGMode
                action(SimpleNamespace(getId=lambda: 3))
                self.assertEqual(calls, [(140, 220)])
                calls.clear()
                self.guide.getFocus = lambda: Control(9999)
                action(SimpleNamespace(getId=lambda: 3))
                self.assertEqual(calls, [(0, 0)])

    def test_listing_action_resolves_fresh_wrapper(self):
        for quick, control_id in [(False, 9001), (True, 9002)]:
            with self.subTest(quick=quick):
                calls = []
                self.guide.getFocus = lambda: Control(control_id)
                self.guide.getFocusId = lambda: control_id
                self.guide.showListing = calls.append
                action = self.guide.onActionQuickEPGMode if quick else self.guide.onActionEPGMode
                action(SimpleNamespace(getId=lambda: 99))
                self.assertEqual(calls, [self.program.channel])


if __name__ == '__main__':
    unittest.main()
