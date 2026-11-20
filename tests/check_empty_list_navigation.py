"""Execute production dialog and six complete handlers with synthetic inert UI.

No Kodi/stub imports, profile access, network, player or native acceptance.
Reuse the existing extraction helper; only UI/database boundaries are captures.
"""
import ast
import datetime
import time
from types import SimpleNamespace
import unittest

from check_channel_search_empty import ROOT, WindowCapture, extract


HANDLERS = ('showNow', 'showNext', 'programSearch', 'descriptionSearch',
            'categorySearch', 'channelSearch')
DATABASE_METHODS = ('getNowList', 'getNextList', 'programSearch',
                    'descriptionSearch', 'programCategorySearch', 'channelSearch')


class Item:
    def __init__(self, *args):
        self.properties = {}

    def setArt(self, art):
        pass

    def setProperty(self, key, value):
        self.properties[key] = value

    def getProperty(self, key):
        return self.properties[key]


class MemoryFile:
    def __init__(self, path, mode):
        self.text = 'Synthetic=1' if path.endswith('category_count.ini') else ''

    def read(self):
        return self.text

    def write(self, text):
        pass

    def close(self):
        pass


class EmptyListNavigation(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.dialogs = []
        self.action = 1
        self.row = 0
        self.no_selection = False
        self.forced_index = None
        self.sort_time = False
        self.programs = []
        case = self

        class ModalCapture(WindowCapture):
            def doModal(dialog):
                dialog.onInit()
                case.dialogs.append(dialog)
                control = dialog.controls[1000]
                control.getSelectedItem = lambda: (
                    control.items[case.row]
                    if control.items and not case.no_selection else None)
                if case.action == 'select':
                    dialog.onClick(1000)
                else:
                    dialog.onAction(SimpleNamespace(getId=lambda: case.action))
                # Stale/corrupt stored item index: exercise bounds, not UI logic.
                if case.forced_index is not None:
                    dialog.index = case.forced_index
                case.assertTrue(dialog.closed)

        env = {'datetime': datetime, 'time': time,
               'timedelta_total_seconds': lambda delta: delta.total_seconds(),
               'COMMAND_ACTIONS': {'CLOSE': [9, 10, 92], 'MENU': [117]},
               'ADDON': SimpleNamespace(getSetting=lambda key:
                   'true' if key == 'listing.sort.time' and self.sort_time else 'false'),
               'xbmcgui': SimpleNamespace(
                   ListItem=Item,
                   Dialog=lambda: SimpleNamespace(select=lambda *args: 0,
                                                  input=lambda *args: 'Synthetic')),
               'xbmcvfs': SimpleNamespace(File=MemoryFile)}
        for node in ast.parse((ROOT / 'gui.py').read_text()).body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in (
                            'ACTION_LEFT', 'ACTION_RIGHT', 'KEY_CONTEXT_MENU'):
                        env[target.id] = ast.literal_eval(node.value)
        env['ProgramListDialog'] = extract(
            'gui.py', 'ProgramListDialog', env,
            {'__init__', 'onInit', 'onAction', 'onClick',
             'formatDateTodayTomorrow', 'close'}, base=ModalCapture)
        self.Guide = extract('gui.py', 'TVGuide', env, set(HANDLERS))

    def populated(self):
        start = datetime.datetime.now() + datetime.timedelta(days=2)
        self.programs = [SimpleNamespace(
            title='Synthetic programme', channel=SimpleNamespace(title=title, logo=''),
            startDate=start + datetime.timedelta(hours=hours),
            endDate=start + datetime.timedelta(hours=hours + 1),
            description='', imageSmall='', imageLarge='')
            for title, hours in [('Channel A', 3), ('Channel B', 1)]]

    def run_handler(self, handler):
        self.events.clear()
        guide = self.Guide()
        guide.database = SimpleNamespace(**{
            method: lambda *args: self.programs for method in DATABASE_METHODS})
        guide.category = None
        guide.currentProgram = None
        guide.getFocus = lambda: None
        guide.showListing = lambda channel: self.events.append(('listing', channel))
        guide.showNow = lambda: self.events.append(('now',))
        guide.showNext = lambda: self.events.append(('next',))
        guide._showContextMenu = lambda program: self.events.append(('menu', program))
        guide.playOrChoose = lambda program, choose: self.events.append(('play', program, choose))
        guide.play_catchup = lambda program: self.fail('unexpected catchup')
        getattr(self.Guide, handler)(guide)

    def dependent_arrow(self, handler):
        return 2 if handler == 'showNext' else 1

    def test_empty_item_dependent_arrows_are_harmless(self):
        for handler in HANDLERS:
            with self.subTest(handler=handler):
                self.action = self.dependent_arrow(handler)
                self.run_handler(handler)
                self.assertEqual(self.dialogs[-1].index, -1)
                self.assertEqual(self.events, [])

    def test_populated_arrows_route_exact_selected_channel(self):
        self.populated()
        for handler in HANDLERS:
            for row in (0, 1):
                with self.subTest(handler=handler, row=row):
                    self.action = self.dependent_arrow(handler)
                    self.row = row
                    self.run_handler(handler)
                    self.assertEqual(self.events, [('listing', self.programs[row].channel)])

    def test_no_selection_does_not_route_last_populated_channel(self):
        self.populated()
        self.no_selection = True
        for handler in HANDLERS:
            with self.subTest(handler=handler):
                self.action = self.dependent_arrow(handler)
                self.run_handler(handler)
                self.assertEqual(self.events, [])

    def test_out_of_bounds_arrow_does_not_fall_through_to_playback(self):
        self.populated()
        for handler in HANDLERS:
            for index in (-2, len(self.programs), len(self.programs) + 1):
                with self.subTest(handler=handler, index=index):
                    self.action = self.dependent_arrow(handler)
                    self.forced_index = index
                    self.run_handler(handler)
                    self.assertEqual(self.events, [])

    def test_empty_item_independent_now_next_routes_remain(self):
        for handler in HANDLERS:
            with self.subTest(handler=handler):
                self.action = 1 if handler == 'showNext' else 2
                self.run_handler(handler)
                self.assertEqual(self.events, [('now' if handler == 'showNext' else 'next',)])

    def test_empty_menu_select_and_back_are_harmless(self):
        for handler in HANDLERS:
            for action in (117, 'select', 9, 10, 92):
                with self.subTest(handler=handler, action=action):
                    self.action = action
                    self.run_handler(handler)
                    self.assertEqual(self.dialogs[-1].index, -1)
                    self.assertEqual(self.events, [])

    def test_populated_menu_select_and_back_keep_routing(self):
        self.populated()
        self.row = 1
        for handler in HANDLERS:
            for action in (117, 'select', 92):
                with self.subTest(handler=handler, action=action):
                    self.action = action
                    self.run_handler(handler)
                    expected = ([('menu', self.programs[1])] if action == 117 else
                                [('play', self.programs[1], True)] if action == 'select' else [])
                    self.assertEqual(self.events, expected)

    def test_sorted_rows_keep_original_index_for_arrow_menu_and_select(self):
        self.populated()
        self.sort_time = True
        for handler in HANDLERS[2:]:
            for action in (1, 117, 'select'):
                with self.subTest(handler=handler, action=action):
                    self.action = action
                    self.run_handler(handler)
                    self.assertEqual(self.dialogs[-1].index, 1)
                    expected = ([('listing', self.programs[1].channel)] if action == 1 else
                                [('menu', self.programs[1])] if action == 117 else
                                [('play', self.programs[1], True)])
                    self.assertEqual(self.events, expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
