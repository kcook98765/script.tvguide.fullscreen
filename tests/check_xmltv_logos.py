"""Actual XMLTV channel parser with inert logo/VFS fakes; no Kodi or network.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import ast
import copy
import io
from itertools import product
import os
from pathlib import Path
import re
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PROFILE = 'special://profile/addon_data/script.tvguide.fullscreen/'
ICON = 'https://example.invalid/xmltv.png'
LOOKUP = 'https://example.invalid/thelogodb.png'
URL_LOGO = 'https://example.invalid/logos/Fixture Channel.png'
VALUES = ('true', 'false', '')


class XMLTVLogos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse((ROOT / 'source.py').read_text(encoding='utf-8'))
        cls.channel = next(n for n in ast.parse((ROOT / 'utils.py').read_text()).body
                           if isinstance(n, ast.ClassDef) and n.name == 'Channel')

    def load(self, value, icon=ICON, logo_source=0, files=(), mode='0', keep='false',
             truthiness_control=False, logo_base='https://example.invalid/logos/'):
        settings = {'xmltv.logos': value, 'thelogodb': mode, 'logos.keep': keep}
        lookup = Mock(return_value=LOOKUP)
        def vfs_file(path, mode):
            if (path, mode) == (PROFILE + 'channel_id_shortcut.ini', 'rb'):
                return io.StringIO('')
            self.assertEqual((path, mode), (PROFILE + 'category_count.ini', 'wb'))
            return io.BytesIO()
        folder = {0: '', 1: 'fixture-logos', 2: logo_base}[logo_source]
        listdir = Mock(return_value=([], files))
        env = dict(os=os, re=re, Channel=None, getLogo=lookup,
                   ADDON=SimpleNamespace(getSetting=lambda key: settings.get(key, '')),
                   xbmcvfs=SimpleNamespace(File=vfs_file, listdir=listdir))
        parser = copy.deepcopy(next(n for n in self.tree.body
                                    if isinstance(n, ast.ClassDef) and n.name == 'XMLTVSource'))
        parser.bases = []
        parser.body = [n for n in parser.body
                       if isinstance(n, ast.FunctionDef) and n.name == 'parseXMLTV']
        self.assertEqual(len(parser.body), 1)
        if truthiness_control:
            # Mutate ONLY an in-memory AST: restore the old raw-string condition.
            targets = [n for n in ast.walk(parser) if isinstance(n, ast.If)
                       and isinstance(n.test, ast.BoolOp)
                       and any(isinstance(c, ast.Constant) and c.value == 'xmltv.logos'
                               for c in ast.walk(n.test))]
            self.assertEqual(len(targets), 1)
            condition = targets[0].test
            setting_call = next(n for n in ast.walk(condition) if isinstance(n, ast.Call))
            condition.values[-1] = copy.deepcopy(setting_call)
        exec(compile(ast.fix_missing_locations(ast.Module(
            body=[copy.deepcopy(self.channel), parser], type_ignores=[])),
            '<actual XMLTV channel parser>', 'exec'), env)
        source = env['XMLTVSource']()
        env['XMLTVSource'].LOGO_SOURCE_FOLDER = 1
        env['XMLTVSource'].LOGO_SOURCE_URL = 2
        source.logoSource = logo_source
        root = ET.Element('tv')
        channel = ET.SubElement(root, 'channel', id='fixture.channel')
        ET.SubElement(channel, 'display-name').text = 'Fixture Channel'
        ET.SubElement(channel, 'stream').text = 'fixture://stream'
        if icon is not None:
            ET.SubElement(channel, 'icon', **({} if icon == 'missing-src' else {'src': icon}))
        data = ET.tostring(root)
        stream = io.BytesIO(data)
        rows = list(source.parseXMLTV(ET.iterparse(stream, events=('start', 'end')),
                                      stream, len(data), folder, None, 0))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual((row.id, row.title, row.streamUrl, row.visible),
                         ('fixture.channel', 'Fixture Channel', 'fixture://stream', True))
        self.assertTrue(stream.closed)
        if logo_source == 1:
            listdir.assert_called_once_with(folder)
        else:
            listdir.assert_not_called()
        return row.logo, lookup

    def test_declared_bool_and_icon_presence(self):
        setting = ET.parse(ROOT / 'resources/settings.xml').find(".//setting[@id='xmltv.logos']")
        self.assertEqual((setting.get('type'), setting.get('default')), ('bool', 'false'))
        for value, icon in product(VALUES, (ICON, None, '', 'missing-src')):
            with self.subTest(value=value, icon=icon):
                logo, lookup = self.load(value, icon)
                self.assertEqual(logo, ICON if value == 'true' and icon == ICON else '')
                lookup.assert_not_called()

    def test_explicit_folder_precedence_and_missing_match(self):
        for value, matched in product(VALUES, (False, True)):
            with self.subTest(value=value, matched=matched):
                logo, lookup = self.load(value, logo_source=1, files=[
                    'Fixture Channel.png' if matched else 'Unrelated.png'])
                expected = os.path.join('fixture-logos', 'Fixture Channel.png') if matched else (
                    ICON if value == 'true' else '')
                self.assertEqual(logo, expected)
                lookup.assert_not_called()

    def test_explicit_url_overrides_xmltv_and_preserves_path_spelling(self):
        settings = ET.parse(ROOT / 'resources/settings.xml')
        self.assertEqual(settings.find(".//setting[@id='logos.source']").get('values'),
                         'None|Folder|Url')
        self.assertEqual(settings.find(".//setting[@id='logos.url']").get('type'), 'text')
        for value, icon, base in product(VALUES, (ICON, None), (
                'https://example.invalid/logos', 'https://example.invalid/logos/', '')):
            with self.subTest(value=value, icon=icon, base=base):
                logo, lookup = self.load(value, icon, logo_source=2, logo_base=base)
                expected = URL_LOGO if base else (ICON if value == 'true' and icon else '')
                # Keep mixed case and the literal space; no new encoding policy.
                self.assertEqual(logo, expected)
                lookup.assert_not_called()

    def test_url_source_thelogodb_precedence(self):
        for icon, mode, keep in product((ICON, None), ('0', '1', '2'), ('false', 'true')):
            with self.subTest(icon=icon, mode=mode, keep=keep):
                logo, lookup = self.load('true', icon, logo_source=2, mode=mode, keep=keep)
                # An explicit URL is present even without XMLTV icons: If Missing
                # must not look up. Always still bypasses both sources; keep wins.
                expected = URL_LOGO if mode != '2' else (LOOKUP if keep == 'false' else '')
                self.assertEqual(logo, expected)
                if mode == '2' and keep == 'false':
                    lookup.assert_called_once_with('Fixture Channel', False, False)
                else:
                    lookup.assert_not_called()

    def test_thelogodb_opt_in_and_keep_mapping(self):
        for value, icon, mode, keep in product(VALUES, (ICON, None), ('0', '1', '2'),
                                               ('false', 'true')):
            with self.subTest(value=value, icon=icon, mode=mode, keep=keep):
                logo, lookup = self.load(value, icon, mode=mode, keep=keep)
                expected = ICON if value == 'true' and icon == ICON and mode != '2' else ''
                should_lookup = keep == 'false' and (mode == '2' or (mode == '1' and not expected))
                self.assertEqual(logo, LOOKUP if should_lookup else expected)
                if should_lookup:
                    lookup.assert_called_once_with('Fixture Channel', False, False)
                else:
                    lookup.assert_not_called()

    def test_negative_control_raw_false_string_uses_icon(self):
        logo, lookup = self.load('false', truthiness_control=True)
        self.assertEqual(logo, ICON)
        self.assertNotEqual(logo, '', 'Negative control failed to expose truthy false')
        lookup.assert_not_called()
        print('DETECTED in-memory raw-string negative control: false incorrectly selects XMLTV icon')


if __name__ == '__main__':
    unittest.main(verbosity=2)
