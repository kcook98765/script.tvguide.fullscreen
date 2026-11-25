"""Issue #88 bundled PopupMenu XML regression, NOT native mouse acceptance.

Nexus CGUIControlGroup::SendMouseEvent visits children in reverse XML order;
CGUIBaseContainer::OnMouseOver selects under the pointer and wheel events scroll
the container. Keep the transparent close button behind interactive controls and
the category container confined to its drawn column. No Kodi/stub execution.

Real pre-fix XML negative control (must fail):
  python3 tests/check_category_mouse_layering.py --skin-ref v0.1.2-beta
"""
import argparse
from pathlib import Path
import subprocess
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SKIN_REF = None
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
    options, remaining = parser.parse_known_args()
    SKIN_REF = options.skin_ref
    unittest.main(argv=[__file__] + remaining, verbosity=2)
