"""Execute actual PopupMenu methods with inert controls, not Kodi or its stubs.

Bundled XML supplies real control IDs; optional-control variants model the
existing visibility/enabled guards, not Kodi layout or native acceptance.
No legacy module import, network, settings writes, player or database is used.
"""
import ast
import datetime
from pathlib import Path
import re
from types import SimpleNamespace
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TREE = ast.parse((ROOT / 'gui.py').read_text(), feature_version=(3, 8))
OPTIONAL = {77000: 'Visible', 77003: 'Visible', 44000: 'Visible',
            4103: 'Visible', 4104: 'Visible', 4105: 'Enabled',
            4106: 'Visible', 4107: 'Visible', 44101: 'Visible'}
DETAILS = {7000, 7001, 7003, 7002, 4002, 4008, 4009,
           4100, 4101, 4102, 4005, 4006}


class Control:
    def __init__(self):
        self.enabled = True
        self.visible = True
        self.label = self.text = self.image = None
        self.percent = None
        self.items = []

    def setEnabled(self, value):
        self.enabled = value

    def setVisible(self, value):
        self.visible = value

    def setLabel(self, value):
        self.label = value

    def setText(self, value):
        self.text = value

    def setImage(self, value):
        self.image = value

    def setPercent(self, value):
        self.percent = value

    def addItems(self, items):
        self.items.extend(items)

    def selectItem(self, index):
        self.selected = index


class WindowCapture:
    def __init__(self):
        self.closed = False

    def getControl(self, control_id):
        self.lookups.append(control_id)
        if control_id not in self.controls:
            raise RuntimeError('Non-Existent Control %s' % control_id)
        return self.controls[control_id]

    def setFocusId(self, control_id):
        self.focus = control_id

    def close(self):
        self.closed = True


def popup_class(condition):
    namespace = {'WindowCapture': WindowCapture, 'datetime': datetime,
                 'xbmc': SimpleNamespace(getCondVisibility=condition),
                 'xbmcgui': SimpleNamespace(ListItem=lambda label: label),
                 'ADDON': SimpleNamespace(getSetting=lambda _: 'false'),
                 'strings': lambda key: key, 'CHOOSE_STRM_FILE': 'Choose stream'}
    for node in TREE.body:
        if isinstance(node, ast.Assign):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name):
                    namespace[target.id] = value
    original = next(n for n in TREE.body
                    if isinstance(n, ast.ClassDef) and n.name == 'PopupMenu')
    # Whole, unchanged methods, including onInit and action dispatch. Only the
    # native XML allocator is excluded; the inert base replaces WindowXMLDialog.
    body = [n for n in original.body if isinstance(n, ast.Assign)
            or isinstance(n, ast.FunctionDef) and n.name != '__new__']
    captured = ast.ClassDef(name='PopupMenu',
                            bases=[ast.Name(id='WindowCapture', ctx=ast.Load())],
                            keywords=[], body=body, decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[captured], type_ignores=[]))
    exec(compile(module, str(ROOT / 'gui.py'), 'exec'), namespace)
    return namespace['PopupMenu'], namespace


def make_popup(title='Ordinary episode', skin='Default', extras=(), hidden=(),
               channel=True, scheduled=False, timed=True, mapped=True):
    layout = ROOT / 'resources/skins' / skin / '720p/script-tvguide-menu.xml'
    ids = {int(n.get('id')) for n in ET.parse(layout).iter('control') if n.get('id')}
    ids.update(extras)
    active = set(extras) - set(hidden)
    lookups = []

    def condition(expression):
        match = re.fullmatch(r'Control.Is(Visible|Enabled)\((\d+)\)', expression)
        if match:
            kind, number = match.groups()
            number = int(number)
            if number in OPTIONAL:
                return number in active and kind == OPTIONAL[number]
            return number in ids
        # No setup group in the bundled layouts. Unexpected expressions must
        # fail rather than silently skip an unmodeled branch.
        if expression == '[Control.IsVisible(40011)|Control.IsVisible(44001)]':
            return False
        raise AssertionError('Unexpected condition: ' + expression)

    Popup, namespace = popup_class(condition)
    start = datetime.datetime.now().replace(second=0, microsecond=0)
    programme = SimpleNamespace(
        channel=SimpleNamespace(title='Fixture channel', logo='logo.png',
                                isPlayable=lambda: True) if channel else None,
        title=title, sub_title='Episode subtitle', categories='Drama,Comedy',
        season='2', episode='3', description='Ordinary description',
        imageSmall='small.png', imageLarge='large.png',
        startDate=start if timed else None,
        endDate=start + datetime.timedelta(minutes=30) if timed else None)
    next_programme = SimpleNamespace(title='Next episode', startDate=start,
                                     endDate=start + datetime.timedelta(minutes=30))
    database = SimpleNamespace(
        getNextProgram=lambda _: next_programme, getPreviousProgram=lambda _: None,
        isNotificationRequiredForProgramStart=lambda _: scheduled,
        isAutoPlayRequiredForProgramStart=lambda _: scheduled,
        isAutoPlaywithRequiredForProgramStart=lambda _: scheduled,
        getCustomStreamUrl=lambda _: 'inert://mapped' if mapped else None)
    popup = Popup(database, programme, True, True, True, 'Drama', ['Drama'])
    popup.controls = {number: Control() for number in ids}
    popup.lookups = lookups
    return popup, namespace


