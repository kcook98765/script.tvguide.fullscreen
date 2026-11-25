"""Real XMLTV routing/parser regression; only synthetic in-memory VFS/settings.

No add-on imports, Kodi/stub execution, network, host profile or database access.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import ast
import copy
import datetime
from functools import lru_cache
import io
from itertools import chain, product
from pathlib import Path
import re
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, call
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'special://profile/addon_data/script.tvguide.fullscreen/'
SLOTS = ('primary', 'secondary', 'tertiary')
# Each source gets zero, negative and positive minutes; all-zero masks the bug.
OFFSETS = ((0, -45, 90), (60, 0, -120), (-90, 150, 0), (0, 0, 0))
START = datetime.datetime(2026, 11, 20, 12)


@lru_cache(maxsize=None)
def source_tree(path):
    return ast.parse((ROOT / path).read_text(encoding='utf-8'), filename=path)


def extract(path, name, methods=None):
    node = copy.deepcopy(next(n for n in source_tree(path).body
                              if isinstance(n, ast.ClassDef) and n.name == name))
    if methods is not None:
        node.bases = []
        node.body = [n for n in node.body
                     if isinstance(n, ast.FunctionDef) and n.name in methods]
        assert {n.name for n in node.body} == set(methods)
    return node


def payload(slot):
    return (f'<tv><channel id="{slot}"><display-name>{slot}</display-name></channel>'
            f'<programme channel="{slot}" start="20261120120000 +0000" '
            f'stop="20261120123000 +0000"><title lang="en">{slot} show</title>'
            '<desc>Deterministic synopsis</desc><category>Fixture</category>'
            '</programme></tv>').encode('utf-8')


class MemoryFile(io.BytesIO):
    def readBytes(self, size=-1):
        return self.read(size)

    def size(self):
        return len(self.getvalue())


class MemoryVFS:
    def __init__(self, present):
        self.files = {slot: payload(slot) for slot, exists in zip(SLOTS, present) if exists}
        self.files[PROFILE + 'channel_id_shortcut.ini'] = b''
        self.opened = []
        self.outputs = []

    def exists(self, path):
        return path in self.files

    def File(self, path, mode):
        self.opened.append((path, mode))
        if mode == 'wb':
            # The real parser writes category counts; retain only inert bytes.
            assert path == PROFILE + 'category_count.ini', path
            result = MemoryFile()
            self.outputs.append(result)
            return result
        assert mode == 'rb', mode
        return MemoryFile(self.files[path])  # Unexpected paths fail closed.


class SourceOffsets(unittest.TestCase):
    maxDiff = None

    def source(self, enabled, present, offsets):
        settings = dict(zip(('xmltv.offset', 'xmltv2.offset', 'xmltv3.offset'),
                            map(str, offsets)))
        settings.update({'xmltv2.enabled': str(enabled[0]).lower(),
                         'xmltv3.enabled': str(enabled[1]).lower(),
                         'update.progress': 'false', 'xmltv.date': 'false',
                         'thelogodb': '0'})
        vfs = MemoryVFS(present)
        env = dict(datetime=datetime, re=re, chain=chain, ElementTree=ET,
                   time=SimpleNamespace(daylight=0, timezone=0, altzone=0),
                   ADDON=SimpleNamespace(getSetting=lambda key: settings.get(key, '')),
                   xbmcvfs=vfs, SourceNotConfiguredException=type('NotConfigured', (Exception,), {}))
        nodes = [extract('utils.py', name) for name in ('Channel', 'Program')]
        nodes += [extract('source.py', 'FileWrapper'),
                  extract('source.py', 'XMLTVSource', {
                      'getDataFromExternal', 'getDataFromExternal2',
                      'parseXMLTVDate', 'parseXMLTV'})]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<real XMLTV methods>', 'exec'), env)
        cls = env['XMLTVSource']
        cls.LOGO_SOURCE_FOLDER = 1
        source = cls()
        source.xmltvFile, source.xmltv2File, source.xmltv3File = SLOTS
        source.logoFolder, source.logoSource = '', 0
        # Observe arguments without replacing the real wrapper/parser execution.
        source.getDataFromExternal2 = Mock(wraps=source.getDataFromExternal2)
        return source, env, vfs

    def check_matrix(self, enabled):
        for present, offsets in product(product((False, True), repeat=3), OFFSETS):
            with self.subTest(enabled=enabled, present=present, offsets=offsets):
                source, env, vfs = self.source(enabled, present, offsets)
                date, channels = START.date(), ['caller channel sentinel']
                progress = Mock(return_value=True)
                if not present[0]:
                    with self.assertRaises(env['SourceNotConfiguredException']):
                        list(source.getDataFromExternal(date, channels, progress))
                    source.getDataFromExternal2.assert_not_called()
                    self.assertEqual(vfs.opened, [])
                    continue

                active = [0] + [i for i in (1, 2) if enabled[i - 1] and present[i]]
                if any(enabled[i - 1] and not present[i] for i in (1, 2)):
                    # #85: silently skipping an enabled missing cache would let
                    # a successful primary import erase that slot's old rows.
                    with self.assertRaises(env['SourceNotConfiguredException']):
                        list(source.getDataFromExternal(date, channels, progress))
                    continue
                rows = list(source.getDataFromExternal(date, channels, progress))
                self.assertEqual(len(rows), 2 * len(active))
                # Preserve primary/secondary/tertiary order, channel identity and
                # unshifted metadata; independently check BOTH timestamp bounds.
                expected = []
                for i in active:
                    slot, delta = SLOTS[i], datetime.timedelta(minutes=offsets[i])
                    expected.extend([
                        ('channel', slot, slot, '', None, True),
                        ('programme', slot, slot + ' show', START + delta,
                         START + datetime.timedelta(minutes=30) + delta,
                         'Deterministic synopsis', 'Fixture', 'en')])
                actual = []
                for row in rows:
                    if isinstance(row, env['Channel']):
                        actual.append(('channel', row.id, row.title, row.logo,
                                       row.streamUrl, row.visible))
                    else:
                        self.assertIsInstance(row, env['Program'])
                        actual.append(('programme', row.channel, row.title,
                                       row.startDate, row.endDate, row.description,
                                       row.categories, row.language))
                self.assertEqual(
                    {'rows': actual, 'calls': source.getDataFromExternal2.call_args_list},
                    {'rows': expected, 'calls': [
                        call(SLOTS[i], date, channels, progress, offsets[i]) for i in active]})
                self.assertEqual([path for path, mode in vfs.opened if path in SLOTS],
                                 [SLOTS[i] for i in active])
                self.assertTrue(all(f.closed for f in vfs.outputs))
                progress.assert_not_called()  # Tiny fixtures never reach 500 rows.
                self.assertEqual(channels, ['caller channel sentinel'])

    def test_primary_only(self):
        self.check_matrix((False, False))

    def test_secondary_enabled(self):
        self.check_matrix((True, False))

    def test_tertiary_enabled(self):
        self.check_matrix((False, True))

    def test_both_optional_enabled(self):
        self.check_matrix((True, True))


if __name__ == '__main__':
    unittest.main(verbosity=2)
