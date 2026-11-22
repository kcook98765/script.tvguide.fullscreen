"""Absent XMLTV display-name regression using the existing real-parser adapter.

Only inert in-memory VFS/settings; no Kodi, network, profile or database access.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import ast
import datetime
import io
import os
from unittest.mock import Mock, patch
import unittest
import xml.etree.ElementTree as ET

import check_xmltv_programme_rows as programmes
import check_xmltv_source_offsets as offsets


ICON = 'https://example.invalid/feed.png'
URL = 'https://example.invalid/logos'
FOLDER = 'fixture-logos'
FALLBACK = ('                    title = elem.findtext("display-name")\n'
            '                    if title is None:\n'
            '                        title = cid\n'
            '                    title = title.replace("=","-")')
ORIGINAL = '                    title = elem.findtext("display-name").replace("=","-")'


def payload(slot, name, raw_id='stable'):
    root = ET.Element('tv')
    for cid, title in ((slot, slot), (raw_id, name), (slot + '-tail', 'Tail')):
        channel = ET.SubElement(root, 'channel', id=cid, visible='0')
        if title is not None:
            ET.SubElement(channel, 'display-name').text = title
        ET.SubElement(channel, 'icon', src=ICON)
        ET.SubElement(channel, 'stream').text = 'fixture://stream'
        if cid != raw_id:
            root.append(programmes.programme(cid, 'valid'))
    # The fallback channel's programme follows another valid channel/programme.
    root.append(programmes.programme(raw_id, slot + ' trailing'))
    return ET.tostring(root)


def parser(payloads, logo_source=0, xmltv_logos=False, matched=True,
           shortcut=False, raw_id='stable', original=False):
    def build():
        return programmes.parser(payloads)

    if original:
        # All-valid differential oracle: reverse only this correction in memory.
        text = (offsets.ROOT / 'source.py').read_text(encoding='utf-8')
        assert text.count(FALLBACK) + text.count(ORIGINAL) == 1
        tree = ast.parse(text.replace(FALLBACK, ORIGINAL), filename='source.py')
        source_tree = offsets.source_tree
        with patch.object(offsets, 'source_tree', side_effect=lambda path: (
                tree if path == 'source.py' else source_tree(path))):
            source, env, vfs = build()
    else:
        source, env, vfs = build()
    normalized = raw_id.replace("'", '').replace('=', '-')
    old_setting = env['ADDON'].getSetting
    env['ADDON'].getSetting = lambda key: (
        str(xmltv_logos).lower() if key == 'xmltv.logos' else old_setting(key))
    env['os'] = os
    env['XMLTVSource'].LOGO_SOURCE_URL = 2
    source.logoSource = logo_source
    source.logoFolder = {0: '', 1: FOLDER, 2: URL}[logo_source]
    vfs.listdir = Mock(return_value=([], [normalized + '.png'] if matched else []))
    if shortcut:
        original_file = vfs.File
        vfs.File = lambda path, mode: (
            io.StringIO(normalized + '=routed-stable\n')
            if path == offsets.PROFILE + 'channel_id_shortcut.ini'
            else original_file(path, mode))
    return source, env, vfs


class ChannelNames(unittest.TestCase):
    maxDiff = None

    def check_rows(self, rows, env, names, raw_id='stable', shortcut=False,
                   logo_source=0, xmltv_logos=False, matched=True):
        normalized = raw_id.replace("'", '').replace('=', '-')
        expected = []
        for slot, minutes in zip(offsets.SLOTS, programmes.OFFSETS):
            name = names[slot]
            fallback_title = normalized if name is None else name.replace('=', '-')
            cid = 'routed-stable' if shortcut else normalized
            for channel_id, title in ((slot, slot), (cid, fallback_title),
                                      (slot + '-tail', 'Tail')):
                logo = ICON if xmltv_logos else ''
                if logo_source == 2:
                    logo = URL + '/' + title + '.png'
                elif logo_source == 1 and matched and title == normalized:
                    logo = os.path.join(FOLDER, normalized + '.png')
                expected.append(vars(env['Channel'](
                    channel_id, title, '', logo, 'fixture://stream', False)))
                if channel_id != cid:
                    expected.append(self.programme(env, channel_id,
                                                   channel_id + ' valid', minutes))
            expected.append(self.programme(env, cid, raw_id + ' ' + slot + ' trailing', minutes))
        self.assertEqual([vars(row) for row in rows], expected)

    def programme(self, env, cid, title, minutes):
        start = offsets.START + datetime.timedelta(minutes=minutes)
        return vars(env['Program'](
            cid, title, 'Part', start, start + datetime.timedelta(minutes=30),
            'Synthetic synopsis', 'Drama,Fixture', season=2, episode=3,
            is_new='New', is_movie=None, language='fr'))

    def test_absent_name_retains_channel_and_trailing_rows_in_each_slot(self):
        for missing_slot in offsets.SLOTS:
            with self.subTest(slot=missing_slot):
                names = {slot: None if slot == missing_slot else 'Normal'
                         for slot in offsets.SLOTS}
                source, env, vfs = parser({slot: payload(slot, names[slot])
                                           for slot in offsets.SLOTS})
                self.check_rows(list(source.getDataFromExternal(None, [])), env, names)
                self.assertTrue(all(f.closed for f in vfs.outputs))
                self.assertEqual(len(vfs.outputs), 3)

    def test_present_names_equal_original_output(self):
        for name in ('', '   ', 'Normal Name', "Télé=日本 ' HD"):
            with self.subTest(name=name):
                names = dict.fromkeys(offsets.SLOTS, name)
                data = {slot: payload(slot, name) for slot in offsets.SLOTS}
                source, env, _ = parser(data)
                rows = list(source.getDataFromExternal(None, []))
                self.check_rows(rows, env, names)
                original, _, _ = parser(data, original=True)
                self.assertEqual([vars(row) for row in rows],
                                 [vars(row) for row in original.getDataFromExternal(None, [])])

    def test_normalized_fallback_precedes_shortcut_and_logo_selection(self):
        for raw_id in ('stable', "st=ab'le"):
            for shortcut in (False, True):
                for logo_source, xmltv_logos, matched in (
                        (0, False, False), (0, True, False),
                        (2, False, False), (2, True, False),
                        (1, False, True), (1, True, True),
                        (1, False, False), (1, True, False)):
                    with self.subTest(raw_id=raw_id, shortcut=shortcut,
                                      logo_source=logo_source, xmltv_logos=xmltv_logos,
                                      matched=matched):
                        names = dict.fromkeys(offsets.SLOTS, None)
                        source, env, _ = parser(
                            {slot: payload(slot, None, raw_id) for slot in offsets.SLOTS},
                            logo_source, xmltv_logos, matched, shortcut, raw_id)
                        self.check_rows(list(source.getDataFromExternal(None, [])), env,
                                        names, raw_id, shortcut, logo_source,
                                        xmltv_logos, matched)

    def test_cancellation_still_propagates_after_fallback_rows(self):
        root = ET.Element('tv')
        for i in range(500):
            ET.SubElement(root, 'channel', id='stable-' + str(i))
        source, env, _ = parser({'primary': ET.tostring(root)})
        error = type('Canceled', (Exception,), {})
        env['SourceUpdateCanceledException'] = error
        progress = Mock(return_value=False)
        with self.assertRaises(error):
            list(source.getDataFromExternal(None, [], progress))
        progress.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
