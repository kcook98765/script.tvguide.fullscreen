"""Focused pure snapshot/AST checks, NOT a Kodi or pixel-behavior simulation.

Only the new pure helper is imported. Kodi/stubs and legacy entry points are
never host-imported. All writes use disposable local temporary folders.
"""
import ast
import importlib.util
import io
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('custom_skin', ROOT / 'custom_skin.py')
skin = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(skin)
MAIN = 'script-tvguide-main.xml'


class CustomSkins(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='tvguide-skin-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'original'
        self.layout = self.source / 'resources/skins/Mine/720p'
        self.layout.mkdir(parents=True)
        self.media = self.layout.parent / 'media'
        self.media.mkdir()
        self.bundled = 'Default'

    def original(self, filename=MAIN):
        return ET.parse(ROOT / 'resources/skins' / self.bundled / '720p' / filename).getroot()

    def save(self, layout, filename=MAIN):
        (self.layout / filename).write_bytes(ET.tostring(layout, encoding='utf-8'))

    def prepare(self):
        snapshot = skin.prepare(str(ROOT), str(self.source), 'Mine', self.bundled, str(self.root))
        self.addCleanup(snapshot.directory.cleanup)
        return snapshot

    def loaded(self, snapshot, filename=MAIN):
        return ET.parse(Path(snapshot.path) / 'resources/skins' / snapshot.skin /
                        '720p' / snapshot.filenames[filename]).getroot()

    def png(self, name='mine.png'):
        out = io.BytesIO()
        Image.new('RGBA', (3, 2), (12, 34, 56, 78)).save(out, format='PNG')
        raw = out.getvalue() + b'UNUSED APPENDED DATA'
        (self.media / name).write_bytes(raw)
        return raw

    def test_customized_bundle_geometry_label_navigation_texture_all_three(self):
        for bundled in skin.BUNDLED:
            with self.subTest(bundled=bundled):
                self.bundled = bundled
                layout = self.original()
                next(layout.iter('posx')).text = '17'
                next(e for e in layout.iter('width') if not len(e)).text = '123'
                label = next(e for e in layout.iter('label') if (e.text or '').strip() and
                             '$' not in e.text and e.text.lower() not in ('true', 'false'))
                label.text = 'Café — My guide'
                menu = self.original('script-tvguide-menu.xml')
                nav = next(menu.iter('onright'))
                nav.text = next(e.get('id') for e in menu.iter('control') if e.get('id'))
                self.save(menu, 'script-tvguide-menu.xml')
                texture = next(layout.iter('texture'))
                texture.text = 'mine.png'
                raw = self.png()
                self.save(layout)
                snapshot = self.prepare()
                self.assertNotEqual(snapshot.path.rstrip(os.sep), str(self.source))
                output = self.loaded(snapshot)
                self.assertEqual(next(output.iter('posx')).text, '17')
                self.assertIn('Café — My guide', [e.text for e in output.iter('label')])
                image_path = Path(next(output.iter('texture')).text)
                image_path.relative_to(Path(snapshot.path))  # no is_relative_to (3.9+)
                self.assertTrue(image_path.is_file())
                self.assertNotEqual(image_path.read_bytes(), raw)
                with Image.open(image_path) as image:
                    self.assertEqual(image.getpixel((0, 0)), (12, 34, 56, 78))
                self.assertEqual((self.media / 'mine.png').read_bytes(), raw)
                self.assertTrue(all(name != original for original, name in snapshot.filenames.items()))

    def test_reject_hooks_providers_includes_templates_and_attribute_changes(self):
        attacks = [('onload', 'RunScript(INERT)'), ('onclick', 'RunAddon(INERT)'),
                   ('onfocus', 'RunScript(INERT)'), ('onunload', 'RunScript(INERT)'),
                   ('ontextchange', 'RunScript(INERT)'), ('onback', 'RunScript(INERT)'),
                   ('oninfo', 'RunScript(INERT)'), ('onnext', 'RunScript(INERT)'),
                   ('content', 'plugin://INERT/'), ('include', 'INERT'),
                   ('include', 'Other.xml'), ('item', 'plugin://INERT/')]
        for tag, text in attacks:
            with self.subTest(tag=tag, text=text):
                layout = self.original()
                ET.SubElement(layout.find('controls'), tag).text = text
                self.save(layout)
                with self.assertRaisesRegex(skin.SkinError, 'structure/control'):
                    self.prepare()
        layout = self.original()
        next(layout.iter('control')).set('onclick', 'RunScript(INERT)')
        self.save(layout)
        with self.assertRaises(skin.SkinError):
            self.prepare()
        # Existing content is NOT trusted merely because the element exists.
        layout = self.original('script-tvguide-vod-tv.xml')
        next(layout.iter('content')).text = 'plugin://INERT/'
        self.save(self.original())
        self.save(layout, 'script-tvguide-vod-tv.xml')
        with self.assertRaisesRegex(skin.SkinError, '<content>'):
            self.prepare()

    def test_real_space_unicode_source_directory_and_png_names(self):
        for name in ('My Skin', 'Café 日本語'):
            with self.subTest(name=name):
                source_skin = self.source / 'resources/skins' / name
                (source_skin / '720p').mkdir(parents=True)
                (source_skin / 'media').mkdir()
                layout = self.original()
                next(layout.iter('texture')).text = 'Café 日本語 image.png'
                original_xml = ET.tostring(layout, encoding='utf-8')
                (source_skin / '720p' / MAIN).write_bytes(original_xml)
                raw = self.png()
                (source_skin / 'media/Café 日本語 image.png').write_bytes(raw)
                snapshot = skin.prepare(str(ROOT), str(self.source), name, 'Default', str(self.root))
                self.addCleanup(snapshot.directory.cleanup)
                path = Path(next(self.loaded(snapshot).iter('texture')).text)
                self.assertTrue(path.is_file())
                self.assertTrue(path.name.isascii())
                self.assertEqual((source_skin / '720p' / MAIN).read_bytes(), original_xml)
                self.assertEqual((source_skin / 'media/Café 日本語 image.png').read_bytes(), raw)
                self.assertIn('Café 日本語 image.png', snapshot.textures)

    def test_existing_action_navigation_and_resource_reference_controls(self):
        for tag, value in [('onclick', 'RunScript(INERT)'), ('onright', 'RunAddon(INERT)'),
                           ('texture', '../escape.png'), ('texture', '/tmp/escape.png'),
                           ('texture', 'plugin://INERT/image.png'), ('texture', '$INFO[INERT].png'),
                           ('texture', 'missing.png'), ('label', '$INFO[INERT]'),
                           ('label', 'bad\x7f'),
                           ('width', '0'), ('width', '99999')]:
            with self.subTest(tag=tag, value=value):
                filename = 'script-tvguide-menu.xml' if tag == 'onright' else MAIN
                layout = self.original(filename)
                next(layout.iter(tag)).text = value
                self.save(layout, filename)
                with self.assertRaises(skin.SkinError):
                    self.prepare()

    def test_required_control_structure_and_type_cannot_change(self):
        for operation in ('remove', 'id', 'type'):
            with self.subTest(operation=operation):
                layout = self.original()
                controls = layout.find('controls')
                control = controls.find('control')
                if operation == 'remove':
                    controls.remove(control)
                else:
                    control.set(operation, 'INERT')
                self.save(layout)
                with self.assertRaisesRegex(skin.SkinError, 'control IDs/types'):
                    self.prepare()

    def test_source_change_after_read_does_not_change_loaded_bytes(self):
        self.save(self.original())
        read = skin._read
        def change_after(root, relative):
            raw = read(root, relative)
            if relative == '720p/' + MAIN:
                (root / relative).write_text('<window><onload>RunScript(INERT)</onload></window>')
            return raw
        with patch.object(skin, '_read', side_effect=change_after):
            snapshot = self.prepare()
        loaded = ET.tostring(self.loaded(snapshot))
        self.assertNotIn(b'INERT', loaded)
        self.assertIn('INERT', (self.layout / MAIN).read_text())
        with self.assertRaises(skin.SkinError):
            self.prepare()  # changed source is refused at the next opening

    def test_symlink_escape_and_changed_read_refused(self):
        target = self.root / 'outside.xml'
        target.write_bytes(ET.tostring(self.original()))
        (self.layout / MAIN).symlink_to(target)
        with self.assertRaisesRegex(skin.SkinError, 'Symlink'):
            self.prepare()
        (self.layout / MAIN).unlink()
        self.png()
        (self.media / 'mine.png').unlink()
        (self.media / 'mine.png').symlink_to(target)
        layout = self.original()
        next(layout.iter('texture')).text = 'mine.png'
        self.save(layout)
        with self.assertRaisesRegex(skin.SkinError, 'Symlink'):
            self.prepare()
        # Deliberately change the file between lstat and open; no unsafe data is
        # accepted just because the initial path check passed.
        real_open = os.open
        def change_open(path, flags):
            Path(path).write_bytes(b'changed')
            return real_open(path, flags)
        with patch.object(skin.os, 'open', side_effect=change_open):
            with self.assertRaisesRegex(skin.SkinError, 'source changed'):
                skin._read(self.layout, MAIN)

    def test_limits_encoding_and_decode_not_extension_only(self):
        for raw in (b'<window><!DOCTYPE x></window>',
                    b'<!DOCTYPE window [<!ENTITY x "INERT">]><window>&x;</window>',
                    b'<?INERT x?><window/>', b'\xff<window/>'):
            with self.subTest(raw=raw):
                with self.assertRaises(skin.SkinError):
                    skin._xml(raw)
        with self.assertRaisesRegex(skin.SkinError, '64 levels'):
            skin._xml(b'<window>' * 65 + b'</window>' * 65)
        self.save(self.original())
        for value in ('../Mine', '/Mine', 'Mine/Other', '..', 'Mine\\Other', 'Mine\x00', 'Mine\n', 'plugin:Mine'):
            with self.assertRaises(skin.SkinError):
                skin.prepare(str(ROOT), str(self.source), value, 'Default', str(self.root))
        for value in ('../bad.png', '/tmp/bad.png', 'a\\bad.png', 'plugin://bad.png',
                      'a/../bad.png', '%2e%2e/bad.png', '$INFO[x].png', 'bad\x00.png'):
            with self.assertRaises(skin.SkinError):
                skin._parts(value)
        for value in ('smb://INERT/share', 'https://INERT/', '//INERT/share', 'relative'):
            with self.assertRaises(skin.SkinError):
                skin.local_path(value)
        layout = self.original()
        next(layout.iter('texture')).text = 'mine.png'
        self.save(layout)
        (self.media / 'mine.png').write_bytes(b'NOT AN IMAGE')
        with self.assertRaises(skin.SkinError):
            self.prepare()
        (self.media / 'mine.png').write_bytes(b'x' * (skin.MAX_FILE + 1))
        with self.assertRaisesRegex(skin.SkinError, '4 MiB'):
            self.prepare()
        self.png()
        with patch.object(skin, 'MAX_TOTAL', 1):
            with self.assertRaisesRegex(skin.SkinError, '32 MiB'):
                self.prepare()

    def test_unrelated_code_include_and_resources_not_copied_or_loaded(self):
        (self.source / 'service.py').write_text('THIS IS INERT TEST DATA, NOT IMPORTABLE PYTHON')
        (self.layout / 'includes.xml').write_text('<includes><onload>INERT</onload></includes>')
        (self.media / 'unused.png').write_bytes(b'NOT AN IMAGE')
        snapshot = self.prepare()
        paths = list(Path(snapshot.path).rglob('*'))
        self.assertFalse(any(p.suffix == '.py' or p.name in ('includes.xml', 'unused.png') for p in paths))
        self.assertNotIn(b'INERT', ET.tostring(self.loaded(snapshot)))

    def test_adapter_opt_in_profile_folder_fallback_and_all_window_handoffs(self):
        # Extract only the adapter function. These are inert Python data/call
        # captures, NOT imported stubs, Kodi callbacks, or native acceptance.
        tree = ast.parse((ROOT / 'skin_runtime.py').read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'select_skin')
        calls = []
        namespace = {'BUNDLED': skin.BUNDLED, 'SkinError': skin.SkinError, 'prepare': skin.prepare,
                     'GUIDE_URL': 'https://github.com/kcook98765/script.tvguide.fullscreen/blob/preserve/custom-skins/docs/custom-guide-skins.md',
                     'xbmcvfs': SimpleNamespace(translatePath=lambda value: str(self.root) if value == 'special://temp/' else value),
                     'xbmcgui': SimpleNamespace(Dialog=lambda: SimpleNamespace(ok=lambda *args: calls.append(args)))}
        exec(compile(ast.Module(body=[function], type_ignores=[]), 'adapter-only', 'exec'), namespace)
        settings = {'skin': 'Default', 'skin.custom.enabled': 'false', 'skin.source': '1', 'skin.user': 'Mine'}
        addon = SimpleNamespace(getSetting=lambda key: settings.get(key, ''),
                                getAddonInfo=lambda key: str(ROOT) if key == 'path' else str(self.source))
        select = namespace['select_skin']
        self.assertEqual(select(addon), (str(ROOT), 'Default', {}, None))
        settings['skin.custom.enabled'] = 'true'
        settings['skin.source'] = '0'
        self.assertEqual(select(addon), (str(ROOT), 'Default', {}, None))
        self.assertEqual(calls, [])  # enabling + Bundled is legitimate, not an error
        settings['skin.source'] = '1'
        profile = select(addon)
        self.addCleanup(profile[3].directory.cleanup)
        self.assertNotEqual(profile[0], str(self.source))
        settings.update({'skin.source': '2', 'skin.folder': str(self.source)})
        folder = select(addon)
        self.addCleanup(folder[3].directory.cleanup)
        self.assertEqual(set(profile[2]), set(folder[2]))
        settings['skin.folder'] = ''
        self.assertEqual(select(addon), (str(ROOT), 'Default', {}, None))
        self.assertIn('local filesystem folder', calls[-1][1])
        settings['skin.folder'] = str(self.root / 'missing')
        self.assertEqual(select(addon), (str(ROOT), 'Default', {}, None))
        self.assertIn('Missing resources/skins', calls[-1][1])
        self.assertIn(namespace['GUIDE_URL'], calls[-1][1])
        self.assertNotIn('See docs/custom-guide-skins.md.', calls[-1][1])
        settings['skin.folder'] = str(self.source)
        gui_tree = ast.parse((ROOT / 'gui.py').read_text())
        helpers = [n for n in gui_tree.body if isinstance(n, ast.FunctionDef) and
                   n.name in ('skin_xml', 'skin_texture')]
        handoff = {'SKIN_XML': folder[2], '_SKIN_SNAPSHOT': folder[3]}
        exec(compile(ast.Module(body=helpers, type_ignores=[]), 'pure-skin-handoff', 'exec'), handoff)
        self.assertEqual(handoff['skin_xml'](MAIN), folder[2][MAIN])
        self.assertEqual(handoff['skin_texture']('tvg-program-nofocus.png'),
                         folder[3].textures['tvg-program-nofocus.png'])
        self.assertTrue(Path(handoff['skin_texture']('tvg-program-nofocus.png')).is_file())
        self.assertEqual(handoff['skin_texture']('https://INERT/art.png'), 'https://INERT/art.png')
        self.save(ET.fromstring('<window/>'))
        self.assertEqual(select(addon), (str(ROOT), 'Default', {}, None))
        self.assertIn('Using bundled Default. Originals are unchanged.', calls[-1][1])
        self.assertIn('control IDs/types', calls[-1][1])
        for file in ('gui.py', 'editor.py'):
            tree = ast.parse((ROOT / file).read_text(), feature_version=(3, 8))
            constructors = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and
                            isinstance(n.func, ast.Attribute) and n.func.attr == '__new__']
            self.assertTrue(constructors)
            for node in constructors:
                # Every active WindowXML constructor uses the snapshot mapping,
                # not a literal legacy filename or a user-selected source root.
                self.assertIsInstance(node.args[1], ast.Call)
                self.assertEqual([n.id for n in node.args[-2:]], ['SKIN_PATH', 'SKIN'])
        for file in ('custom_skin.py', 'skin_runtime.py'):
            source = (ROOT / file).read_text()
            ast.parse(source, feature_version=(3, 8))
            for newer in ('is_relative_to', 'removeprefix', 'removesuffix', 'follow_symlinks='):
                self.assertNotIn(newer, source)


if __name__ == '__main__':
    unittest.main(verbosity=2)
