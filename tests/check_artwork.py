"""Artwork/preservation acceptance checks; no Kodi or runtime module imports."""
import hashlib
from io import BytesIO
import os
from pathlib import Path
import runpy
import subprocess
import unittest
import xml.etree.ElementTree as ET

from PIL import Image

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


class ArtworkTests(unittest.TestCase):
    def test_exact_screenshot_dispositions_and_no_missing_current_links(self):
        self.assertEqual({p.relative_to(ROOT).as_posix() for p in
                          (ROOT / 'resources/screenshots').iterdir()}, {RETAINED})
        self.assertEqual((ROOT / RETAINED).read_bytes(), original(RETAINED))
        manifest = ET.parse(ROOT / 'addon.xml').getroot()
        self.assertEqual([e.text for e in manifest.findall(
            "extension[@point='xbmc.addon.metadata']/assets/screenshot")], [RETAINED])
        readme = (ROOT / 'README.md').read_text()
        self.assertIn('](' + RETAINED + ')', readme)
        for path in OMITTED:
            self.assertFalse((ROOT / path).exists())
            self.assertNotIn('](' + path + ')', readme)

    def test_artwork_contract_and_source_hash_documentation(self):
        provenance = (ROOT / 'docs/artwork-provenance.md').read_text()
        for path, fmt, size in (('icon.png', 'PNG', (512, 512)),
                                ('fanart.jpg', 'JPEG', (1920, 1080))):
            raw = (ROOT / path).read_bytes()
            validate_image(raw, fmt, size)
            self.assertNotEqual(raw, original(path))
        for path in ('icon.png', 'fanart.jpg', RETAINED, 'tools/generate_artwork.py'):
            self.assertIn(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), provenance)

    def test_generator_reproduces_both_encoded_assets_without_external_input(self):
        generate = runpy.run_path(str(ROOT / 'tools/generate_artwork.py'))['artwork']
        first, second = generate(), generate()
        self.assertEqual(set(first), {'icon.png', 'fanart.jpg'})
        self.assertEqual(first, second)
        for path, raw in first.items():
            self.assertEqual(raw, (ROOT / path).read_bytes())

    def test_all_166_skin_images_preserved(self):
        paths = [p for p in (ROOT / 'resources/skins').rglob('*')
                 if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif')]
        self.assertEqual(len(paths), 166)
        for path in paths:
            self.assertEqual(path.read_bytes(), original(path.relative_to(ROOT).as_posix()))

    def test_manifest_non_artwork_semantics_preserved(self):
        before = ET.fromstring(original('addon.xml'))
        after = ET.parse(ROOT / 'addon.xml').getroot()
        self.assertEqual([n.attrib for n in before.findall('requires/import')],
                         [n.attrib for n in after.findall('requires/import')])
        self.assertEqual(ET.tostring(before.find('requires')), ET.tostring(after.find('requires')))
        for old, new in zip(before.findall('extension'), after.findall('extension')):
            self.assertEqual(old.attrib, new.attrib)
            for child in old:
                if child.tag not in ('summary', 'news', 'assets'):
                    self.assertEqual(ET.tostring(child), ET.tostring(new.find(child.tag)))
        news = after.findtext("extension[@point='xbmc.addon.metadata']/news")
        self.assertTrue(news.startswith('0.1.1 Beta: artwork-only successor; runtime unchanged.'))
        self.assertNotIn('candidate', news.lower())
        self.assertNotIn('not published', news.lower())

    def test_image_contract_negative_controls(self):
        valid = (ROOT / 'icon.png').read_bytes()
        for mode, size in (('RGBA', (512, 512)), ('RGB', (64, 64))):
            output = BytesIO()
            Image.new(mode, size).save(output, format='PNG')
            with self.assertRaises(AssertionError):
                validate_image(output.getvalue(), 'PNG', (512, 512))
        with self.assertRaises(AssertionError):
            validate_image(valid, 'JPEG', (512, 512))
        print('Asset negative controls rejected: alpha mode, wrong dimensions, wrong encoding')


if __name__ == '__main__':
    unittest.main(verbosity=2)
