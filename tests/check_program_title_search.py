"""Fresh XMLTV -> real parser -> stored rows -> production search, without Kodi.

The clock is fixed to the fixture reference, not a retained/aging database.
SPDX-License-Identifier: GPL-2.0-or-later
"""
import datetime
import io
import sqlite3
import sys
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from xml.sax.saxutils import escape

from check_channel_search_empty import extract
import check_empty_list_navigation as navigation
import check_program_search_window as window
import check_xmltv_source_offsets as offsets


REFERENCE = datetime.datetime(2026, 11, 25, 12)
GEORGIE = "Georgie & Mandy's First Marriage"
CURLY = 'Georgie & Mandy’s First Marriage'
COMBINED = 'The Joy Of Painting - Waterfall'
# Each programme has its own channel, so all can genuinely be current together.
CASES = (
    ('sixty', '60 Minutes', None, 'Synthetic synopsis'),
    ('georgie', GEORGIE, None, 'Synthetic synopsis'),
    ('roseanne', 'Roseanne', None, 'Synthetic synopsis'),
    ('frontline', 'Frontline', None, 'Synthetic synopsis'),
    ('combined', COMBINED, None, 'Synthetic synopsis'),
    ('subtitle', 'The Joy Of Painting', 'Waterfall', 'Synthetic synopsis'),
    ('curly', CURLY, None, 'Synthetic synopsis'),
    ('padded', '  Roseanne  ', '', 'Synthetic synopsis'),
    ('entity', 'Double &amp; Escape', None, 'Synthetic synopsis'),
    ('plot', 'Synopsis fixture', None, 'Waterfall in the synopsis only'),
    ('bound', "x' OR 1=1 --", None, 'Synthetic synopsis'),
)


def fixture_xml(reference):
    """Pure fixture builder; --fixture prints a newly dated native input."""
    def text(value):
        return escape(value, {"'": '&apos;'}).replace('’', '&#x2019;')

    start = (reference - datetime.timedelta(minutes=15)).strftime('%Y%m%d%H%M%S +0000')
    stop = (reference + datetime.timedelta(minutes=15)).strftime('%Y%m%d%H%M%S +0000')
    rows = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv>']
    for key, title, subtitle, description in CASES:
        rows.append('<channel id="%s"><display-name>Fixture %s</display-name></channel>'
                    % (key, key))
    for key, title, subtitle, description in CASES:
        rows.extend([
            '<programme channel="%s" start="%s" stop="%s">' % (key, start, stop),
            '<title lang="en">%s</title>' % text(title),
            '' if subtitle is None else '<sub-title>%s</sub-title>' % text(subtitle),
            '<desc>%s</desc><category>Fixture</category>' % text(description),
            '</programme>'])
    return ('\n'.join(rows) + '\n</tv>\n').encode('utf-8')


