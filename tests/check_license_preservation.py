"""Exact artwork-successor delta; no add-on imports, native access or downloads."""
import hashlib
import os
from pathlib import Path
import subprocess
import unittest

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


def runtime(path):
    return path.startswith('resources/') or ('/' not in path and (
        path.endswith('.py') or path in ('addon.xml', 'changelog.txt', 'commands.txt',
                                        'LICENSE.txt', 'icon.png', 'fanart.jpg', NOTICE)))


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


class LicensePreservationTests(unittest.TestCase):
    def test_full_primary_notice_and_provenance(self):
        validate_notice((ROOT / NOTICE).read_bytes())

    def test_exact_318_payload_delta_and_45_python_files_unchanged(self):
        paths = git('ls-tree', '-r', '--name-only', BASE).decode().splitlines()
        paths = [p for p in paths if runtime(p)]
        self.assertEqual(len(paths), 322)
        self.assertEqual(sum(p.endswith('.py') for p in paths), 45)
        for path in sorted(set(paths) - OMITTED - CHANGED):
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_bytes(), git('show', BASE + ':' + path))
        for path in OMITTED:
            self.assertIn(path, paths)
            self.assertFalse((ROOT / path).exists())
        for path in CHANGED:
            self.assertNotEqual((ROOT / path).read_bytes(), git('show', BASE + ':' + path))
        current = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()]
        payloads = {p for p in current if runtime(p)}
        self.assertEqual(payloads, set(paths) - OMITTED)
        self.assertEqual(len(payloads), 318)
        self.assertEqual(sum(p.endswith('.py') for p in payloads), 45)
        print('Exact delta: 322 - 4 = 318 payloads; four changed payloads; 314 unchanged including all 45 Python files')

    def test_gpl_and_distinct_pyaes_full_mit_notice_preserved(self):
        gpl = (ROOT / 'LICENSE.txt').read_bytes()
        self.assertEqual(gpl, git('show', BASE + ':LICENSE.txt'))
        self.assertIn(b'GNU GENERAL PUBLIC LICENSE', gpl)
        self.assertIn(b'Version 2, June 1991', gpl)
        pyaes = (ROOT / 'pyaes.py').read_bytes()
        self.assertEqual(pyaes, git('show', BASE + ':pyaes.py'))
        self.assertIn(b'Copyright (c) 2010 Marti Raudsepp <marti@juffo.org>', pyaes)
        block = pyaes.split(b'####')[1]
        permission = block[block.index(b'# Permission'):]
        unwrapped = b' '.join(b' '.join(line.removeprefix(b'#').split())
                              for line in permission.splitlines()).split()
        body = validate_notice((ROOT / NOTICE).read_bytes())
        self.assertEqual(unwrapped, body[body.index(b'Permission'):].split())

    def test_notice_loss_and_truncation_negative_controls(self):
        raw = (ROOT / NOTICE).read_bytes()
        for bad in (b'', raw.replace(COPYRIGHT, b'Copyright 2010 Other'),
                    raw.replace(b'The above copyright notice', b'The copyright notice'),
                    raw.split(b'THE SOFTWARE IS PROVIDED')[0],
                    raw.replace(UPSTREAM, b'unpinned')):
            with self.subTest(sha256=hashlib.sha256(bad).hexdigest()):
                with self.assertRaises((AssertionError, ValueError)):
                    validate_notice(bad)
        print('Notice negative controls rejected: missing, wrong attribution, changed condition, truncated disclaimer, unpinned provenance')


if __name__ == '__main__':
    unittest.main(verbosity=2)
