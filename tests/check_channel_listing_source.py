"""Actual per-channel listing methods, existing SQLite fixture; no Kodi/profile I/O.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import sqlite3
from types import SimpleNamespace
import unittest

import check_program_search_window as fixture


NOW, DELTA = fixture.NOW, fixture.DELTA
METHODS = ('_getChannelListing', '_getCatchupListing')


class ChannelListingSource(unittest.TestCase):
    def setUp(self):
        self.case = fixture.ProgramSearchWindow()
        self.addCleanup(self.case.doCleanups)
        self.case.setUp()  # Actual Database timestamp adapters/converters, frozen clock.
        self.case.settings['catchup.hours'] = '6'
        self.case.conn.execute('CREATE UNIQUE INDEX event_identity ON programs(channel,start_date,end_date)')
        self.case.conn.execute('CREATE INDEX program_list_idx ON programs(source,channel,start_date,end_date)')
        env = dict(Program=self.case.Program, datetime=SimpleNamespace(
            datetime=SimpleNamespace(now=lambda: NOW), timedelta=DELTA),
            ADDON=SimpleNamespace(getSetting=lambda key: self.case.settings.get(key, '')))
        self.Listings = fixture.extract('source.py', 'Database', env, set(METHODS))
        self.channels = {c.id: c for c in self.case.db._getChannelList(True)}

    def rows(self, method, channel='a'):
        rows = getattr(self.Listings, method)(self.case.db, self.channels[channel])
        self.assertIsInstance(rows, list, 'SQL failure must not pass as empty results')
        self.assertTrue(all(p.channel is self.channels[channel] for p in rows))
        return rows

    def test_source_channel_isolation_metadata_and_real_uniqueness(self):
        title = 'Café — O\'Brien, "日本語" 📺'
        self.case.add('active-a', title=title)
        self.case.add('active-b', title=title, channel='b')
        # Real schema uniqueness omits source: an identical end would be invalid.
        with self.assertRaises(sqlite3.IntegrityError):
            self.case.add('invalid-duplicate', source='other')
        self.case.add('other-source', end=NOW + DELTA(minutes=31), source='other')
        stored = self.case.conn.execute('SELECT start_date, typeof(start_date) FROM programs').fetchone()
        self.assertEqual(stored[0], NOW)
        self.assertIn(stored[1], ('integer', 'real'))
        for method in METHODS:
            for channel in ('a', 'b'):
                with self.subTest(method=method, channel=channel):
                    rows = self.rows(method, channel)
                    expected = self.case.Program(
                        self.channels[channel], title, 'active-' + channel, NOW,
                        NOW + DELTA(minutes=30), 'Synopsis', 'Drama,Fixture',
                        'large.png', 'small.png', season='2', episode='3',
                        is_new='New', is_movie='', language='ja')
                    self.assertEqual([vars(p) for p in rows], [vars(expected)])

    def test_same_source_sequence_survives_other_source_insertion(self):
        for label, hours in (('later', 2), ('now', 0), ('next', 1)):
            self.case.add(label, NOW + DELTA(hours=hours))
        control = {method: [vars(p) for p in self.rows(method)] for method in METHODS}
        self.case.add('other-source', end=NOW + DELTA(minutes=31), source='other')
        for method in METHODS:
            with self.subTest(method=method):
                self.assertEqual([vars(p) for p in self.rows(method)], control[method])

    def test_strict_overlap_boundaries_not_search_containment(self):
        for label, start, end in (
                ('ended', NOW - DELTA(hours=1), NOW),
                ('ending-inside', NOW - DELTA(days=2), NOW + DELTA(seconds=1)),
                ('six-hour-edge', NOW + DELTA(hours=6), NOW + DELTA(hours=7)),
                ('six-hour-inside', NOW + DELTA(hours=6, seconds=-1), NOW + DELTA(hours=7)),
                ('day-edge', NOW + DELTA(days=1), NOW + DELTA(days=1, hours=1)),
                ('spanning', NOW - DELTA(days=2), NOW + DELTA(days=3))):
            self.case.add(label, start, end)
        expected = {'_getChannelListing': ['ending-inside', 'six-hour-edge', 'six-hour-inside', 'spanning'],
                    '_getCatchupListing': ['ending-inside', 'six-hour-inside', 'spanning']}
        for method in METHODS:
            with self.subTest(method=method):
                self.assertEqual(sorted(p.sub_title for p in self.rows(method)), expected[method])

    def test_listing_days_and_catchup_hours_remain_independent(self):
        self.case.settings.update({'listing.days': '2', 'catchup.hours': '3'})
        for label, hours in (('two-hours', 2), ('four-hours', 4), ('next-day', 36), ('too-far', 72)):
            self.case.add(label, NOW + DELTA(hours=hours))
        self.assertEqual(sorted(p.sub_title for p in self.rows('_getChannelListing')),
                         ['four-hours', 'next-day', 'two-hours'])
        self.assertEqual([p.sub_title for p in self.rows('_getCatchupListing')], ['two-hours'])

    def test_empty_channel_and_no_overlapping_programmes(self):
        self.case.add('expired', NOW - DELTA(hours=2), NOW - DELTA(hours=1))
        for method in METHODS:
            for channel in ('a', 'b'):
                with self.subTest(method=method, channel=channel):
                    self.assertEqual(self.rows(method, channel), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
