"""Actual search/channel methods and SQLite timestamp codecs, no Kodi/profile I/O.

SPDX-License-Identifier: GPL-2.0-or-later
"""
import datetime
import re
import sqlite3
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from check_channel_search_empty import extract


NOW = datetime.datetime(2026, 11, 20, 12)
DELTA = datetime.timedelta


class ProgramSearchWindow(unittest.TestCase):
    def setUp(self):
        self.settings = {'listing.days': '1', 'listing.hours': '6',
                         'program.search.plot': 'false'}
        clock = SimpleNamespace(datetime=SimpleNamespace(
            now=lambda: NOW, fromtimestamp=datetime.datetime.fromtimestamp), timedelta=DELTA)
        env = dict(datetime=clock, time=time, re=re,
                   ADDON=SimpleNamespace(getSetting=lambda key: self.settings.get(key, '')))
        self.Program = extract('utils.py', 'Program', env)
        self.Channel = extract('utils.py', 'Channel', env)
        Database = extract('source.py', 'Database', env, {
            '_programSearch', '_getChannelList', 'adapt_datetime', 'convert_datetime'})
        # Use production Unix-seconds codecs, not ISO-text substitutes. Restore
        # process-local SQLite registries so the harness has no lasting state.
        for registry in (sqlite3.adapters, sqlite3.converters):
            context = patch.dict(registry)
            context.start()
            self.addCleanup(context.stop)
        sqlite3.register_adapter(datetime.datetime, Database.adapt_datetime)
        sqlite3.register_converter('timestamp', Database.convert_datetime)
        self.conn = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
        self.addCleanup(self.conn.close)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute('''CREATE TABLE channels (
            id TEXT, title TEXT, lineup TEXT, logo TEXT, stream_url TEXT,
            source TEXT, visible BOOLEAN, weight INTEGER)''')
        self.conn.execute('''CREATE TABLE programs (
            channel TEXT, source TEXT, title TEXT, sub_title TEXT,
            start_date TIMESTAMP, end_date TIMESTAMP, description TEXT,
            categories TEXT, image_large TEXT, image_small TEXT, season TEXT,
            episode TEXT, is_new TEXT, is_movie TEXT, language TEXT)''')
        self.db = Database()
        self.db.conn, self.db.source, self.db.category = self.conn, SimpleNamespace(KEY='active'), None
        for channel, source, visible, weight in (
                ('a', 'active', 1, 1), ('b', 'active', 1, 0),
                ('hidden', 'active', 0, 2), ('a', 'other', 1, 0)):
            self.conn.execute('INSERT INTO channels VALUES (?,?,?,?,?,?,?,?)', (
                channel, source + '/' + channel, 'Lineup', 'logo.png',
                'fixture://stream', source, visible, weight))

    def add(self, label, start=NOW, end=None, title='Window match', description='Synopsis',
            channel='a', source='active'):
        self.conn.execute('INSERT INTO programs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
            channel, source, title, label, start, end if end is not None else start + DELTA(minutes=30),
            description, 'Drama,Fixture', 'large.png', 'small.png', '2', '3', 'New', '', 'ja'))

    def labels(self, query='Window', plot='false'):
        self.settings['program.search.plot'] = plot
        result = self.db._programSearch(query)
        self.assertIsInstance(result, list, 'SQL failure must not pass as an empty result')
        return sorted(p.sub_title for p in result)

    def test_default_window_three_identical_titles(self):
        for label, start in (('past', NOW - DELTA(days=2)), ('now', NOW),
                             ('future', NOW + DELTA(days=3))):
            self.add(label, start)
        for plot in ('false', 'true'):
            with self.subTest(plot=plot):
                self.assertEqual(self.labels(plot=plot), ['now'])

    def test_inclusive_boundaries_and_containment_not_overlap(self):
        lower, upper = NOW - DELTA(hours=6), NOW + DELTA(days=1)
        for label, start, end in (
                ('lower', lower, lower + DELTA(minutes=30)),
                ('inside', lower + DELTA(seconds=1), upper - DELTA(seconds=1)),
                ('upper', upper - DELTA(minutes=30), upper),
                ('before', lower - DELTA(seconds=1), lower + DELTA(minutes=30)),
                ('after', upper - DELTA(minutes=30), upper + DELTA(seconds=1)),
                ('spanning', lower - DELTA(seconds=1), upper + DELTA(seconds=1))):
            self.add(label, start, end)
        for plot in ('false', 'true'):
            with self.subTest(plot=plot):
                self.assertEqual(self.labels(plot=plot), ['inside', 'lower', 'upper'])
        row = self.conn.execute('SELECT start_date, typeof(start_date) AS storage FROM programs').fetchone()
        self.assertEqual(row['start_date'], lower)
        self.assertIn(row['storage'], ('integer', 'real'))

    def test_nondefault_settings_are_used(self):
        self.settings.update({'listing.days': '2', 'listing.hours': '2'})
        self.add('past-outside', NOW - DELTA(hours=3))
        self.add('past-inside', NOW - DELTA(hours=1))
        self.add('future-inside', NOW + DELTA(hours=36))
        self.add('future-outside', NOW + DELTA(days=3))
        for plot in ('false', 'true'):
            with self.subTest(plot=plot):
                self.assertEqual(self.labels(plot=plot), ['future-inside', 'past-inside'])

    def test_active_source_visible_crosschannel_results_and_metadata(self):
        title = 'Café — O\'Brien, "News" 📺'
        for channel, source in (('a', 'active'), ('b', 'active'), ('hidden', 'active'),
                                ('a', 'other'), ('unknown', 'active')):
            self.add('Subtitle 日本語', title=title, channel=channel, source=source)
        for plot in ('false', 'true'):
            with self.subTest(plot=plot):
                self.settings['program.search.plot'] = plot
                rows = self.db._programSearch('Café')
                self.assertEqual([p.channel.id for p in rows], ['b', 'a'])
                for p in rows:
                    expected = self.Program(p.channel, title, 'Subtitle 日本語', NOW,
                                            NOW + DELTA(minutes=30), 'Synopsis', 'Drama,Fixture',
                                            'large.png', 'small.png', season='2', episode='3',
                                            is_new='New', is_movie='', language='ja')
                    self.assertEqual(vars(p), vars(expected))
                    expected_channel = self.Channel(p.channel.id, 'active/' + p.channel.id,
                                                    'Lineup', 'logo.png', 'fixture://stream', 1,
                                                    0 if p.channel.id == 'b' else 1)
                    self.assertEqual(vars(p.channel), vars(expected_channel))

    def test_plot_toggle_only_changes_matching_fields(self):
        self.add('title', title='Needle title', description='Plain synopsis')
        self.add('plot', title='Other title', description='Needle synopsis')
        self.add('outdated-title', NOW - DELTA(days=2), title='Needle title')
        self.assertEqual(self.labels('Needle', 'false'), ['title'])
        self.assertEqual(self.labels('Needle', 'true'), ['plot', 'title'])

    def test_unicode_punctuation_bound_parameters_and_like_wildcards(self):
        for label, title in (('cafe', "Café — O'Brien (100%)"), ('percent', '100 percent'),
                             ('underscore', 'a_b'), ('single', 'axb'), ('japanese', '日本語')):
            self.add(label, title=title)
        all_labels = ['cafe', 'japanese', 'percent', 'single', 'underscore']
        for plot in ('false', 'true'):
            for query, expected in (
                    ("Café — O'Brien", ['cafe']), ('日本語', ['japanese']),
                    ('100%', ['cafe', 'percent']), ('a_b', ['single', 'underscore']),
                    ('%', all_labels), ('_', all_labels), ('', all_labels),
                    ("x' OR 1=1 --", []), ('no match', [])):
                with self.subTest(plot=plot, query=query):
                    self.assertEqual(self.labels(query, plot), expected)

    def test_no_visible_channels_returns_empty(self):
        self.add('hidden-by-setting')
        self.conn.execute('UPDATE channels SET visible=0 WHERE source=?', ('active',))
        for plot in ('false', 'true'):
            with self.subTest(plot=plot):
                self.assertEqual(self.labels(plot=plot), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
