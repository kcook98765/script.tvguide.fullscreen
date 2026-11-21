"""Actual-XML regression for ONLY the two optional logo-widget conditions.

This models reviewed Kodi legacy conversion, not C++ execution or native GUI:
AddonSettings.cpp retains separator slots in categorySettings and adds relative
indices in ParseOldCondition; enum becomes CSettingInt, bool CSettingBool.
Omega 21.3 SettingDependency.cpp delegates equality to setting->Equals;
Setting.cpp bool Equals/fromString accepts true/false, whereas int fromString
rejects nonnumeric trailing input (including 'true'). No Python truthiness or
int/bool equality is used. Model inputs are bounded to these XML declarations.

Reviewed AddonSettings.cpp tags: 19.4-Matrix, 20.5-Nexus, 21.3-Omega,
22.0rc2-Piers (xbmc/xbmc, xbmc/addons/settings/AddonSettings.cpp).
Typed comparison: 21.3-Omega, xbmc/settings/lib/{Setting,SettingDependency}.cpp.
Run this same settled regression against pre-fix XML, expecting assertion failures:
  python -B tests/check_logo_settings_visibility.py --settings-ref a92d17858b01dc6201a52ccfbd1f163f600acd78
No add-on, Kodi, profile, network or settings action is executed.
"""
import argparse
from itertools import product
from pathlib import Path
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
WIDGETS = ('xmltv.logos', 'addon.logos')
SETTINGS_TEXT = None


def logo_rows(text):
    category = next(c for c in ET.fromstring(text).findall('category')
                    if c.find("setting[@id='logos.enabled']") is not None)
    # Do NOT discard separators: Kodi stores a nullptr slot for each one.
    return category.findall('setting')


def dependency(rows, widget):
    index = next(i for i, row in enumerate(rows) if row.get('id') == widget)
    match = re.fullmatch(r'eq\((-\d+),(true|false|[0-2])\)', rows[index].get('visible'))
    assert match, 'Only the two reviewed single-eq logo conditions are modeled'
    target = index + int(match[1])
    assert 0 <= target < len(rows)
    referenced = rows[target]
    assert referenced.get('id'), 'A separator cannot be a dependency'
    return referenced, match[2]


def typed_equals(row, stored, literal):
    """Bounded bool/enum Equals model, not a general Kodi condition engine."""
    if row.get('type') == 'bool':
        assert stored in ('true', 'false')
        return literal.lower() in ('true', 'false') and stored == literal.lower()
    assert row.get('type') == 'enum'
    assert row.get('values') == 'None|Folder|Url' and row.get('entries') is None
    assert stored in ('0', '1', '2')
    # CSettingInt::fromString must consume the entire decimal comparison string.
    return re.fullmatch(r'[0-2]', literal) is not None and int(stored) == int(literal)


def visible(rows, widget, values):
    row, literal = dependency(rows, widget)
    return typed_equals(row, values[row.get('id')], literal)


class LogoSettingsVisibility(unittest.TestCase):
    def setUp(self):
        text = SETTINGS_TEXT if SETTINGS_TEXT is not None else (
            ROOT / 'resources/settings.xml').read_text(encoding='utf-8')
        self.rows = logo_rows(text)

    def test_actual_xml_dependencies_target_enabled(self):
        self.assertEqual([r.get('id') for r in self.rows[:9]], [
            None, 'logos.enabled', 'logos.source', 'logos.folder', 'logos.url',
            'logos.keep', None, 'xmltv.logos', 'addon.logos'])
        for widget in WIDGETS:
            with self.subTest(widget=widget):
                row, literal = dependency(self.rows, widget)
                self.assertEqual((row.get('id'), row.get('type'), literal),
                                 ('logos.enabled', 'bool', 'true'))

    def test_widgets_follow_enabled_independent_of_source_and_keep(self):
        for enabled, source, keep, widget in product(
                ('true', 'false'), ('0', '1', '2'), ('true', 'false'), WIDGETS):
            with self.subTest(enabled=enabled, source=source, keep=keep, widget=widget):
                values = {'logos.enabled': enabled, 'logos.source': source, 'logos.keep': keep}
                self.assertIs(visible(self.rows, widget, values), enabled == 'true')

    def test_typed_equality_rejects_enum_true_even_for_folder_one(self):
        enabled, source = self.rows[1:3]
        for stored in ('0', '1', '2'):
            self.assertFalse(typed_equals(source, stored, 'true'))
            self.assertTrue(typed_equals(source, stored, stored))
        for stored in ('true', 'false'):
            self.assertTrue(typed_equals(enabled, stored, stored))
            self.assertFalse(typed_equals(enabled, stored, 'false' if stored == 'true' else 'true'))

    def test_original_offsets_hide_both_widgets_for_all_sources(self):
        # Only an in-memory negative control; never rewrite actual settings XML.
        for widget, old_condition in zip(WIDGETS, ('eq(-5,true)', 'eq(-6,true)')):
            next(r for r in self.rows if r.get('id') == widget).set('visible', old_condition)
            row, literal = dependency(self.rows, widget)
            self.assertEqual((row.get('id'), row.get('type'), literal),
                             ('logos.source', 'enum', 'true'))
        for enabled, source, keep, widget in product(
                ('true', 'false'), ('0', '1', '2'), ('true', 'false'), WIDGETS):
            values = {'logos.enabled': enabled, 'logos.source': source, 'logos.keep': keep}
            self.assertIs(visible(self.rows, widget, values), False)
        print('DETECTED original offsets: 24/24 hidden, including 12/12 enabled cases; '
              'XML/source model only, not native GUI proof')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--settings-ref', help='Read actual settings XML from this Git ref instead')
    options, remaining = parser.parse_known_args()
    if options.settings_ref:
        SETTINGS_TEXT = subprocess.check_output(
            ['git', 'show', options.settings_ref + ':resources/settings.xml'], cwd=ROOT, text=True)
    unittest.main(argv=[__file__] + remaining, verbosity=2)
