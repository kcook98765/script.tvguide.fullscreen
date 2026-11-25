"""Issue #88 PopupMenu XML and category-write regressions, not native acceptance.

Nexus CGUIControlGroup::SendMouseEvent visits children in reverse XML order;
CGUIBaseContainer::OnMouseOver selects under the pointer and wheel events scroll
the container. Keep the transparent close button behind interactive controls and
the category container confined to its drawn column. The M3U write check executes
only the source-preservation transformation with synthetic data. No Kodi/stubs.

Real pre-fix XML negative control (must fail):
  python3 tests/check_category_mouse_layering.py --skin-ref v0.1.2-beta

Removal-order negative control (must fail in both editors):
  python3 tests/check_category_mouse_layering.py --gui-ref 529582c9421dc2aa74462892be134ae36b3936f2
"""
import argparse
import ast
import io
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SKIN_REF = None
GUI_REF = None
SKINS = ('Default', 'CatBar')


def read_skin(skin):
    path = 'resources/skins/{}/720p/script-tvguide-menu.xml'.format(skin)
    if SKIN_REF:
        return ET.fromstring(subprocess.check_output(
            ['git', 'show', SKIN_REF + ':' + path], cwd=ROOT))
    return ET.parse(ROOT / path).getroot()


def control(root, control_id):
    matches = root.findall(".//control[@id='{}']".format(control_id))
    if len(matches) != 1:
        raise AssertionError('Expected one control {}'.format(control_id))
    return matches[0]


class CategoryWriteOrder(unittest.TestCase):
    def editor(self, editor, operation, selected, saved):
        source = (subprocess.check_output(['git', 'show', GUI_REF + ':gui.py'],
                                         cwd=ROOT).decode() if GUI_REF else
                  (ROOT / 'gui.py').read_text())
        cls, = [n for n in ast.parse(source).body
                if isinstance(n, ast.ClassDef) and n.name == editor]
        method, = [n for n in cls.body
                   if isinstance(n, ast.FunctionDef) and n.name == 'onAction']
        # Run the actual read/edit/write suite, including its cancellation return,
        # without importing Kodi or exercising unrelated navigation/rendering.
        suite, = [body for n in ast.walk(method) if isinstance(n, ast.If)
                  for body in (n.body, n.orelse)
                  if any(isinstance(s, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id == 'lines'
                                 for t in s.targets) for s in body)]
        start = next(i for i, n in enumerate(suite) if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == 'f' for t in n.targets))
        function = ast.FunctionDef(name='edit', args=ast.arguments(
            posonlyargs=[], args=[ast.arg(arg='ret'), ast.arg(arg='dialog')],
            kwonlyargs=[], kw_defaults=[], defaults=[]),
            body=suite[start:], decorator_list=[])
        code = compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])),
                       'gui.py:category-editor', 'exec')
        output = io.StringIO()
        writes = []

        def file(path, mode):
            if mode == 'rb':
                return io.StringIO(saved)
            writes.append(path)
            return SimpleNamespace(write=output.write, close=lambda: None)

        def multiselect(heading, names):
            self.assertEqual(names, sorted(names))
            return selected

        state = SimpleNamespace(category='Custom', selected_category='Custom',
                                database=SimpleNamespace(getChannelList=lambda **kw:
                                    [SimpleNamespace(title=n) for n in ['New', 'Zulu']]))
        env = dict(self=state,
                   dialog=SimpleNamespace(multiselect=multiselect),
                   xbmcvfs=SimpleNamespace(File=file))
        exec(code, env)
        env['edit'](operation, env['dialog'])
        return output.getvalue(), writes

    def test_remove_preserves_saved_occurrences_in_both_editors(self):
        saved = ('Zulu=Custom\nSame=Custom\nBeta=Custom\nSame=Custom\n'
                 'Alpha=Custom\nZulu=Other\nAlpha=Other\n')
        # Sorted chooser: Alpha, Beta, Same(first), Same(second), Zulu.
        cases = [([], ['Zulu', 'Same', 'Beta', 'Same', 'Alpha']),
                 ([2], ['Zulu', 'Beta', 'Same', 'Alpha']),
                 ([3], ['Zulu', 'Same', 'Beta', 'Alpha']),
                 ([1, 3], ['Zulu', 'Same', 'Alpha']),
                 ([0, 1, 2, 3, 4], [])]
        for editor, remove in [('PopupMenu', 1), ('CatMenu', 2)]:
            for indices, remaining in cases:
                with self.subTest(editor=editor, indices=indices):
                    actual, writes = self.editor(editor, remove, indices, saved)
                    self.assertEqual(actual, ''.join(n + '=Custom\n' for n in remaining)
                                     + 'Zulu=Other\nAlpha=Other\n')
                    self.assertEqual(len(writes), 1)
            with self.subTest(editor=editor, operation='cancel'):
                self.assertEqual(self.editor(editor, remove, None, saved), ('', []))
            with self.subTest(editor=editor, operation='empty names'):
                actual, _ = self.editor(editor, remove, [], '=Custom\n' + saved)
                self.assertEqual(actual, saved)  # Existing confirmed-remove cleanup.
            with self.subTest(editor=editor, operation='clear'):
                actual, _ = self.editor(editor, remove + 1, [], saved)
                self.assertEqual(actual, 'Zulu=Other\nAlpha=Other\n')
            with self.subTest(editor=editor, operation='add'):
                actual, _ = self.editor(editor, remove - 1, [0], saved)
                self.assertEqual(actual, saved.replace('Alpha=Custom\n',
                                                     'Alpha=Custom\nNew=Custom\n'))
                restored, _ = self.editor(editor, remove, [2], actual)
                self.assertEqual(restored, saved)  # Add/remove has zero net change.

    def test_m3u_startup_preserves_order_and_adds_members(self):
        tree = ast.parse((ROOT / 'gui.py').read_text())
        block, = [n for n in ast.walk(tree) if isinstance(n, ast.If)
                  and isinstance(n.test, ast.Name) and n.test.id == 'import_m3u']
        start, = [i for i, n in enumerate(block.body) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'categories'
                          for t in n.targets) and isinstance(n.value, ast.Dict)]
        end = next(i for i in range(start, len(block.body))
                   if isinstance(block.body[i], ast.For)
                   and isinstance(block.body[i].target, ast.Name)
                   and block.body[i].target.id == 'cat')
        # Execute the actual saved-lines -> additive merge -> write only.
        code = compile(ast.Module(body=block.body[start:end + 1], type_ignores=[]),
                       'gui.py:category-preservation', 'exec')

        class Label(str):
            def __hash__(self):
                return int(self)  # Fixed hashes: independent of PYTHONHASHSEED.

        class SavedLine(str):
            def rsplit(self, *args):
                name, category = super().rsplit(*args)
                return Label(name), category

        saved = ['3=Custom', '1=Custom', '3=Custom', '2=Other', '1=Other']
        expected = '3=Custom\n1=Custom\n4=Custom\n2=Other\n1=Other\n5=New\n'
        for _ in range(2):  # Repeated ordinary startup must remain stable.
            output = io.StringIO()
            env = dict(lines=[SavedLine(line) for line in saved],
                       stream_categories={Label('1'): 'Custom', Label('4'): 'Custom',
                                          Label('5'): 'New'},
                       stream_id_categories={'known': 'Custom', 'missing': 'Other'},
                       channelNames={'known': Label('4')},
                       xbmcvfs=SimpleNamespace(File=lambda *args: output))
            exec(code, env)
            self.assertEqual(output.getvalue(), expected)
            saved = output.getvalue().splitlines()