class PopupOptionalControls(unittest.TestCase):
    def test_bundled_missing_programme_preserves_disabled_details_and_channel_play(self):
        for skin in ('Default', 'CatBar', 'Dark'):
            for title in ('', None):
                with self.subTest(skin=skin, title=title):
                    popup, _ = make_popup(title, skin, timed=False)
                    self.assertTrue(set(OPTIONAL).isdisjoint(popup.controls))
                    popup.onInit()
                    self.assertTrue(all(not popup.controls[n].enabled for n in DETAILS))
                    self.assertTrue(popup.controls[4000].enabled)
                    self.assertEqual(popup.controls[4000].label, 'Watch Channel')
                    self.assertTrue(popup.controls[4001].enabled)
                    self.assertIn(4108, popup.lookups)  # caught subtitle miss

    def test_each_optional_detail_can_be_absent_or_hidden(self):
        for number in set(OPTIONAL) - {44000}:
            for absent in (False, True):
                with self.subTest(control=number, absent=absent):
                    extras = set(OPTIONAL) - ({number} if absent else set())
                    popup, _ = make_popup('', extras=extras, hidden={number})
                    popup.onInit()
                    self.assertNotIn(number, popup.lookups)
                    if not absent:
                        self.assertTrue(popup.controls[number].enabled)
                    for other in set(OPTIONAL) - {number, 44000}:
                        self.assertFalse(popup.controls[other].enabled)

    def test_all_optional_details_are_disabled_when_available(self):
        for title in ('', None):
            with self.subTest(title=title):
                popup, _ = make_popup(title, extras=OPTIONAL)
                popup.onInit()
                for number in DETAILS | (set(OPTIONAL) - {44000}):
                    self.assertFalse(popup.controls[number].enabled, number)
                self.assertTrue(popup.controls[44000].enabled)

    def test_populated_details_and_scheduling_labels(self):
        for skin in ('Default', 'CatBar', 'Dark'):
            for extras in ((), tuple(OPTIONAL) + (4108,)):
                for scheduled in (False, True):
                    with self.subTest(skin=skin, extras=extras, scheduled=scheduled):
                        popup, _ = make_popup(skin=skin, extras=extras, scheduled=scheduled)
                        popup.onInit()
                        controls = popup.controls
                        self.assertEqual(controls[7001].label, 'Ordinary episode S2E3')
                        self.assertEqual(controls[4102].label, '[B]Ordinary episode[/B]')
                        self.assertEqual(controls[7000].label, 'Ordinary description')
                        self.assertEqual(controls[4101].label, 'Fixture channel')
                        self.assertEqual(controls[4100].image, 'logo.png')
                        self.assertEqual(controls[7002].image, 'large.png')
                        self.assertIn('Today', controls[7003].label)
                        self.assertEqual(controls[4002].label,
                                         "Don't Remind" if scheduled else 'Remind')
                        self.assertEqual(controls[4008].label,
                                         "Don't AutoPlay" if scheduled else 'AutoPlay')
                        self.assertTrue(all(controls[n].enabled for n in DETAILS))
                        self.assertEqual(controls[4009].label, 'Record (Kodi PVR)…')
                        self.assertEqual(controls[7004].items, ['All Channels', 'Drama'])
                        if extras:
                            self.assertEqual(controls[77000].text, 'Ordinary description')
                            self.assertEqual(controls[4108].label, 'Episode subtitle - s2e3')
                            self.assertEqual(controls[4103].label, 'Length: 30 Minute(s)')
                            self.assertEqual(controls[4106].label, 'Next episode')
                            self.assertIsInstance(controls[4105].percent, int)

    def test_missing_channel_disables_play_and_optional_stop(self):
        for available in (False, True):
            with self.subTest(stop_available=available):
                extras = set(OPTIONAL) | {40011, 44001}
                popup, _ = make_popup(extras=extras, hidden=() if available else {44000},
                                      channel=False)
                popup.onInit()
                for number in (4000, 4001, 40011, 44001, 4007, 4014):
                    self.assertFalse(popup.controls[number].enabled)
                self.assertEqual(popup.controls[44000].enabled, not available)

    def test_popup_actions_still_return_selection_and_back_closes(self):
        for title in ('Ordinary episode', '', None):
            for control in (4000, 4001, 4007, 4011, 4004):
                with self.subTest(title=title, control=control):
                    popup, _ = make_popup(title, timed=bool(title), mapped=False)
                    popup.onInit()
                    popup.onClick(control)
                    self.assertEqual(popup.buttonClicked, control)
                    self.assertTrue(popup.closed)
            popup, namespace = make_popup(title, timed=bool(title))
            popup.onInit()
            popup.onAction(SimpleNamespace(getId=lambda: namespace['KEY_NAV_BACK']))
            self.assertTrue(popup.closed)
            self.assertIsNone(popup.buttonClicked)

    def test_mapped_choose_stream_still_removes_mapping_without_closing(self):
        popup, _ = make_popup()
        removed = []
        popup.database.deleteCustomStreamUrl = removed.append
        popup.onInit()
        popup.onClick(4001)
        self.assertEqual(removed, [popup.program.channel])
        self.assertFalse(popup.closed)
        self.assertIsNone(popup.buttonClicked)

    def test_literal_dash_is_not_treated_as_an_empty_title(self):
        popup, _ = make_popup('-')
        popup.onInit()
        self.assertEqual(popup.controls[4102].label, '[B]-[/B]')
        self.assertTrue(all(popup.controls[n].enabled for n in DETAILS))


if __name__ == '__main__':
    unittest.main()
