"""Source-only package checks. Run with the selected Toolkit tooling interpreter.

Requires the preserved Git baseline and installed polib/Pillow; imports no add-on
or Kodi modules. Does not connect to Kodi, install dependencies or publish.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import unittest
import xml.etree.ElementTree as ET

import polib
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BASE = '6d1b9162289ccc20c3ba089302dc3a149150d0be'
LANGUAGES = json.loads((ROOT / 'tests/package_language_map.json').read_text('utf-8'))


def original(path):
    return subprocess.check_output(
        ['git', '-C', str(ROOT), 'show', BASE + ':' + path],
        cwd=str(ROOT), env={'PATH': os.defpath})


def catalog(raw):
    # Same comment normalization as official checker 0.0.36. Historical #empty
    # comments are not standard polib comments; never rewrite the catalog itself.
    text = raw.decode('utf-8')
    normalized = '\n'.join(
        '# ' + line[1:].lstrip() if line.startswith('#') else line
        for line in text.splitlines())
    po = polib.pofile(normalized)
    entries = [(e.msgctxt, e.msgid, e.msgstr, e.msgid_plural,
                sorted(e.msgstr_plural.items()), e.obsolete, e.flags)
               for e in po]
    return po, entries


def fallback(source, translation):
    """Model the ID/msgid freshness check in Kodi LocalizeStrings.cpp LoadPO."""
    result = {e.msgctxt: e.msgstr for e in translation if e.msgstr}
    translated = {e.msgctxt: e for e in translation if e.msgstr}
    for entry in source:
        old = translated.get(entry.msgctxt)
        if old is None or (old.msgid and old.msgid != entry.msgid):
            result[entry.msgctxt] = entry.msgid
    return result


class PackageMetadataTests(unittest.TestCase):
    def test_all_catalogs_byte_and_decoded_equivalence(self):
        self.assertEqual(len(LANGUAGES), 69)
        self.assertEqual(len(set(LANGUAGES.values())), 69)
        actual = {p.parent.name for p in (ROOT / 'resources/language').glob('*/strings.po')}
        self.assertEqual(actual, set(LANGUAGES.values()))
        old_source, _ = catalog(original('resources/language/English/strings.po'))
        new_source, _ = catalog((ROOT / 'resources/language/resource.language.en_gb/strings.po').read_bytes())
        total = 0
        for old, new in LANGUAGES.items():
            with self.subTest(language=old):
                before = original('resources/language/' + old + '/strings.po')
                after = (ROOT / 'resources/language' / new / 'strings.po').read_bytes()
                # The patch tool adds a final LF to the two historical files
                # lacking one. No other byte may change, even comments/headers.
                if old in ('English', 'German'):
                    self.assertFalse(before.endswith(b'\n'))
                    self.assertEqual(before + b'\n', after)
                else:
                    self.assertEqual(before, after, 'Keep every byte, including attribution/comments')
                old_po, old_entries = catalog(before)
                new_po, new_entries = catalog(after)
                self.assertEqual(old_po.metadata, new_po.metadata)
                self.assertEqual(old_entries, new_entries)
                self.assertEqual(len({e.msgctxt for e in new_po}), len(new_po))
                self.assertTrue(all(e.msgctxt and e.msgctxt[1:].isdigit() for e in new_po))
                self.assertEqual(fallback(old_source, old_po), fallback(new_source, new_po))
                total += len(new_po)
                print(json.dumps({'language': old, 'destination': new,
                                  'entries': len(new_po),
                                  'plurals': sum(bool(e.msgid_plural) for e in new_po),
                                  'baseline_sha256': hashlib.sha256(before).hexdigest(),
                                  'sha256': hashlib.sha256(after).hexdigest()}, ensure_ascii=False))
        print('Preserved {} entries across 69 catalogs; only English/German gain a final LF'.format(total))

    def test_manifest_metadata_and_entrypoint_identity(self):
        before = original('addon.xml')
        after = (ROOT / 'addon.xml').read_bytes()
        # Package semantics must survive legitimate dependency/startup changes.
        # Dependency correctness has its own check_dependencies_settings suite;
        # task-specific non-owned byte preservation is proved in private Git trees.
        old, new = ET.fromstring(before), ET.fromstring(after)
        self.assertEqual({k: v for k, v in old.attrib.items() if k != 'version'},
                         {k: v for k, v in new.attrib.items() if k != 'version'})
        self.assertEqual(new.get('version'), '0.1.1')
        self.assertEqual([(e.get('point'), e.get('library')) for e in new.findall('extension')],
                         [('xbmc.python.script', 'addon.py'), ('xbmc.service', 'service.py'),
                          ('xbmc.addon.metadata', None)])
        for entry in new.findall('extension')[:2]:
            self.assertTrue((ROOT / entry.get('library')).is_file())
            self.assertTrue((ROOT / entry.get('library')).read_bytes())
        meta = new.find("extension[@point='xbmc.addon.metadata']")
        old_meta = old.find("extension[@point='xbmc.addon.metadata']")
        for tag in ('disclaimer', 'license'):
            self.assertEqual(meta.findtext(tag), old_meta.findtext(tag))
        self.assertEqual(meta.findtext('website'), 'https://github.com/kcook98765/script.tvguide.fullscreen')
        self.assertIn('modernization Beta', meta.findtext('description'))
        self.assertEqual(meta.findtext('description').split('Thanks for the major contributions from: ')[1],
                         old_meta.findtext('description').split('Thanks for the major contributions from: ')[1])
        self.assertEqual(meta.findtext('source'), 'https://github.com/kcook98765/script.tvguide.fullscreen')
        self.assertTrue(meta.findtext('summary').strip())
        self.assertTrue(0 < len(meta.findtext('news').strip()) <= 1500)
        for asset in meta.findall('assets/*'):
            self.assertTrue((ROOT / asset.text).is_file())
        for path in ('LICENSE.txt',):
            self.assertEqual(original(path), (ROOT / path).read_bytes())

    def test_original_artwork_keeps_runtime_asset_contract(self):
        for path, size, fmt in (('icon.png', (512, 512), 'PNG'),
                                ('fanart.jpg', (1920, 1080), 'JPEG')):
            with Image.open(ROOT / path) as image:
                image.load()
                self.assertEqual(image.size, size)
                self.assertEqual(image.mode, 'RGB')
                self.assertEqual(image.format, fmt)
                self.assertNotIn('transparency', image.info)
            self.assertNotEqual(original(path), (ROOT / path).read_bytes())

    def test_ambiguous_variants_not_discarded(self):
        for name in ('Georgian', 'Haitian (Haitian Creole)', 'Vietnamese (Viet Nam)'):
            self.assertEqual(LANGUAGES[name], name)
        vi, _ = catalog((ROOT / 'resources/language/resource.language.vi_vn/strings.po').read_bytes())
        variant, _ = catalog((ROOT / 'resources/language/Vietnamese (Viet Nam)/strings.po').read_bytes())
        a = {e.msgctxt: e.msgstr for e in vi}
        b = {e.msgctxt: e.msgstr for e in variant}
        self.assertEqual(a['#30100'], 'Tổng Quan')
        self.assertEqual(b['#30100'], 'Chung')
        self.assertNotEqual(a['#30100'], b['#30100'])

    def test_data_loss_negative_controls(self):
        raw = original('resources/language/Vietnamese/strings.po')
        _, baseline = catalog(raw)
        _, changed = catalog(raw.replace('Tổng Quan'.encode(), b'General'))
        self.assertNotEqual(baseline, changed)
        _, changed_id = catalog(raw.replace(b'#30100', b'#39999'))
        self.assertNotEqual(baseline, changed_id)
        # Parser control: escaped newline and literal backslash+n are NOT equal.
        prefix = 'msgid ""\nmsgstr ""\n\nmsgctxt "#30000"\nmsgid "Text"\n'
        _, newline = catalog((prefix + 'msgstr "one\\ntwo"\n').encode())
        _, literal = catalog((prefix + 'msgstr "one\\\\ntwo"\n').encode())
        self.assertNotEqual(newline, literal)
        self.assertEqual(newline[0][2], 'one\ntwo')
        self.assertEqual(literal[0][2], 'one\\ntwo')


if __name__ == '__main__':
    unittest.main(verbosity=2)
