"""Source-only package checks. Run with the selected Toolkit tooling interpreter.

Requires the preserved Git baseline and installed polib/Pillow; imports no add-on
or Kodi modules. Does not connect to Kodi, install dependencies or publish.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_contract import (ARTWORK_COMMIT, FLOORS, git_snapshot, safe_path,
                              validate_dependencies, validate_versions)


ROOT = Path(__file__).resolve().parents[1]
BASE = '6d1b9162289ccc20c3ba089302dc3a149150d0be'
LANGUAGES = json.loads((ROOT / 'tests/package_language_map.json').read_text('utf-8'))


def original(path):
    return subprocess.check_output(
        ['git', '-C', str(ROOT), 'show', BASE + ':' + path],
        cwd=str(ROOT), env={'PATH': os.defpath})


def catalog(raw):
    # Keep the independent manifest/version checks runnable without the PO parser.
    # Catalog checks still ERROR (never skip) when this declared tool is missing.
    import polib
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


def validate_manifest(root):
    old = ET.fromstring(original('addon.xml'))
    new = ET.parse(root / 'addon.xml').getroot()
    assert {k: v for k, v in old.attrib.items() if k != 'version'} == {
        k: v for k, v in new.attrib.items() if k != 'version'}
    validate_dependencies(new)
    assert [e.attrib for e in new.findall('extension')] == [
        {'point': 'xbmc.python.script', 'library': 'addon.py'},
        {'point': 'xbmc.service', 'library': 'service.py'},
        {'point': 'xbmc.addon.metadata'}]
    assert new.findtext("extension[@point='xbmc.python.script']/provides") == 'executable'
    for path in ('addon.py', 'service.py'):
        assert (root / path).is_file() and (root / path).read_bytes(), path
    meta = new.find("extension[@point='xbmc.addon.metadata']")
    old_meta = old.find("extension[@point='xbmc.addon.metadata']")
    for tag in ('disclaimer', 'license', 'platform', 'forum', 'email'):
        assert meta.findtext(tag) == old_meta.findtext(tag), tag
    for tag in ('website', 'source'):
        assert meta.findtext(tag) == 'https://github.com/kcook98765/script.tvguide.fullscreen', tag
    description = meta.findtext('description') or ''
    assert 'modernization Beta' in description
    credits = 'Thanks for the major contributions from: '
    assert credits in description
    assert description.split(credits)[1] == old_meta.findtext('description').split(credits)[1]
    assert meta.findtext('summary', '').strip()
    assert 0 < len(meta.findtext('news', '').strip()) <= 1500
    assert [(e.tag, e.text) for e in meta.findall('assets/*')] == [
        ('icon', 'icon.png'), ('fanart', 'fanart.jpg'),
        ('screenshot', 'resources/screenshots/channel-management.png')]
    for asset in meta.findall('assets/*'):
        safe_path(asset.text)
        assert (root / asset.text).is_file(), asset.text
    assert original('LICENSE.txt') == (root / 'LICENSE.txt').read_bytes()
    readme = (root / 'README.md').read_text('utf-8')
    for credit in ('primaeval', 'Tommy Winther', 'Thomas Geppert', 'Midraal',
                   'iainmacleod', 'im85288', 'RayW1986', 'andy', 'Zomboided',
                   'tycoo', 'kjb86', 'Doctor-Eggs', 'Marti Raudsepp'):
        assert credit in readme, credit
    assert '](LICENSE.txt)' in readme and '](THIRD-PARTY-NOTICES.txt)' in readme
    assert 'GPL v2 or later' in readme
    validate_versions(root)


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
        validate_manifest(ROOT)

    def test_dependency_negative_controls(self):
        import copy
        manifest = ET.parse(ROOT / 'addon.xml').getroot()
        for addon in FLOORS:
            for damage in ('missing', 'duplicate', 'optional', 'wrong-floor'):
                with self.subTest(addon=addon, damage=damage):
                    bad = copy.deepcopy(manifest)
                    requires = bad.find('requires')
                    node = requires.find("import[@addon='{}']".format(addon))
                    if damage == 'missing':
                        requires.remove(node)
                    elif damage == 'duplicate':
                        requires.append(copy.deepcopy(node))
                    elif damage == 'optional':
                        node.set('optional', 'true')
                    else:
                        node.set('version', '0.0.0')
                    with self.assertRaises(AssertionError):
                        validate_dependencies(bad)
        ET.SubElement(manifest.find('requires'), 'import', addon='unrelated', version='1.0.0')
        with self.assertRaises(AssertionError):
            validate_dependencies(manifest)

    def test_current_metadata_damage_and_consistent_future_version(self):
        paths = ('addon.xml', 'addon.py', 'service.py', 'README.md', 'changelog.txt',
                 'LICENSE.txt', 'icon.png', 'fanart.jpg',
                 'resources/screenshots/channel-management.png')
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as directory:
            root = Path(directory)
            for path in paths:
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, root / path)
            validate_manifest(root)
            raw = (root / 'addon.xml').read_text()
            for before, after in (('provider-name="primaeval"', 'provider-name="Other"'),
                                  ('GPLv2', 'MIT'), ('iainmacleod', 'Other'),
                                  ('<platform>all', '<platform>linux'),
                                  ('<provides>executable', '<provides>video'),
                                  ('library="service.py"', 'library="unrelated.py"'),
                                  ('<icon>icon.png', '<icon>../icon.png')):
                with self.subTest(damage=before):
                    self.assertIn(before, raw)
                    (root / 'addon.xml').write_text(raw.replace(before, after))
                    with self.assertRaises(AssertionError):
                        validate_manifest(root)
            for tag in ('summary', 'news'):
                damaged = ET.fromstring(raw)
                damaged.find("extension[@point='xbmc.addon.metadata']/" + tag).text = ''
                (root / 'addon.xml').write_bytes(ET.tostring(damaged))
                with self.subTest(empty=tag), self.assertRaises(AssertionError):
                    validate_manifest(root)
            (root / 'addon.xml').write_text(raw)
            for path in ('addon.py', 'service.py', 'icon.png', 'LICENSE.txt'):
                file = root / path
                saved = file.read_bytes()
                file.unlink()
                with self.subTest(missing=path), self.assertRaises((AssertionError, FileNotFoundError)):
                    validate_manifest(root)
                file.write_bytes(saved)
            # A deliberate future version, not a permanent 0.1.2 pin. Each
            # inconsistent intermediate state must fail; the complete bump passes.
            version = ET.fromstring(raw).get('version')
            future = '9.8.7' if version != '9.8.7' else '9.8.8'
            for path in ('addon.xml', 'changelog.txt', 'README.md'):
                file = root / path
                file.write_text(file.read_text().replace(version, future))
                if path != 'README.md':
                    with self.assertRaises(AssertionError):
                        validate_manifest(root)
            validate_manifest(root)
            evolved = ET.parse(root / 'addon.xml').getroot()
            meta = evolved.find("extension[@point='xbmc.addon.metadata']")
            credits = 'Thanks for the major contributions from: '
            meta.find('description').text = ('Maintained modernization Beta with a new fix. ' + credits +
                                             meta.findtext('description').split(credits)[1])
            meta.find('summary').text = 'Updated guide summary.'
            meta.find('news').text = future + ' Beta: a different maintenance fix.'
            (root / 'addon.xml').write_bytes(ET.tostring(evolved))
            validate_manifest(root)

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


class HistoricalPackageMetadataTests(unittest.TestCase):
    def test_artwork_era_manifest_metadata_and_entrypoint_identity(self):
        with git_snapshot(ARTWORK_COMMIT) as root:
            self.assertEqual(ET.parse(root / 'addon.xml').getroot().get('version'), '0.1.1')
            validate_manifest(root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
