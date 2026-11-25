"""Actual-XML/Python binding regression for issue #79; not a Kodi GUI emulator.

Official skin conditions: https://kodi.wiki/view/List_of_boolean_conditions
String.IsEqual(info,string) is documented since v17. Test pre-fix XML with:
  python3 -B tests/check_stream_setup_visibility.py --skin-ref origin/main
No Kodi modules, profiles or network are used. Weather predicates are unrelated.
"""
import argparse
import ast
from pathlib import Path
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SKIN_REF = None
SKINS = ('Default', 'Dark', 'CatBar')
TABS = (('STRM', 101, 'strm'), ('FAVOURITES', 102, 'favourites'),
        ('ADDONS', 103, 'addons'), ('BROWSE', 104, 'browse'))


def read_skin(skin):
    path = 'resources/skins/{}/720p/script-tvguide-streamsetup.xml'.format(skin)
    if SKIN_REF:
        return subprocess.check_output(['git', 'show', SKIN_REF + ':' + path],
                                       cwd=ROOT, text=True)
    return (ROOT / path).read_text(encoding='utf-8')


class StreamSetupVisibility(unittest.TestCase):
    def test_python_marker_constants_and_focus_bindings(self):
        tree = ast.parse((ROOT / 'gui.py').read_text(encoding='utf-8'))
        dialog = next(n for n in tree.body
                      if isinstance(n, ast.ClassDef) and n.name == 'StreamSetupDialog')
        constants = {n.targets[0].id: ast.literal_eval(n.value)
                     for n in dialog.body if isinstance(n, ast.Assign)
                     and isinstance(n.targets[0], ast.Name)
                     and isinstance(n.value, ast.Constant)}
        self.assertEqual(constants['C_STREAM_VISIBILITY_MARKER'], 100)
        focus = next(n for n in dialog.body
                     if isinstance(n, ast.FunctionDef) and n.name == 'onFocus')
        branch = focus.body[0]
        for name, tab_id, marker in TABS:
            self.assertEqual(constants['C_STREAM_' + name + '_TAB'], tab_id)
            self.assertEqual(constants['VISIBLE_' + name], marker)
            expected = ast.parse(
                'controlId == self.C_STREAM_' + name + '_TAB', mode='eval').body
            self.assertEqual(ast.dump(branch.test), ast.dump(expected))
            expected_call = ast.parse(
                'self.getControl(self.C_STREAM_VISIBILITY_MARKER).setLabel(self.VISIBLE_'
                + name + ')').body
            self.assertEqual(ast.dump(ast.Module(body=branch.body, type_ignores=[])),
                             ast.dump(ast.Module(body=expected_call, type_ignores=[])))
            branch = branch.orelse[0] if branch.orelse else None
        self.assertIsNone(branch)
        init = next(n for n in dialog.body
                    if isinstance(n, ast.FunctionDef) and n.name == 'onInit')
        self.assertEqual(ast.dump(init.body[0]), ast.dump(ast.parse(
            'self.getControl(self.C_STREAM_VISIBILITY_MARKER).setLabel(self.VISIBLE_STRM)').body[0]))

    def test_exact_four_tab_groups_in_each_bundled_skin(self):
        for skin in SKINS:
            with self.subTest(skin=skin):
                text = read_skin(skin)
                self.assertIsNone(re.search(
                    r'StringCompare\s*\(\s*Control\.GetLabel\s*\(\s*100\s*\)',
                    text, re.IGNORECASE), 'Obsolete control-100 visibility predicate')
                root = ET.fromstring(text)
                marker = root.findall(".//control[@id='100']")
                self.assertEqual(len(marker), 1)
                self.assertEqual(marker[0].get('type'), 'label')
                self.assertEqual(marker[0].findtext('visible'), 'false')
                bindings = [(control.get('type'), visible.text)
                            for control in root.iter('control')
                            for visible in control.findall('visible')
                            if 'Control.GetLabel(100)' in (visible.text or '')]
                self.assertEqual(bindings, [
                    ('group', 'String.IsEqual(Control.GetLabel(100),{})'.format(value))
                    for _, _, value in TABS])
                for _, tab_id, _ in TABS:
                    tabs = root.findall(".//control[@id='{}']".format(tab_id))
                    self.assertEqual(len(tabs), 1)
                    self.assertEqual(tabs[0].get('type'), 'button')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skin-ref', help='Read bundled XML from Git ref (negative control)')
    options, remaining = parser.parse_known_args()
    SKIN_REF = options.skin_ref
    unittest.main(argv=[__file__] + remaining, verbosity=2)
