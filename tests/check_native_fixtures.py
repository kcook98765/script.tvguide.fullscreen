"""Bounded data/loader checks, NOT native acceptance or a Kodi emulator.

Execute only AST-extracted loader methods/data classes with in-memory I/O
captures. Never import the add-on, Kodi modules or Kodistubs on the host.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import ast
import datetime
import hashlib
import io
from pathlib import Path
import re
import runpy
from types import SimpleNamespace
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
GEN = runpy.run_path(str(ROOT / 'tools/native_fixtures.py'))
DATA = ROOT / 'resources/fixtures/native'


def extract(path, class_name, methods=None):
    node = next(n for n in ast.parse((ROOT / path).read_text()).body
                if isinstance(n, ast.ClassDef) and n.name == class_name)
    if methods is not None:
        node.bases = []
        node.body = [n for n in node.body if isinstance(n, ast.FunctionDef) and n.name in methods]
        assert {n.name for n in node.body} == set(methods)
    return node


class MemoryFile:
    def __init__(self, content=b''):
        self.content = content
        self.writes = []

    def read(self):
        return self.content.decode('utf-8')

    def readBytes(self):
        return self.content

    def write(self, value):
        self.writes.append(value)

    def close(self):
        pass


class Fixtures(unittest.TestCase):
    def setUp(self):
        self.settings = {'thelogodb': '0', 'xmltv.date': 'true',
                         'mapping.m3u.enabled': 'true', 'mapping.m3u.type': '0',
                         'mapping.m3u.file': 'fixture:m3u'}
        self.files = {
            'special://profile/addon_data/script.tvguide.fullscreen/channel_id_shortcut.ini': MemoryFile(),
            'special://profile/addon_data/script.tvguide.fullscreen/category_count.ini': MemoryFile(),
            'special://profile/addon_data/script.tvguide.fullscreen/categories.ini': MemoryFile(),
            'fixture:m3u': MemoryFile((DATA / 'mapping.m3u').read_bytes())}
        # Unexpected I/O fails closed; no VFS, network, profile or DB is accessed.
        env = {'datetime': datetime, 're': re,
               'time': SimpleNamespace(daylight=0, timezone=0, altzone=0),
               'ADDON': SimpleNamespace(getSetting=lambda key: self.settings.get(key, '')),
               'xbmcvfs': SimpleNamespace(File=lambda path, *args: self.files[path])}
        nodes = [extract('utils.py', name) for name in ['Channel', 'Program']]
        nodes += [extract('source.py', 'XMLTVSource', ['parseXMLTVDate', 'parseXMLTV']),
                  extract('gui.py', 'TVGuide', ['loadChannelMappings'])]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<extracted real loaders>', 'exec'), env)
        self.env = env
        self.source = env['XMLTVSource']()
        env['XMLTVSource'].LOGO_SOURCE_FOLDER = 1
        self.source.logoSource = 0

    def load(self, offset=0):
        stream = io.BytesIO((DATA / 'guide.xml').read_bytes())
        return list(self.source.parseXMLTV(ET.iterparse(stream, events=('start', 'end')),
                                          stream, len(stream.getvalue()), '', None, offset))

    def test_deterministic_payload_and_clock(self):
        reference = GEN['utc'](GEN['REFERENCE'])
        for name, content in GEN['payloads'](reference).items():
            self.assertEqual((DATA / name).read_bytes(), content)
        target = GEN['utc']('2027-02-03T09:40:00Z')
        offset = GEN['offset'](reference, target)
        rows = self.load(offset)
        programmes = rows[3:]
        now = target.replace(tzinfo=None)
        current = [p for p in programmes if p.startDate <= now < p.endDate]
        self.assertEqual(len(current), 3)
        self.assertEqual({p.title for p in current}, {'He said "Hello"', 'He said "Hello" (1999)'})
        self.assertTrue(all(p.endDate - now == datetime.timedelta(minutes=5) for p in current))
        # Same UTC reference, non-UTC local display: offset is NOT a timezone adjustment.
        self.env['time'].timezone = -7200
        local = self.load(offset)[4]
        self.assertEqual(local.startDate, now + datetime.timedelta(hours=2, minutes=-10))
        with self.assertRaises(ValueError):
            GEN['utc']('2026-11-19T12:00:01Z')
        with self.assertRaises(ValueError):
            GEN['utc']('2026-11-19T12:00:00')

    def test_real_xmltv_metadata_and_adjacency(self):
        rows = self.load()
        channels, programmes = rows[:3], rows[3:]
        self.assertEqual([c.id for c in channels], [cid for cid, _ in GEN['CHANNELS']])
        self.assertEqual(len(programmes), 24)
        self.assertTrue(all(c.streamUrl is None for c in channels))  # M3U must supply playback.
        for cid, _ in GEN['CHANNELS']:
            slots = [p for p in programmes if p.channel == cid]
            self.assertEqual(len(slots), 8)
            self.assertTrue(all(a.endDate == b.startDate for a, b in zip(slots, slots[1:])))
            self.assertTrue(all(p.endDate - p.startDate == datetime.timedelta(minutes=15) for p in slots))
        self.assertEqual([(p.season, p.episode) for p in programmes[:8]], [(1, n) for n in range(1, 9)])
        self.assertTrue(all(p.is_new == 'New' and not p.is_movie for p in programmes[:8]))
        self.assertTrue(all(p.is_movie == 'Movie' for p in programmes[8:16]))
        self.assertEqual([p.title for p in programmes[16:]], GEN['TITLES'])
        self.assertEqual(programmes[0].categories, 'Series,Fixture')
        self.assertEqual(programmes[0].sub_title, 'Synthetic slot 0')
        self.assertIn('Café, 日本語 & benign punctuation.', programmes[0].description)

    def test_real_m3u_mapping_matches_xmltv(self):
        channels = self.load()[:3]
        captured = []
        saved = []
        db = SimpleNamespace(getChannelList=lambda **kw: channels,
                             saveChannelListBlock=lambda values: saved.append(list(values)),
                             setCustomStreamUrls=lambda values: captured.extend(values))
        guide = self.env['TVGuide']()
        guide.database = db
        guide.loadChannelMappings()
        self.assertEqual(captured, [(c.id, GEN['MEDIA']) for c in channels])
        self.assertEqual([c.id for c in saved[0]], [c.id for c in channels])
        self.assertEqual(guide.categories, ['Fixture'])
        # Negative control: prove IDs are actually used, not a test-side name join.
        self.files['fixture:m3u'].content = self.files['fixture:m3u'].content.replace(b'fixture.episode', b'wrong.id')
        self.env['utils'] = SimpleNamespace(Channel=self.env['Channel'])
        guide.loadChannelMappings()
        self.assertEqual(captured[3][0], 'wrong.id')
        self.assertEqual(saved[-1][-1].id, 'wrong.id')

    def test_finite_video_identity(self):
        clip = (DATA / 'clip.mp4').read_bytes()
        self.assertEqual(len(clip), 439183)
        self.assertEqual(clip[4:8], b'ftyp')
        self.assertEqual(hashlib.sha256(clip).hexdigest(),
                         '52807a551971e085aac02a19a4c2ab531a972ea13abfd73f8769ad9e11037917')
        self.assertNotEqual(hashlib.sha256(clip[:-1]).digest(), hashlib.sha256(clip).digest())


if __name__ == '__main__':
    unittest.main(verbosity=2)
