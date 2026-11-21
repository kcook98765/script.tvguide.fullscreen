"""Small real-parser row regressions using the existing inert XMLTV VFS adapter.

No Kodi imports, network, provider, profile, database or entry-point execution.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import datetime
from types import SimpleNamespace
from unittest.mock import Mock
import unittest
import xml.etree.ElementTree as ET

import check_xmltv_source_offsets as offsets


OFFSETS = (0, -45, 90)


def programme(slot, label, field=None, value=None):
    attrs = {'channel': slot, 'start': '20261120140000 +0200',
             'stop': '20261120073000 -0500'}
    if field:
        if value is None:
            del attrs[field]
        else:
            attrs[field] = value
    node = ET.Element('programme', attrs)
    for tag, text in (('title', slot + ' ' + label), ('sub-title', 'Part'),
                      ('desc', 'Synthetic synopsis'), ('date', '2026'),
                      ('category', 'Drama'), ('category', 'Fixture'),
                      ('episode-num', '1.2.')):
        child = ET.SubElement(node, tag)
        child.text = text
        if tag == 'title':
            child.set('lang', 'fr')
    ET.SubElement(node, 'new')
    return node


def payload(slot, bad_rows=()):
    root = ET.Element('tv')
    channel = ET.SubElement(root, 'channel', id=slot)
    ET.SubElement(channel, 'display-name').text = slot
    root.append(programme(slot, 'leading'))
    for field, value in bad_rows:
        root.append(programme(slot, 'unusable', field, value))
    root.append(programme(slot, 'trailing'))
    return ET.tostring(root)


def parser(payloads):
    source, env, vfs = offsets.SourceOffsets().source(
        (True, True), (True, True, True), OFFSETS)
    vfs.files.update(payloads)
    return source, env, vfs


class ProgrammeRows(unittest.TestCase):
    maxDiff = None

    def check_rows(self, rows, env, shortcuts=False):
        expected = []
        for slot, minutes in zip(offsets.SLOTS, OFFSETS):
            cid = 'routed-' + slot if shortcuts else slot
            expected.append(vars(env['Channel'](cid, slot, '', '', None, True)))
            for label in ('leading', 'trailing'):
                start = offsets.START + datetime.timedelta(minutes=minutes)
                expected.append(vars(env['Program'](
                    cid, slot + ' ' + label, 'Part', start,
                    start + datetime.timedelta(minutes=30), 'Synthetic synopsis',
                    'Drama,Fixture', season=2, episode=3, is_new='New',
                    is_movie=None, language='fr')))
        self.assertEqual([vars(row) for row in rows], expected)

    def test_required_identity_and_times_in_each_source(self):
        cases = [(field, value) for field in ('channel', 'start', 'stop')
                 for value in (None, '', '   ')]
        cases += [(field, value) for field in ('start', 'stop')
                  for value in ('bogus', '20260230120000 +0000',
                                '20261120120000 +xx00',
                                '20261120120000 +0000 extra')]
        for slot in offsets.SLOTS:
            for field, value in cases:
                with self.subTest(slot=slot, field=field, value=value):
                    source, env, vfs = parser({
                        name: payload(name, [(field, value)] if name == slot else [])
                        for name in offsets.SLOTS})
                    rows = list(source.getDataFromExternal(None, []))
                    self.check_rows(rows, env)
                    self.assertTrue(all(f.closed for f in vfs.outputs))
        # Several unusable records together must not leave stale row metadata.
        source, env, _ = parser({slot: payload(slot, cases) for slot in offsets.SLOTS})
        self.check_rows(list(source.getDataFromExternal(None, [])), env)

    def test_valid_metadata_order_offsets_and_channel_shortcuts(self):
        for shortcuts in (False, True):
            source, env, vfs = parser({slot: payload(slot) for slot in offsets.SLOTS})
            if shortcuts:
                # Kodi File.read() is text; readBytes() is used for XML payloads.
                original_file = vfs.File
                shortcut_text = ''.join(slot + '=routed-' + slot + '\n'
                                        for slot in offsets.SLOTS)
                vfs.File = lambda path, mode: (
                    SimpleNamespace(read=lambda: shortcut_text)
                    if path == offsets.PROFILE + 'channel_id_shortcut.ini'
                    else original_file(path, mode))
            self.check_rows(list(source.getDataFromExternal(None, [])), env, shortcuts)

    def test_malformed_xml_still_propagates(self):
        for slot in offsets.SLOTS:
            source, _, _ = parser({slot: payload(slot)[:-5] + b'<broken></tv>'})
            with self.subTest(slot=slot), self.assertRaises(ET.ParseError):
                list(source.getDataFromExternal(None, []))

    def test_unrelated_errors_are_not_row_skips(self):
        source, env, _ = parser({})
        # The protected boundary is date conversion only, not metadata/model work.
        for error in (ValueError, IndexError, RuntimeError):
            with self.subTest(error=error):
                env['Program'] = Mock(side_effect=error('synthetic model failure'))
                with self.assertRaises(error):
                    list(source.getDataFromExternal(None, []))
        source, _, _ = parser({})
        source.parseXMLTVDate = Mock(side_effect=RuntimeError('synthetic parser failure'))
        with self.assertRaises(RuntimeError):
            list(source.getDataFromExternal(None, []))


if __name__ == '__main__':
    unittest.main(verbosity=2)
