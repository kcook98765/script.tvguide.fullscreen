"""Artwork/preservation acceptance checks; no Kodi or runtime module imports."""
import hashlib
from io import BytesIO
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

from PIL import Image

# Resolve only our sibling test helper, including under python -I.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_contract import ARTWORK_COMMIT, ARTWORK_TREE, git, git_snapshot

ROOT = Path(__file__).resolve().parents[1]
BASE = 'c19f256333efbe7af12418312f17e00f99792dc2'
RETAINED = 'resources/screenshots/channel-management.png'
OMITTED = {'resources/screenshots/' + name + '.png' for name in (
    'fullscreen-guide', 'programme-actions', 'on-now', 'search-results')}


def original(path):
    return subprocess.check_output(['git', '-C', str(ROOT), 'show', BASE + ':' + path],
                                   env={'PATH': os.defpath})


def validate_image(raw, fmt, size):
    with Image.open(BytesIO(raw)) as image:
        image.load()
        assert image.format == fmt and image.size == size and image.mode == 'RGB'
        assert 'transparency' not in image.info
        assert not any(k in image.info for k in ('exif', 'icc_profile', 'comment', 'Description'))


class ArtworkChecks:
    """Asset preservation applies to both today's tree and the frozen artifact."""
    root = ROOT

    def test_exact_screenshot_dispositions_and_no_missing_current_links(self):
        self.assertEqual({p.relative_to(self.root).as_posix() for p in
                          (self.root / 'resources/screenshots').iterdir()}, {RETAINED})
        self.assertEqual((self.root / RETAINED).read_bytes(), original(RETAINED))
        manifest = ET.parse(self.root / 'addon.xml').getroot()
        self.assertEqual([e.text for e in manifest.findall(
            "extension[@point='xbmc.addon.metadata']/assets/screenshot")], [RETAINED])
        # A user README may link to the history rather than embed a screenshot.
        # Validate every screenshot link that it DOES advertise, not its layout.
        readme = (self.root / 'README.md').read_text()
        for path in re.findall(r'\]\((resources/screenshots/[^)]+)\)', readme):
            self.assertEqual(path, RETAINED)
            self.assertTrue((self.root / path).is_file())
        for path in OMITTED:
            self.assertFalse((self.root / path).exists())
            self.assertNotIn('](' + path + ')', readme)

    def test_artwork_contract_and_source_hash_documentation(self):
        provenance = (self.root / 'docs/artwork-provenance.md').read_text()
        for path, fmt, size in (('icon.png', 'PNG', (512, 512)),
                                ('fanart.jpg', 'JPEG', (1920, 1080))):
            raw = (self.root / path).read_bytes()
            validate_image(raw, fmt, size)
            self.assertNotEqual(raw, original(path))
        for path in ('icon.png', 'fanart.jpg', RETAINED, 'tools/generate_artwork.py'):
            raw = (self.root / path).read_bytes()
            self.assertIn(hashlib.sha256(raw).hexdigest(), provenance)
            # Updating prose must not auto-bless replacement artwork.
            self.assertEqual(raw, git('show', ARTWORK_COMMIT + ':' + path))

    def test_generator_reproduces_both_encoded_assets_without_external_input(self):
        generate = runpy.run_path(str(self.root / 'tools/generate_artwork.py'))['artwork']
        first, second = generate(), generate()
        self.assertEqual(set(first), {'icon.png', 'fanart.jpg'})
        self.assertEqual(first, second)
        for path, raw in first.items():
            self.assertEqual(raw, (self.root / path).read_bytes())

    def test_all_166_skin_images_preserved(self):
        paths = [p for p in (self.root / 'resources/skins').rglob('*')
                 if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif')]
        self.assertEqual(len(paths), 166)
        for path in paths:
            self.assertEqual(path.read_bytes(), original(path.relative_to(self.root).as_posix()))

    def test_image_contract_negative_controls(self):
        valid = (self.root / 'icon.png').read_bytes()
        for mode, size in (('RGBA', (512, 512)), ('RGB', (64, 64))):
            output = BytesIO()
            Image.new(mode, size).save(output, format='PNG')
            with self.assertRaises(AssertionError):
                validate_image(output.getvalue(), 'PNG', (512, 512))
        with self.assertRaises(AssertionError):
            validate_image(valid, 'JPEG', (512, 512))
        print('Asset negative controls rejected: alpha mode, wrong dimensions, wrong encoding')


class ArtworkTests(ArtworkChecks, unittest.TestCase):
    """Current artwork is preserved; runtime/metadata prose may evolve."""

    def test_artwork_preservation_negative_controls(self):
        with git_snapshot(ARTWORK_COMMIT) as root:
            skin = sorted((root / 'resources/skins').rglob('*.png'))[0]
            cases = [
                ('icon.png', 'test_artwork_contract_and_source_hash_documentation'),
                (RETAINED, 'test_exact_screenshot_dispositions_and_no_missing_current_links'),
                (skin.relative_to(root).as_posix(), 'test_all_166_skin_images_preserved'),
            ]
            for path, method in cases:
                with self.subTest(damaged=path):
                    file = root / path
                    raw = file.read_bytes()
                    changed = raw + b'\n'
                    file.write_bytes(changed)
                    # Even an edited provenance hash cannot bless damaged art.
                    provenance = root / 'docs/artwork-provenance.md'
                    text = provenance.read_text()
                    provenance.write_text(text.replace(hashlib.sha256(raw).hexdigest(),
                                                        hashlib.sha256(changed).hexdigest()))
                    check = ArtworkTests(method)
                    check.root = root
                    with self.assertRaises(AssertionError):
                        getattr(check, method)()
                    file.write_bytes(raw)
                    provenance.write_text(text)
            for path, addition in (('README.md', '\n![omitted](' + sorted(OMITTED)[0] + ')'),
                                   ('resources/screenshots/unrelated.png', 'unrelated')):
                file = root / path
                raw = file.read_bytes() if file.exists() else None
                file.write_bytes((raw or b'') + addition.encode())
                check = ArtworkTests('test_exact_screenshot_dispositions_and_no_missing_current_links')
                check.root = root
                with self.subTest(damaged=path), self.assertRaises(AssertionError):
                    check.test_exact_screenshot_dispositions_and_no_missing_current_links()
                if raw is None:
                    file.unlink()
                else:
                    file.write_bytes(raw)


class HistoricalArtworkTests(ArtworkChecks, unittest.TestCase):
    """Never point these artwork-only release assertions at the development tree."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert git('rev-parse', ARTWORK_COMMIT + '^{tree}').decode().strip() == ARTWORK_TREE
        fixture = git_snapshot(ARTWORK_COMMIT)
        cls.root = fixture.__enter__()
        cls.addClassCleanup(fixture.__exit__, None, None, None)

    def test_historical_readme_advertises_retained_capture(self):
        self.assertIn('](' + RETAINED + ')', (self.root / 'README.md').read_text())

    def test_manifest_non_artwork_semantics_preserved(self):
        before = ET.fromstring(original('addon.xml'))
        after = ET.parse(self.root / 'addon.xml').getroot()
        self.assertEqual(after.get('version'), '0.1.1')
        self.assertEqual([n.attrib for n in before.findall('requires/import')],
                         [n.attrib for n in after.findall('requires/import')])
        self.assertEqual(ET.tostring(before.find('requires')), ET.tostring(after.find('requires')))
        self.assertEqual(len(before.findall('extension')), len(after.findall('extension')))
        for old, new in zip(before.findall('extension'), after.findall('extension')):
            self.assertEqual(old.attrib, new.attrib)
            for child in old:
                if child.tag not in ('summary', 'news', 'assets'):
                    self.assertEqual(ET.tostring(child), ET.tostring(new.find(child.tag)))
        news = after.findtext("extension[@point='xbmc.addon.metadata']/news")
        self.assertTrue(news.startswith('0.1.1 Beta: artwork-only successor; runtime unchanged.'))
        self.assertNotIn('candidate', news.lower())
        self.assertNotIn('not published', news.lower())


if __name__ == '__main__':
    unittest.main(verbosity=2)