class ProgramTitleSearch(unittest.TestCase):
    def setUp(self):
        clock = patch.object(window, 'NOW', REFERENCE)
        clock.start()
        self.addCleanup(clock.stop)
        window.ProgramSearchWindow.setUp(self)
        source, env, vfs = offsets.SourceOffsets().source((False, False), (True, False, False), (0, 0, 0))
        self.xml = fixture_xml(REFERENCE)
        vfs.files['primary'] = self.xml
        parsed = list(source.getDataFromExternal(REFERENCE.date(), []))
        self.parsed = {p.channel: p for p in parsed if isinstance(p, env['Program'])}
        channels = [c for c in parsed if isinstance(c, env['Channel'])]
        self.assertEqual(len(channels), len(CASES))
        self.assertEqual(len(self.parsed), len(CASES))
        # Use the actual writer and Unix-seconds codecs. The programme insert is
        # also used by the full cache importer; no download/refresh is simulated.
        writer_cls = extract('source.py', 'Database', dict(datetime=datetime, sqlite3=sqlite3, time=time),
                             {'_updateProgramList', 'adapt_datetime', 'convert_datetime'})
        writer = writer_cls()
        writer.conn, writer.source = self.conn, self.db.source
        self.conn.execute('ALTER TABLE programs ADD COLUMN updates_id INTEGER')
        for weight, channel in enumerate(channels, 10):
            self.conn.execute('INSERT INTO channels VALUES (?,?,?,?,?,?,?,?)', (
                channel.id, channel.title, '', channel.logo, '', 'active', 1, weight))
            writer._updateProgramList([self.parsed[channel.id]], channel)

    def ids(self, query, plot='false'):
        self.settings['program.search.plot'] = plot
        rows = self.db._programSearch(query)
        self.assertIsInstance(rows, list, 'SQL failure is not an empty result')
        return sorted(p.channel.id for p in rows)

    def test_xml_parser_stored_rows_and_returned_metadata(self):
        self.assertIn(b'Georgie &amp; Mandy&apos;s', self.xml)
        self.assertIn(b'Mandy&#x2019;s', self.xml)
        self.assertIn(b'Double &amp;amp; Escape', self.xml)
        for key, title, subtitle, description in CASES:
            with self.subTest(key=key):
                parsed = self.parsed[key]
                stored = self.conn.execute('SELECT * FROM programs WHERE channel=?', (key,)).fetchone()
                self.assertEqual((parsed.title, parsed.sub_title, parsed.description),
                                 (title, subtitle, description))
                self.assertEqual((stored['title'], stored['sub_title'], stored['description']),
                                 (title, subtitle, description))
                self.assertEqual((stored['start_date'], stored['end_date']),
                                 (REFERENCE - datetime.timedelta(minutes=15),
                                  REFERENCE + datetime.timedelta(minutes=15)))
                rows = self.db._programSearch(title)
                result = next(p for p in rows if p.channel.id == key)
                self.assertEqual((result.title, result.sub_title, result.description),
                                 (title, subtitle, description))

    def test_reported_main_titles_already_match_ascii_case_and_partial(self):
        for plot in ('false', 'true'):
            for query, expected in (
                    ('60 Minutes', ['sixty']), (GEORGIE, ['georgie']),
                    ('Roseanne', ['padded', 'roseanne']), ('Frontline', ['frontline']),
                    (COMBINED, ['combined']), ('Minutes', ['sixty']),
                    ("Mandy's", ['georgie'])):
                for variant in (query, query.upper(), query.lower()):
                    with self.subTest(plot=plot, query=variant):
                        self.assertEqual(self.ids(variant, plot), expected)

    def test_episode_subtitle_is_searchable_without_enabling_synopsis(self):
        for plot in ('false', 'true'):
            for query in ('Waterfall', 'WATERFALL', 'waterfall', 'aterfal'):
                with self.subTest(plot=plot, query=query):
                    expected = ['combined', 'subtitle']
                    if plot == 'true':
                        expected.insert(1, 'plot')
                    self.assertEqual(self.ids(query, plot), expected)
        self.assertEqual(self.ids('synopsis only'), [])
        self.assertEqual(self.ids('synopsis only', 'true'), ['plot'])
        self.conn.execute('UPDATE programs SET sub_title=? WHERE channel=?', ('Waterfall', 'combined'))
        self.assertEqual(self.ids('Waterfall'), ['combined', 'subtitle'])  # No duplicate OR match.

    def test_empty_wildcard_and_no_visible_channel_results(self):
        all_ids = sorted(key for key, *_ in CASES)
        for plot in ('false', 'true'):
            for query in ('', '%', '_'):
                self.assertEqual(self.ids(query, plot), all_ids)
        self.conn.execute('UPDATE channels SET visible=0 WHERE source=?', ('active',))
        for plot in ('false', 'true'):
            self.assertEqual(self.ids('Waterfall', plot), [])

    def test_literal_entities_apostrophes_padding_and_injection_text(self):
        # Deliberately retain LIKE semantics, not punctuation/HTML/fuzzy folding.
        for plot in ('false', 'true'):
            for query, expected in (
                    (CURLY, ['curly']), (CURLY.upper(), ['curly']),
                    ('Georgie &amp; Mandy', []), ('Double &amp; Escape', ['entity']),
                    ('Double & Escape', []), ('  Roseanne  ', ['padded']),
                    (' Frontline ', []), ("x' OR 1=1 --", ['bound']),
                    ('unmatched programme', [])):
                with self.subTest(plot=plot, query=query):
                    self.assertEqual(self.ids(query, plot), expected)

    def test_subtitle_cannot_bypass_window_visibility_category_or_source(self):
        self.conn.execute("UPDATE programs SET title='Other', sub_title='Needle'")
        # All the ordinary title fixtures must now match only through sub_title.
        self.conn.execute('UPDATE channels SET visible=0 WHERE id=?', ('sixty',))
        self.conn.execute('UPDATE programs SET source=? WHERE channel=?', ('other', 'georgie'))
        self.conn.execute('UPDATE programs SET start_date=?, end_date=? WHERE channel=?', (
            REFERENCE - datetime.timedelta(days=2), REFERENCE - datetime.timedelta(days=1), 'roseanne'))
        self.conn.execute('UPDATE programs SET end_date=? WHERE channel=?', (
            REFERENCE + datetime.timedelta(days=1, seconds=1), 'frontline'))
        # Real _getChannelList category filtering, with an in-memory categories.ini.
        self.db.category = 'Selected'
        self.db._getChannelList.__func__.__globals__['xbmcvfs'] = SimpleNamespace(
            File=lambda *args: io.StringIO('Fixture combined=Selected\nFixture subtitle=Selected\n'
                                          'Fixture sixty=Selected\nFixture georgie=Selected\n'
                                          'Fixture roseanne=Selected\nFixture frontline=Selected\n'))
        for plot in ('false', 'true'):
            self.assertEqual(self.ids('Needle', plot), ['combined', 'subtitle'])

    def test_subtitle_inclusive_containment_boundaries(self):
        self.conn.execute('DELETE FROM programs')
        lower = REFERENCE - datetime.timedelta(hours=6)
        upper = REFERENCE + datetime.timedelta(days=1)
        for label, start, end in (
                ('lower', lower, lower + datetime.timedelta(minutes=30)),
                ('upper', upper - datetime.timedelta(minutes=30), upper),
                ('before', lower - datetime.timedelta(seconds=1), lower),
                ('after', upper, upper + datetime.timedelta(seconds=1)),
                ('spanning', lower - datetime.timedelta(seconds=1), upper + datetime.timedelta(seconds=1))):
            self.conn.execute('''INSERT INTO programs(channel,source,title,sub_title,start_date,end_date)
                                 VALUES (?,?,?,?,?,?)''', ('a', 'active', 'Other', label + ' Needle', start, end))
        for plot in ('false', 'true'):
            self.settings['program.search.plot'] = plot
            self.assertEqual(sorted(p.sub_title for p in self.db._programSearch('Needle')),
                             ['lower Needle', 'upper Needle'])

    def test_selected_category_strict_title_search_preserves_guide_fallback(self):
        # Exercise the public search dispatch after the real category setter.
        # Only worker-thread dispatch is synchronous here; SQL/filtering are real.
        self.db._invokeAndBlockForResult = lambda method, *args: method(*args)
        self.conn.execute('UPDATE channels SET visible=0 WHERE id=?', ('sixty',))
        categories = ('Fixture subtitle=Populated\nFixture combined=Populated\n'
                      'Fixture sixty=Hidden only\nMissing channel=Stale\n')
        self.db._getChannelList.__func__.__globals__['xbmcvfs'] = SimpleNamespace(
            File=lambda *args: io.StringIO(categories))
        visible = [c.id for c in self.db._getChannelList(True, all=True)]
        self.assertIn('combined', visible)  # Nonempty All Channels control.
        for sort in ('0', '1', '2'):
            self.settings['channel.filter.sort'] = sort
            for category, expected in (
                    ('Populated', ['combined', 'subtitle']),
                    ('Empty', []), ('Hidden only', []), ('Stale', [])):
                self.db.setCategory(category)
                self.assertEqual(self.db.category, category)
                for plot in ('false', 'true'):
                    self.settings['program.search.plot'] = plot
                    with self.subTest(sort=sort, category=category, plot=plot):
                        rows = self.db.programSearch('Waterfall')
                        self.assertIsInstance(rows, list)
                        self.assertEqual(sorted(p.channel.id for p in rows), expected)
                # Guide callers keep the unfiltered fallback, without changing
                # the selected category; title search must not inherit it.
                if category != 'Populated':
                    self.assertEqual([c.id for c in self.db._getChannelList(True)], visible)
                    self.assertEqual(self.db.category, category)

    def test_title_search_all_channel_sentinels(self):
        self.db._getChannelList.__func__.__globals__['xbmcvfs'] = SimpleNamespace(
            File=lambda *args: io.StringIO('Fixture sixty=Other\n'))
        for category in ('All Channels', 'Any', '', None):
            self.db.setCategory(category)
            for sort in ('0', '1', '2'):
                self.settings['channel.filter.sort'] = sort
                for sort_all in ('false', 'true'):
                    self.settings['channel.filter.sort.all'] = sort_all
                    for plot in ('false', 'true'):
                        with self.subTest(category=category, sort=sort,
                                          sort_all=sort_all, plot=plot):
                            expected = ['combined', 'subtitle']
                            if plot == 'true':
                                expected.insert(1, 'plot')
                            self.assertEqual(self.ids('Waterfall', plot), expected)

    def test_category_channel_now_next_unchanged(self):
        clock = SimpleNamespace(datetime=SimpleNamespace(now=lambda: REFERENCE),
                                timedelta=datetime.timedelta)
        env = dict(datetime=clock, re=window.re, Program=self.Program,
                   ADDON=SimpleNamespace(getSetting=lambda key: self.settings.get(key, '')))
        cls = extract('source.py', 'Database', env, {
            '_programCategorySearch', '_channelSearch', '_getNowList', '_getNextList'})
        db = cls()
        db.conn, db.source, db._getChannelList = self.conn, self.db.source, self.db._getChannelList
        all_ids = sorted(key for key, *_ in CASES)
        self.assertEqual(sorted(p.channel.id for p in db._programCategorySearch('Fixture')), all_ids)
        self.assertEqual([p.channel.id for p in db._channelSearch('Fixture frontline')], ['frontline'])
        self.assertEqual(sorted(p.channel.id for p in db._getNowList()), all_ids)
        self.assertEqual(db._getNextList(), [])
        self.conn.execute('UPDATE programs SET start_date=?, end_date=? WHERE channel=?', (
            REFERENCE + datetime.timedelta(minutes=15), REFERENCE + datetime.timedelta(minutes=45), 'frontline'))
        self.assertEqual([p.channel.id for p in db._getNextList()], ['frontline'])

    def test_matching_rows_render_and_keep_selected_identity(self):
        # Real search output enters the existing inert six-handler UI harness.
        # Kodi's physical keyboard/mouse/focus dispatch still needs native tests.
        rows = self.db._programSearch('Waterfall')
        self.assertEqual([p.channel.id for p in rows], ['combined', 'subtitle'])
        nav = navigation.EmptyListNavigation()
        nav.setUp()
        self.addCleanup(nav.doCleanups)
        nav.programs, nav.row = rows, 1

        class LabelItem(navigation.Item):
            def __init__(self, label, name):
                super().__init__()
                self.label = label

        nav.Guide.programSearch.__globals__['xbmcgui'].ListItem = LabelItem
        for sort_time in (False, True):
            nav.sort_time = sort_time
            for action in ('select', 117, 1, 92):
                nav.action = action
                nav.run_handler('programSearch')
                items = nav.dialogs[-1].controls[1000].items
                self.assertEqual([item.label for item in items], [COMBINED, 'The Joy Of Painting'])
                self.assertEqual([item.getProperty('index') for item in items], ['0', '1'])
                expected = ([('play', rows[1], True)] if action == 'select' else
                            [('menu', rows[1])] if action == 117 else
                            [('listing', rows[1].channel)] if action == 1 else [])
                self.assertEqual(nav.events, expected)
                self.assertEqual(rows[1].sub_title, 'Waterfall')

    def test_history_new_reuse_remove_cancel_and_empty_input(self):
        history = {'text': '', 'writes': [], 'choice': 0, 'input': 'Waterfall'}

        class HistoryFile(io.StringIO):
            def __init__(file, path, mode):
                self.assertEqual(path, 'special://profile/addon_data/script.tvguide.fullscreen/title_search.list')
                super().__init__(history['text'] if mode == 'rb' else '')
                file.mode = mode

            def close(file):
                if file.mode == 'wb':
                    history['text'] = file.getvalue()
                    history['writes'].append(history['text'])
                super().close()

        queries, prefills, rendered = [], [], []

        def search(query):
            queries.append(query)
            return self.db._programSearch(query)

        def input_text(heading, default):
            prefills.append(default)
            return history['input']

        def results(title, rows, sort_time):
            rendered.append(rows)
            return SimpleNamespace(doModal=lambda: None, index=-1, action=None)

        env = dict(xbmcvfs=SimpleNamespace(File=HistoryFile),
                   xbmcgui=SimpleNamespace(Dialog=lambda: SimpleNamespace(
                       select=lambda title, options: history['choice'], input=input_text)),
                   ADDON=SimpleNamespace(getSetting=lambda key: 'false'),
                   ProgramListDialog=results, ACTION_RIGHT=2, ACTION_LEFT=1, KEY_CONTEXT_MENU=117)
        cls = extract('gui.py', 'TVGuide', env, {'programSearch'})
        guide = cls()
        guide.getFocus, guide.currentProgram = lambda: None, None
        guide.database = SimpleNamespace(programSearch=search)
        guide.programSearch()
        self.assertEqual(history['text'], 'Waterfall')
        self.assertEqual([p.channel.id for p in rendered[-1]], ['combined', 'subtitle'])
        history['choice'] = 2  # Reuse first sorted history entry.
        guide.programSearch()
        self.assertEqual(prefills, ['', 'Waterfall'])
        self.assertEqual(queries, ['Waterfall', 'Waterfall'])
        self.assertEqual(history['text'], 'Waterfall')  # Deduplicated.
        before = list(history['writes'])
        history['choice'] = -1
        guide.programSearch()
        history['choice'], history['input'] = 0, ''
        guide.programSearch()
        self.assertEqual(history['writes'], before)
        self.assertEqual(queries, ['Waterfall', 'Waterfall'])
        # Remove Search then its first entry; no SQL or results dialog.
        choices = iter((1, 0))
        env['xbmcgui'].Dialog = lambda: SimpleNamespace(select=lambda *args: next(choices))
        guide.programSearch()
        self.assertEqual(history['text'], '')
        self.assertEqual(len(queries), 2)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--fixture':
        reference = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%dT%H:%M:%SZ')
        sys.stdout.buffer.write(fixture_xml(reference))
    else:
        unittest.main(verbosity=2)
