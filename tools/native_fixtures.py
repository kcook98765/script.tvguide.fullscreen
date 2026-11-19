"""Developer-only deterministic data generator; never imported by the add-on.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import argparse
import datetime as dt
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'resources' / 'fixtures' / 'native'
REFERENCE = '2026-11-19T12:00:00Z'
MEDIA = 'special://home/addons/script.tvguide.fullscreen/resources/fixtures/native/clip.mp4'
CHANNELS = [('fixture.episode', 'Fixture Episodes'),
            ('fixture.movie', 'Fixture Movies'),
            ('fixture.unicode', 'Fixture Café 日本語')]
TITLES = ["Doctor's diary", 'He said "Hello"', 'News, Weather & Sport',
          'Film (1999)', 'Café — 日本語 📺', 'Quiet shapes: part 6',
          'Evening & morning', 'The final square']


def utc(value):
    """Require an explicit UTC minute; never consult the host clock/timezone."""
    result = dt.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)
    if result.second:
        raise ValueError('use a whole UTC minute (seconds 00)')
    return result


def offset(reference, target):
    # Put target ten minutes into slot 1: next boundary is five minutes away.
    return int((target - reference).total_seconds() // 60) - 10


def payloads(reference):
    tv = ET.Element('tv', {'generator-info-name': 'TVGF deterministic native fixtures'})
    for cid, name in CHANNELS:
        channel = ET.SubElement(tv, 'channel', {'id': cid})
        ET.SubElement(channel, 'display-name').text = name
    for index, (cid, _) in enumerate(CHANNELS):
        for slot, title in enumerate(TITLES):
            start = reference + dt.timedelta(minutes=15 * (slot - 1))
            programme = ET.SubElement(tv, 'programme', {
                'start': start.strftime('%Y%m%d%H%M%S +0000'),
                'stop': (start + dt.timedelta(minutes=15)).strftime('%Y%m%d%H%M%S +0000'),
                'channel': cid})
            ET.SubElement(programme, 'title', {'lang': 'en'}).text = title
            ET.SubElement(programme, 'sub-title').text = 'Synthetic slot %d' % slot
            ET.SubElement(programme, 'desc').text = (
                'Original fictional guide data; no broadcast or third-party media. '
                'Channel %d, slot %d. Café, 日本語 & benign punctuation.' % (index + 1, slot))
            if index == 1:
                ET.SubElement(programme, 'date').text = '1999'
            ET.SubElement(programme, 'category').text = ['Series', 'Movie', 'Culture'][index]
            ET.SubElement(programme, 'category').text = 'Fixture'
            if index == 0:
                ET.SubElement(programme, 'episode-num', {'system': 'xmltv_ns'}).text = '0.%d.' % slot
                ET.SubElement(programme, 'new')
    ET.indent(tv, space='  ')
    xml = ET.tostring(tv, encoding='utf-8', xml_declaration=True) + b'\n'
    m3u = '#EXTM3U\n' + ''.join(
        '#EXTINF:-1 tvg-id="%s" group-title="Fixture",%s\n%s\n' % (cid, name, MEDIA)
        for cid, name in CHANNELS)
    return {'guide.xml': xml, 'mapping.m3u': m3u.encode('utf-8')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', default=REFERENCE, help='UTC base, YYYY-MM-DDTHH:MM:00Z')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check', action='store_true', help='compare generated text; write nothing')
    modes.add_argument('--align', metavar='UTC', help='print xmltv.offset for target UTC minute; write nothing')
    args = parser.parse_args()
    reference = utc(args.reference)
    if args.align:
        print(offset(reference, utc(args.align)))
        return
    for name, content in payloads(reference).items():
        path = DATA / name
        if args.check:
            if path.read_bytes() != content:
                raise SystemExit('fixture differs: ' + name)
            print('PASS deterministic bytes:', name)
        else:
            # Only two fixed source-data paths; no profile/settings/media writes.
            DATA.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            print('generated:', path.relative_to(ROOT))


if __name__ == '__main__':
    main()
