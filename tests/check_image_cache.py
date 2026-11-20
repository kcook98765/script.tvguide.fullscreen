"""Pure helper + real AST caller captures; no Kodi/stub/legacy host imports."""
import ast
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('image_cache', ROOT / 'image_cache.py')
cache = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cache)

VALUES = ["Doctor's diary", 'News, Weather & Sport (1999)', 'Café — 日本語 📺',
          'He said "Hello"\t\n\r', r'C:\Kodi\art\poster.png',
          '../not-a-filename,RunScript(INERT_MARKER)']


def tree(name):
    return ast.parse((ROOT / name).read_text(encoding='utf-8'), filename=name)


def execute(nodes, scope):
    module = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    exec(compile(module, '<actual-cache-caller>', 'exec'), scope)


class ImageMatches(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='tvguide-image-test-')
        self.addCleanup(self.temp.cleanup)
        # Resolve platform temp aliases for these positive local-path tests.
        self.profile = Path(self.temp.name).resolve()
        self.path = self.profile / cache.FILENAME
        self.store = cache.ImageCache(str(self.profile))

    def reload(self):
        return cache.ImageCache(str(self.profile))

    def test_roundtrip_exact_strings_and_no_dispatch(self):
        for i, title in enumerate(VALUES):
            self.store[title] = VALUES[-i - 1]
        self.store['empty miss/deletion'] = ''
        rebuilt = self.reload()
        for i, title in enumerate(VALUES):
            self.assertEqual(rebuilt[title], VALUES[-i - 1])
        self.assertEqual(rebuilt['empty miss/deletion'], '')
        self.assertEqual(set(p.name for p in self.profile.iterdir()), {cache.FILENAME})
        self.assertIn('日本語', self.path.read_text(encoding='utf-8'))

    def test_update_delete_clear_persist(self):
        self.store['title'] = 'special://profile/art.png'
        self.store['title'] = 'image://encoded-local-art/'
        self.assertEqual(self.reload()['title'], 'image://encoded-local-art/')
        del self.store['title']
        self.assertNotIn('title', self.reload())
        self.store['title'] = 'tvg-tv.png'
        self.assertTrue(self.store.clear())
        self.assertNotIn('title', self.reload())
        self.assertEqual(json.loads(self.path.read_text())['entries'], {})

    def test_legacy_and_unrelated_files_never_opened_or_changed(self):
        untouched = {'tvdb.pickle': b'INERT OLD PICKLE DATA',
                     'tvdb_banners.pickle': b'INERT BANNERS', 'user.json': b'USER DATA'}
        for name, raw in untouched.items():
            (self.profile / name).write_bytes(raw)
        opened = []
        real_open = os.open

        def observe(path, *args, **kwargs):
            opened.append(os.fspath(path))
            return real_open(path, *args, **kwargs)

        with patch.object(cache.os, 'open', side_effect=observe):
            store = self.reload()
            store['normal'] = 'normal.png'
            store = self.reload()
            store.clear()
        self.assertTrue(opened)
        self.assertFalse(any(name in path for name in untouched for path in opened))
        for name, raw in untouched.items():
            self.assertEqual((self.profile / name).read_bytes(), raw)

    def test_malformed_schema_size_and_depth_rebuild(self):
        bad = [b'\xff', b'{broken', b'[]', b'null', b'[' * 2000 + b']' * 2000,
               b'x' * (cache.MAX_BYTES + 1), b'{"version":' + b'9' * 20000 + b',"entries":{}}']
        for value in [dict(version=True, entries={}), dict(version=2, entries={}),
                      dict(version=1, entries=[]), dict(version=1, entries={'x': 1}),
                      dict(version=1, entries={'x': None}),
                      dict(version=1, entries={'x': float('nan')}),
                      dict(version=1, entries={'x': {'__reduce__': 'INERT'}}),
                      dict(version=1, entries={'x': '\ud800'}),
                      dict(version=1, entries={'x' * (cache.MAX_TITLE + 1): ''}),
                      dict(version=1, entries={'x': 'y' * (cache.MAX_IMAGE + 1)}),
                      dict(version=1, entries={str(i): '' for i in range(cache.MAX_ENTRIES + 1)}),
                      dict(version=1, entries={}, extra='not schema')]:
            bad.append(json.dumps(value).encode('utf-8'))
        for raw in bad:
            with self.subTest(size=len(raw)):
                self.path.write_bytes(raw)
                store = self.reload()
                self.assertNotIn('x', store)
                store['rebuilt'] = 'safe.png'
                self.assertEqual(self.reload()['rebuilt'], 'safe.png')

    def test_bounds_on_writes_and_encoded_resource_size(self):
        for title, value in [(None, 'x'), ('x', 1), ('x', None), ('x', []),
                             ('x' * (cache.MAX_TITLE + 1), ''),
                             ('x', 'y' * (cache.MAX_IMAGE + 1)), ('x', '\ud800')]:
            self.store[title] = value
        self.assertFalse(self.path.exists())
        with patch.object(cache, 'MAX_ENTRIES', 2):
            self.store['one'] = '1'
            self.store['two'] = '2'
            self.store['overflow'] = '3'
            self.store['one'] = 'updated'
            self.assertNotIn('overflow', self.store)
            self.assertEqual(self.reload()['one'], 'updated')
        old = self.path.read_bytes()
        with patch.object(cache, 'MAX_BYTES', len(old) + 1):
            self.store['encoded-overflow'] = '\x00' * 100
        self.assertEqual(self.path.read_bytes(), old)
        self.assertNotIn('encoded-overflow', self.store)

    def test_oversized_file_rejected_before_open_and_failed_write_cleanup(self):
        self.path.write_bytes(b'x' * (cache.MAX_BYTES + 1))
        with patch.object(cache.os, 'open', side_effect=AssertionError('must not open oversized data')):
            self.assertNotIn('title', self.reload())
        self.store['old'] = 'old.png'
        previous = self.path.read_bytes()
        real_fdopen = os.fdopen

        class FailedWriter:
            def __init__(self, fd, mode):
                self.stream = real_fdopen(fd, mode)

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.stream.close()

            def write(self, raw):
                self.stream.write(raw[:10])
                raise OSError('inert partial-write failure')

        with patch.object(cache.os, 'fdopen', side_effect=FailedWriter):
            self.store['new'] = 'new.png'
        self.assertEqual(self.store['new'], 'new.png')
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(list(self.profile.glob('.image-matches-*.tmp')), [])

    def test_missing_nonlocal_and_nonregular_paths(self):
        for profile in ['', 'relative', 'special://profile/', 'https://example.invalid/',
                        str(self.profile / 'missing'), None]:
            store = cache.ImageCache(profile)
            store['title'] = 'still available in memory'
            self.assertEqual(store['title'], 'still available in memory')
            self.assertFalse(store.clear())
        self.path.mkdir()
        self.reload()['title'] = 'normal.png'
        self.assertTrue(self.path.is_dir())
        self.path.rmdir()
        if hasattr(os, 'mkfifo'):
            os.mkfifo(self.path)
            self.assertNotIn('title', self.reload())
            self.reload()['title'] = 'normal.png'
            self.assertTrue(self.path.is_fifo())

    def test_symlink_and_hardlink_do_not_overwrite_targets(self):
        target = self.profile / 'unrelated'
        target.write_bytes(b'UNTOUCHED')
        self.path.symlink_to(target)
        store = self.reload()
        self.assertNotIn('title', store)
        store['title'] = 'image.png'
        self.assertFalse(store.clear())
        self.assertEqual(target.read_bytes(), b'UNTOUCHED')
        self.path.unlink()
        os.link(target, self.path)
        self.reload()['title'] = 'image.png'
        self.assertEqual(target.read_bytes(), b'UNTOUCHED')
        alias = self.profile / 'alias'
        alias.symlink_to(self.profile, target_is_directory=True)
        store = cache.ImageCache(str(alias))
        store['blocked'] = 'image.png'
        self.assertFalse(store.clear())
        self.assertNotIn('blocked', self.reload())

    def test_io_errors_keep_operation_and_previous_complete_file(self):
        self.store['old'] = 'old.png'
        previous = self.path.read_bytes()
        for method in ['mkstemp', 'fsync', 'replace']:
            owner = cache.tempfile if method == 'mkstemp' else cache.os
            with patch.object(owner, method, side_effect=OSError('inert I/O error')):
                self.store['new'] = 'new.png'
                self.assertEqual(self.store['new'], 'new.png')
                self.assertEqual(self.path.read_bytes(), previous)
                self.assertFalse(self.store.clear())
                self.assertNotIn('new', self.store)
            self.assertEqual(list(self.profile.glob('.image-matches-*.tmp')), [])
        with patch.object(cache.os, 'open', side_effect=PermissionError('inert')):
            self.assertNotIn('old', self.reload())

    def test_atomic_replace_and_lookup_threads(self):
        self.store['old'] = 'old.png'
        previous = self.path.read_bytes()
        real_replace = os.replace
        replacements = []

        def observe(src, dst):
            self.assertEqual(Path(src).parent, self.profile)
            self.assertEqual(Path(dst), self.path)
            json.loads(Path(src).read_text(encoding='utf-8'))
            if not replacements:
                self.assertEqual(self.path.read_bytes(), previous)
            replacements.append(src)
            real_replace(src, dst)

        with patch.object(cache.os, 'replace', side_effect=observe):
            with ThreadPoolExecutor(max_workers=6) as pool:
                list(pool.map(lambda i: self.store.__setitem__(str(i), 'image%d.png' % i), range(40)))
        rebuilt = self.reload()
        for i in range(40):
            self.assertEqual(rebuilt[str(i)], 'image%d.png' % i)
        self.assertEqual(len(replacements), 40)
        self.assertEqual(list(self.profile.glob('.image-matches-*.tmp')), [])

    def test_real_guide_constructor_writes_delete_and_consumers(self):
        gui = tree('gui.py')
        guide = next(n for n in gui.body if isinstance(n, ast.ClassDef) and n.name == 'TVGuide')
        assignments = [n for n in ast.walk(guide) if isinstance(n, ast.Assign) and
                       isinstance(n.targets[0], ast.Attribute) and n.targets[0].attr == 'tvdb_urls']
        self.assertEqual(len(assignments), 1)
        addon = SimpleNamespace(getAddonInfo=lambda key: str(self.profile) if key == 'profile' else None)
        translate = SimpleNamespace(translatePath=lambda path: path)
        obj = SimpleNamespace(C_MAIN_IMAGE=1)
        scope = dict(self=obj, ADDON=addon, xbmcvfs=translate, ImageCache=cache.ImageCache)
        execute(assignments, scope)
        writes = [n for n in ast.walk(guide) if isinstance(n, ast.Assign) and
                  isinstance(n.targets[0], ast.Subscript) and
                  isinstance(n.targets[0].value, ast.Attribute) and n.targets[0].value.attr == 'tvdb_urls']
        self.assertEqual(len(writes), 4)
        program = SimpleNamespace(title=VALUES[0])
        scope.update(program=program, program_title=program.title, title=program.title,
                     orig_title=program.title, img=VALUES[2], tvdb_url=VALUES[2])
        for node in writes:
            if isinstance(node.value, ast.Name):
                execute([node], scope)
                rebuilt = SimpleNamespace()
                execute(assignments, dict(scope, self=rebuilt))
                self.assertEqual(rebuilt.tvdb_urls[program.title], VALUES[2])
        # Real delete branch keeps its empty-string suppression across rebuild.
        branch = next(n for n in ast.walk(guide) if isinstance(n, ast.If) and
                      'COMMAND_ACTIONS[\'DELETE_PROGRAM_IMAGE\']' in ast.unparse(n.test))
        obj._getProgramFromControl = lambda control: program
        calls = []
        obj.setControlImage = lambda *args: calls.append(args)
        execute(branch.body, dict(scope, controlInFocus=object()))
        self.assertEqual(calls, [(1, '')])
        self.assertEqual(self.reload()[program.title], '')
        # Cached context artwork fills only an absent XMLTV small image.
        context = next(n for n in ast.walk(guide) if isinstance(n, ast.FunctionDef) and n.name == '_showContextMenu')
        use = next(n for n in context.body if isinstance(n, ast.If) and 'tvdb_urls' in ast.unparse(n.test))
        obj.tvdb_urls[program.title] = 'cached.png'
        for original, expected in [('', 'cached.png'), ('xmltv.png', 'xmltv.png')]:
            program.imageSmall = original
            execute([use], scope)
            self.assertEqual(program.imageSmall, expected)

    def test_real_reset_modes_clear_only_json(self):
        reset = tree('ResetDatabase.py')
        clear = next(n for n in reset.body if isinstance(n, ast.FunctionDef) and n.name == 'clearImageCache')
        logs = []
        scope = dict(ImageCache=cache.ImageCache,
                     xbmcaddon=SimpleNamespace(Addon=lambda **kw: SimpleNamespace(getAddonInfo=lambda key: str(self.profile))),
                     xbmcvfs=SimpleNamespace(translatePath=lambda path: path),
                     xbmc=SimpleNamespace(log=lambda *args: logs.append(args), LOGWARNING=2))
        execute([clear], scope)
        # Both maintenance modes call the actual helper; do not execute unrelated reset operations.
        main = next(n for n in reset.body if isinstance(n, ast.If) and '__name__' in ast.unparse(n.test))
        calls = [n for n in ast.walk(main) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                 and isinstance(n.value.func, ast.Name) and n.value.func.id == 'clearImageCache']
        self.assertEqual(len(calls), 2)
        modes = [ast.unparse(n.test) for n in ast.walk(main) if isinstance(n, ast.If) and
                 any(call in n.body for call in calls)]
        self.assertEqual(sorted(modes), ['mode == 2', 'mode == 3'])
        for call in calls:
            self.store['title'] = 'image.png'
            execute([call], scope)
            self.assertNotIn('title', self.reload())
        self.assertFalse(logs)
        with patch.object(cache.os, 'replace', side_effect=OSError('inert clear error')):
            scope['clearImageCache']()
        self.assertEqual(len(logs), 1)
        self.assertNotIn('.pickle', ast.unparse(reset))


if __name__ == '__main__':
    unittest.main(verbosity=2)