class CategoryMouseLayering(unittest.TestCase):
    def test_close_is_behind_categories_add_and_action_controls(self):
        for skin in SKINS:
            with self.subTest(skin=skin):
                root = read_skin(skin)
                siblings = list(root.find('controls'))
                close = control(root, 4015)
                # Same parent: reverse child order applies directly, not through
                # a guessed group/renderer or a simulated control click.
                targets = [c for c in siblings if c.get('type') in ('button', 'list')
                           and c is not close]
                self.assertIn(control(root, 7004), targets)
                self.assertIn(control(root, 80003), targets)
                self.assertIn(control(root, 4007), targets)  # Stream Setup
                self.assertTrue(all(siblings.index(close) < siblings.index(c)
                                    for c in targets),
                                'Fullscreen close must not intercept category/add/action input')
                self.assertEqual(close.findtext('visible'), 'true')
                self.assertEqual([close.findtext(tag) for tag in
                                  ('posx', 'posy', 'width', 'height')],
                                 ['0', '0', '1280', '720'])
                self.assertFalse(close.findtext('texturefocus'))
                self.assertFalse(close.findtext('texturenofocus'))

    def test_category_hit_bounds_match_existing_item_column(self):
        for skin in SKINS:
            with self.subTest(skin=skin):
                category = control(read_skin(skin), 7004)
                self.assertEqual(category.findtext('width'), '200',
                                 'Category hover/wheel bounds must not span blank/details areas')
                for tag in ('itemlayout', 'focusedlayout'):
                    self.assertEqual(category.find(tag).get('width'), '200')
                    self.assertEqual(category.find(tag).get('height'), '45')
                self.assertEqual([category.findtext(tag) for tag in
                                  ('left', 'top', 'height', 'orientation', 'visible')],
                                 ['20', '65', '625', 'vertical', 'true'])

    def test_existing_focus_navigation_and_add_button_geometry(self):
        for skin in SKINS:
            with self.subTest(skin=skin):
                root = read_skin(skin)
                default = root.find('defaultcontrol')
                self.assertEqual((default.text, default.get('always')), ('4000', 'false'))
                category = control(root, 7004)
                self.assertEqual([category.findtext(tag) for tag in
                                  ('onup', 'ondown', 'onleft', 'onright')],
                                 ['80003', '4006', '1', '4006'])
                add = control(root, 80003)
                self.assertEqual([add.findtext(tag) for tag in
                                  ('posx', 'posy', 'width', 'height', 'visible')],
                                 ['20', '20', '200', '40', 'true'])
                self.assertEqual([add.findtext(tag) for tag in
                                  ('onup', 'ondown', 'onright')], ['-', '7004', '4006'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skin-ref', help='Read actual bundled XML from a Git ref (negative control)')
    parser.add_argument('--gui-ref', help='Read gui.py from a Git ref (write-order negative control)')
    options, remaining = parser.parse_known_args()
    SKIN_REF = options.skin_ref
    GUI_REF = options.gui_ref
    unittest.main(argv=[__file__] + remaining, verbosity=2)
