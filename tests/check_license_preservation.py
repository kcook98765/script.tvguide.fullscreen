"""License/current inventory contracts and a separately frozen artwork-era delta."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_contract import (ARTWORK_COMMIT, entrypoint_notice, git_snapshot,
                              historical_payloads, OPTIONAL_PAYLOADS, pyaes_notice,
                              runtime, validate_payload_paths, validate_runtime_inventory)

ROOT = Path(__file__).resolve().parents[1]
BASE = 'c19f256333efbe7af12418312f17e00f99792dc2'
OMITTED = {'resources/screenshots/' + name for name in (
    'fullscreen-guide.png', 'programme-actions.png', 'on-now.png', 'search-results.png')}
CHANGED = {'addon.xml', 'changelog.txt', 'icon.png', 'fanart.jpg'}
NOTICE = 'THIRD-PARTY-NOTICES.txt'
COPYRIGHT = b'Copyright 2011 Raymond Hettinger'
PRIMARY_SHA256 = '0dfea32796792c994868b2cd531f017f2ee85d7852dd77dc41128640a7a9d4ef'
UPSTREAM = b'e6378c55515c45eb8eab07ca64c59ddefba9bf94'


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args],
                                   env={'PATH': os.defpath})


def validate_notice(raw):
    assert b'https://code.activestate.com/recipes/576693/' in raw
    assert UPSTREAM in raw and PRIMARY_SHA256.encode() in raw
    # Compare the complete primary copyright/permission/condition/disclaimer,
    # allowing only a single final LF added for the distributable text file.
    start = raw.index(COPYRIGHT)
    body = raw[start:]
    assert any(hashlib.sha256(b).hexdigest() == PRIMARY_SHA256
               for b in (body, body[:-1] if body.endswith(b'\n') else body))
    return body


def validate_gpl_pyaes(root):
    gpl = (root / 'LICENSE.txt').read_bytes()
    assert gpl == git('show', BASE + ':LICENSE.txt')
    assert b'GNU GENERAL PUBLIC LICENSE' in gpl and b'Version 2, June 1991' in gpl
    block = pyaes_notice((root / 'pyaes.py').read_bytes())
    assert block == pyaes_notice(git('show', BASE + ':pyaes.py'))
    assert b'Copyright (c) 2010 Marti Raudsepp <marti@juffo.org>' in block
    permission = block[block.index(b'# Permission'):]
    unwrapped = b' '.join(b' '.join(line.removeprefix(b'#').split())
                          for line in permission.splitlines()).split()
    notice = (root / NOTICE).read_bytes()
    assert notice == git('show', BASE + ':' + NOTICE)
    body = validate_notice(notice)
    assert unwrapped == body[body.index(b'Permission'):].split()


def validate_entrypoint_headers(root):
    for path in ('addon.py', 'service.py'):
        assert entrypoint_notice((root / path).read_bytes()) == entrypoint_notice(
            git('show', BASE + ':' + path)), path


class LicensePreservationTests(unittest.TestCase):
    def test_full_primary_notice_and_provenance(self):
        raw = (ROOT / NOTICE).read_bytes()
        validate_notice(raw)
        self.assertEqual(raw, git('show', BASE + ':' + NOTICE))

    def test_current_runtime_inventory_and_package_safety(self):
        paths = validate_runtime_inventory(ROOT)
        self.assertEqual(len(historical_payloads()), 318)
        self.assertEqual(len(paths - OPTIONAL_PAYLOADS), 318)

    def test_inventory_negative_controls_and_reviewed_favourites_allowance(self):
        required = historical_payloads()
        for extra in ('unrelated.py', 'resources/private-settings.json', 'docs/report.md',
                      'tests/check_artwork.py', '../addon.py', '/addon.py',
                      'resources/../secret', 'resources\\secret', 'C:/secret'):
            with self.subTest(extra=extra), self.assertRaises(AssertionError):
                validate_payload_paths([*required, extra])
        with self.assertRaises(AssertionError):
            validate_payload_paths(required - {'gui.py'})
        with self.assertRaises(AssertionError):
            validate_payload_paths([*required, 'addon.py'])
        validate_payload_paths(required | {'favourites_navigation.py'})
        with self.assertRaises(AssertionError):
            validate_payload_paths(required | {'favourites_navigation_debug.py'})

    def test_filesystem_inventory_controls_do_not_freeze_runtime_bytes(self):
        # A tiny fixture exercises the actual filesystem scanner, not a second
        # permissive model of it. The real 318-member inventory is tested above.
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as directory:
            root = Path(directory)
            (root / 'resources').mkdir()
            (root / 'gui.py').write_text('pass\n')
            with patch('package_contract.historical_payloads', return_value={'gui.py'}):
                validate_runtime_inventory(root)
                (root / 'gui.py').write_text('# legitimate implementation change\npass\n')
                validate_runtime_inventory(root)
                for extra in ('unrelated.py', 'resources/debug.json', 'favourites_navigation.py'):
                    with self.subTest(extra=extra):
                        path = root / extra
                        path.write_bytes(b'')
                        with self.assertRaises(AssertionError):
                            validate_runtime_inventory(root)
                        path.write_bytes(b'pass\n')
                        if extra == 'favourites_navigation.py':
                            validate_runtime_inventory(root)
                            (root / 'gui.py').write_text('import favourites_navigation\n')
                            validate_runtime_inventory(root)
                        else:
                            with self.assertRaises(AssertionError):
                                validate_runtime_inventory(root)
                        path.unlink()
                        if extra == 'favourites_navigation.py':
                            with self.assertRaises(AssertionError):
                                validate_runtime_inventory(root)
                            (root / 'gui.py').write_text('pass\n')
                (root / 'resources/link').symlink_to(root / 'gui.py')
                with self.assertRaises(AssertionError):
                    validate_runtime_inventory(root)

    def test_gpl_and_distinct_pyaes_full_mit_notice_preserved(self):
        validate_gpl_pyaes(ROOT)

    def test_source_caches_are_not_package_candidates(self):
        from unittest.mock import patch
        cache_paths = (
            '__pycache__/gui.cpython-312.pyc', 'gui.pyc',
            'resources/__pycache__/__init__.cpython-312.pyc',
            'resources/lib/legacy.pyo',
            'resources/.pytest_cache/v/cache/nodeids',
            'resources/.mypy_cache/generated.py',
            'resources/.ruff_cache/cache', 'resources/.cache/generated.py',
        )
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as directory:
            root = Path(directory)
            (root / 'resources').mkdir()
            (root / 'gui.py').write_text('pass\n')
            for name in cache_paths:
                file = root / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(b'\x00generated cache, not runtime Python')
            with patch('package_contract.historical_payloads', return_value={'gui.py'}):
                self.assertEqual(validate_runtime_inventory(root), {'gui.py'})
                for name in cache_paths:
                    with self.subTest(packaged=name), self.assertRaises(AssertionError):
                        validate_payload_paths(['gui.py', name])
                    # Even an explicit inventory declaration cannot bless caches.
                    with self.subTest(declared=name), self.assertRaises(AssertionError):
                        validate_payload_paths([name], required={name})
                # Real extra resources alongside ignored caches must still fail.
                (root / 'resources/unrelated.json').write_text('{}')
                with self.assertRaises(AssertionError):
                    validate_runtime_inventory(root)

    def test_original_entrypoint_attributions_and_gpl_headers(self):
        validate_entrypoint_headers(ROOT)

    def test_license_and_attribution_damage_controls_allow_code_evolution(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as directory:
            root = Path(directory)
            for path in ('LICENSE.txt', NOTICE, 'pyaes.py', 'addon.py', 'service.py'):
                shutil.copyfile(ROOT / path, root / path)
            for path, before, after, check in (
                    ('LICENSE.txt', b'June 1991', b'Other', validate_gpl_pyaes),
                    (NOTICE, COPYRIGHT, b'Other', validate_gpl_pyaes),
                    ('pyaes.py', b'Marti Raudsepp', b'Other', validate_gpl_pyaes),
                    ('pyaes.py', b'# THE SOFTWARE IS PROVIDED', b'# removed', validate_gpl_pyaes),
                    ('addon.py', b'Tommy Winther', b'Other', validate_entrypoint_headers),
                    ('service.py', b'Thomas Geppert', b'Other', validate_entrypoint_headers),
                    ('service.py', b'#  any later version.', b'# removed', validate_entrypoint_headers)):
                file = root / path
                raw = file.read_bytes()
                self.assertIn(before, raw)
                file.write_bytes(raw.replace(before, after))
                with self.subTest(damaged=path, clause=before), self.assertRaises(AssertionError):
                    check(root)
                file.write_bytes(raw)
            # Changes after the original legal blocks are deliberately not frozen.
            for path in ('pyaes.py', 'addon.py', 'service.py'):
                file = root / path
                file.write_bytes(file.read_bytes() + b'\n# legitimate implementation change\n')
            validate_gpl_pyaes(root)
            validate_entrypoint_headers(root)

    def test_notice_loss_and_truncation_negative_controls(self):
        raw = (ROOT / NOTICE).read_bytes()
        for bad in (b'', raw.replace(COPYRIGHT, b'Copyright 2010 Other'),
                    raw.replace(b'The above copyright notice', b'The copyright notice'),
                    raw.split(b'THE SOFTWARE IS PROVIDED')[0],
                    raw.replace(UPSTREAM, b'unpinned')):
            with self.subTest(sha256=hashlib.sha256(bad).hexdigest()):
                with self.assertRaises((AssertionError, ValueError)):
                    validate_notice(bad)
        print('Notice negative controls rejected: attribution, permission, disclaimer, provenance')


class HistoricalPayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fixture = git_snapshot(ARTWORK_COMMIT)
        cls.root = fixture.__enter__()
        cls.addClassCleanup(fixture.__exit__, None, None, None)

    def test_exact_318_payload_delta_and_45_python_files_unchanged(self):
        paths = git('ls-tree', '-r', '--name-only', BASE).decode().splitlines()
        paths = [p for p in paths if runtime(p)]
        self.assertEqual(len(paths), 322)
        self.assertEqual(sum(p.endswith('.py') for p in paths), 45)
        for path in sorted(set(paths) - OMITTED - CHANGED):
            with self.subTest(path=path):
                self.assertEqual((self.root / path).read_bytes(), git('show', BASE + ':' + path))
        for path in OMITTED:
            self.assertIn(path, paths)
            self.assertFalse((self.root / path).exists())
        for path in CHANGED:
            self.assertNotEqual((self.root / path).read_bytes(), git('show', BASE + ':' + path))
        current = [p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file()]
        payloads = {p for p in current if runtime(p)}
        self.assertEqual(payloads, set(paths) - OMITTED)
        self.assertEqual(len(payloads), 318)
        self.assertEqual(sum(p.endswith('.py') for p in payloads), 45)
        print('Exact delta: 322 - 4 = 318 payloads; four changed payloads; 314 unchanged including all 45 Python files')


if __name__ == '__main__':
    unittest.main(verbosity=2)
