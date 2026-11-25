"""Actual XMLTV fetch path with synthetic files and explicit Kodi/network fakes."""
import ast
from contextlib import nullcontext
import datetime
import gzip
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import sqlite3
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
A = (b'<tv><channel id="a"><display-name>A</display-name></channel>'
     b'<programme channel="a" start="20261120120000 +0000" stop="20261120123000 +0000">'
     b'<title>A</title><desc>Fixture</desc></programme></tv>')
B = A.replace(b'id="a"', b'id="b"').replace(b'channel="a"', b'channel="b"').replace(b'>A<', b'>B<')


def extract(path, name, env, methods=None):
    tree = ast.parse((ROOT / path).read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
    if methods is not None:
        cls.bases = []
        cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in methods]
    exec(compile(ast.Module(body=[cls], type_ignores=[]), path, 'exec'), env)
    return env[name]


class VFSFile:
    def __init__(self, path, mode='r'):
        self.file = open(path, mode) if 'w' in mode or os.path.exists(path) else None

    def read(self):
        data = self.file.read() if self.file else ''
        return data.decode() if isinstance(data, bytes) else data

    def readBytes(self, size=-1):
        return self.file.read(size) if self.file else b''

    def size(self):
        return os.fstat(self.file.fileno()).st_size

    def write(self, data):
        if 'b' in self.file.mode and isinstance(data, str):
            data = data.encode()
        self.file.write(data)
        self.file.flush()
        return True

    def close(self):
        if self.file:
            self.file.close()

    def __del__(self):
        self.close()


class SourceCache(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.profile = Path(self.tmp.name)
        self.cache = self.profile / 'xmltv.xml'
        self.settings = {'xmltv.interval': '2', 'xmltv.refresh': 'false'}
        self.addon = SimpleNamespace(getSetting=lambda key: self.settings.get(key, ''))
        self.requests = SimpleNamespace(get=Mock(side_effect=self.download), codes=SimpleNamespace(ok=200))
        self.payload = A
        self.status = 200
        self.copy = Mock(side_effect=self.copy_file)
        vfs = SimpleNamespace(
            translatePath=lambda path: str(self.profile), exists=os.path.exists,
            File=VFSFile, copy=self.copy, delete=lambda path: os.remove(path),
            Stat=lambda path: SimpleNamespace(st_mtime=lambda: os.path.getmtime(path)))
        self.env = dict(os=os, datetime=datetime, time=time, gzip=gzip, hashlib=hashlib, uuid=uuid,
                        sqlite3=sqlite3, ElementTree=ET, re=re, json=json,
                        requests=self.requests, ADDON=self.addon, xbmcvfs=vfs,
                        xbmc=SimpleNamespace(log=Mock(), LOGDEBUG=0, LOGERROR=4),
                        xbmcgui=SimpleNamespace(Dialog=Mock(), DialogProgressBG=Mock(),
                                                NOTIFICATION_ERROR='error'))
        self.fetcher = extract('fileFetcher.py', 'FileFetcher', self.env)
        self.env['FileFetcher'] = self.fetcher
        for name in ('Channel', 'Program'):
            extract('utils.py', name, self.env)
        extract('source.py', 'FileWrapper', self.env)
        self.source_cls = extract('source.py', 'XMLTVSource', self.env, {
            'updateLocalFile', 'validateLocalFile', 'parseXMLTV', 'parseXMLTVDate'})
        self.source_cls.LOGO_SOURCE_FOLDER = 1
        self.source_cls.PLUGIN_DATA = str(self.profile)
        self.source = self.source_cls()
        self.source.needReset = False
        self.env.update(strings=lambda key: 'Fetch error', FETCH_ERROR_TITLE=0,
                        FETCH_ERROR_LINE1=1, FETCH_ERROR_LINE2=2)

    def copy_file(self, source, target):
        shutil.copyfile(source, target)
        return True

    def download(self, url, **kwargs):
        return SimpleNamespace(status_code=self.status, headers={},
                               text=hashlib.md5(self.payload).hexdigest(),
                               iter_content=lambda size: iter([self.payload]))

    def fetch(self, url, force=False):
        self.source.needReset = False
        self.source.updateLocalFile('xmltv.xml', url, self.addon, force=force)

    def test_fresh_remote_cache_switches_source_before_interval(self):
        self.fetch('https://example.invalid/a.xml')
        self.assertEqual(self.cache.read_bytes(), A)
        self.payload = B
        self.fetch('https://example.invalid/b.xml')
        self.assertEqual(self.cache.read_bytes(), B)
        self.assertTrue(self.source.needReset)
        self.assertEqual(self.requests.get.call_count, 2)

    def test_fetcher_visible_diagnostics_never_include_source_secrets(self):
        secret = 'SYNTHETIC_SECRET_85'
        vfs_url = 'smb://user:' + secret + '@host/private/' + secret + '.xml'
        http_url = 'https://user:' + secret + '@example.invalid/feed.xml?signature=' + secret
        gui = self.env['xbmcgui']
        logger = self.env['xbmc'].log
        for operation in ('vfs-ok', 'vfs-false', 'vfs-exception', 'http-ok',
                          'http-status', 'http-gz-status', 'http-exception',
                          'http-stream-exception', 'md5-exception', 'md5-mismatch'):
            with self.subTest(operation=operation):
                logger.reset_mock()
                gui.Dialog.reset_mock()
                gui.DialogProgressBG.reset_mock()
                self.settings['gz'] = 'true' if operation == 'http-gz-status' else 'false'
                self.settings['md5'] = 'true' if operation.startswith('md5-') else 'false'
                self.status = 503 if operation.endswith('status') else 200
                self.requests.get.side_effect = self.download
                self.copy.side_effect = lambda source, target: Path(target).write_bytes(A) > 0
                expected = self.fetcher.FETCH_OK
                if operation == 'vfs-false':
                    self.copy.side_effect = None
                    self.copy.return_value = False
                    expected = self.fetcher.FETCH_ERROR
                elif operation == 'vfs-exception':
                    self.copy.side_effect = OSError(vfs_url)
                    expected = self.fetcher.FETCH_ERROR
                elif operation == 'http-exception':
                    self.requests.get.side_effect = OSError(http_url)
                    expected = self.fetcher.FETCH_NOT_NEEDED
                elif operation == 'http-stream-exception':
                    response = self.download(http_url)
                    response.iter_content = Mock(side_effect=OSError(http_url))
                    self.requests.get.side_effect = None
                    self.requests.get.return_value = response
                    expected = self.fetcher.FETCH_ERROR
                elif operation == 'http-status':
                    expected = self.fetcher.FETCH_NOT_NEEDED
                elif operation == 'http-gz-status':
                    expected = self.fetcher.FETCH_ERROR
                elif operation == 'md5-exception':
                    self.requests.get.side_effect = [OSError(http_url), self.download(http_url)]
                elif operation == 'md5-mismatch':
                    response = self.download(http_url)
                    response.text = secret  # Untrusted remote MD5 body, not a digest.
                    response.headers = {'X-Secret': secret}
                    self.requests.get.side_effect = None
                    self.requests.get.return_value = response
                    expected = self.fetcher.FETCH_ERROR
                url = vfs_url if operation.startswith('vfs-') else http_url
                # The destination directory is sensitive too, even on success.
                destination = self.profile / secret / 'xmltv.xml'
                destination.parent.mkdir(exist_ok=True)
                fetcher = self.fetcher(url, str(destination), self.addon, track_source=True)
                self.assertEqual(fetcher.fetchFile(force=True), expected)
                visible = repr((logger.mock_calls, gui.Dialog.mock_calls,
                                gui.DialogProgressBG.mock_calls))
                self.assertNotIn(secret, visible)
                self.assertNotIn('example.invalid', visible)
                self.assertNotIn(str(self.profile), visible)
                self.assertIn('xmltv.xml', visible)
                gui.Dialog.return_value.ok.assert_not_called()
                if operation.endswith('status'):
                    self.assertIn('503', visible)
                if operation in ('http-ok', 'md5-exception', 'md5-mismatch'):
                    gui.DialogProgressBG.return_value.create.assert_called_once_with(
                        'TV Guide Fullscreen', 'downloading xmltv.xml')
                retry = Path(str(destination) + '.retry')
                self.assertEqual(retry.exists(), not operation.startswith('vfs-') and
                                 expected != self.fetcher.FETCH_OK)
                retry.unlink(missing_ok=True)

    def test_fetcher_unknown_destination_name_is_not_a_diagnostic_slot(self):
        secret = 'SYNTHETIC_SECRET_85'
        fetcher = self.fetcher('https://example.invalid/feed?secret=' + secret,
                               str(self.profile / secret), self.addon)
        self.assertEqual(fetcher.fetchFile(force=True), self.fetcher.FETCH_OK)
        visible = repr((self.env['xbmc'].log.mock_calls,
                        self.env['xbmcgui'].DialogProgressBG.mock_calls))
        self.assertNotIn(secret, visible)
        self.assertIn('cache file', visible)

    def test_fresh_local_cache_switches_to_older_file(self):
        first, second = self.profile / 'a.xml', self.profile / 'b.xml'
        first.write_bytes(A)
        second.write_bytes(B)
        os.utime(second, (1, 1))
        self.fetch(str(first))
        self.fetch(str(second))
        self.assertEqual(self.cache.read_bytes(), B)
        self.assertTrue(self.source.needReset)

    def test_local_to_remote_switch_ignores_fresh_cache(self):
        local = self.profile / 'a.xml'
        local.write_bytes(A)
        self.fetch(str(local))
        self.payload = B
        self.fetch('https://example.invalid/b.xml')
        self.assertEqual(self.cache.read_bytes(), B)
        self.assertTrue(self.source.needReset)

    def test_other_fetcher_callers_do_not_opt_into_source_tracking(self):
        self.cache.write_bytes(A)
        fetcher = self.fetcher('https://example.invalid/b.xml', str(self.cache), self.addon)
        self.assertEqual(fetcher.fetchFile(), fetcher.FETCH_NOT_NEEDED)
        self.requests.get.assert_not_called()
        self.assertFalse(self.cache.with_suffix('.xml.source').exists())

    def test_http_failure_outcomes_keep_notifications_nonblocking_and_retry_scoped(self):
        for tracked in (False, True):
            for failure in ('status', 'request', 'gz-status'):
                with self.subTest(tracked=tracked, failure=failure):
                    self.settings['gz'] = 'true' if failure == 'gz-status' else 'false'
                    self.status = 503
                    self.requests.get.side_effect = (OSError('offline') if failure == 'request'
                                                     else self.download)
                    self.env['xbmcgui'].Dialog.reset_mock()
                    retry = Path(str(self.cache) + '.retry')
                    retry.unlink(missing_ok=True)
                    fetcher = self.fetcher('https://example.invalid/a.xml', str(self.cache),
                                           self.addon, track_source=tracked)
                    expected = fetcher.FETCH_ERROR if failure == 'gz-status' else fetcher.FETCH_NOT_NEEDED
                    self.assertEqual(fetcher.fetchFile(force=True), expected)
                    self.env['xbmcgui'].Dialog.return_value.notification.assert_called_once()
                    self.env['xbmcgui'].Dialog.return_value.ok.assert_not_called()
                    self.assertEqual(retry.exists(), tracked)

    def test_xmltv_http_errors_do_not_add_blocking_dialog(self):
        url = 'https://example.invalid/a.xml'
        self.fetch(url)
        for failure in ('status', 'request'):
            self.status = 503
            self.requests.get.side_effect = OSError('offline') if failure == 'request' else self.download
            self.env['xbmcgui'].Dialog.reset_mock()
            self.fetch(url, force=True)
            self.env['xbmcgui'].Dialog.return_value.ok.assert_not_called()
            self.assertTrue(Path(str(self.cache) + '.retry').exists())
            self.assertEqual(self.cache.read_bytes(), A)

    def test_unchanged_source_reuses_fresh_cache_and_force_downloads(self):
        url = 'https://example.invalid/a.xml'
        self.fetch(url)
        self.payload = B
        self.fetch(url)
        self.assertEqual(self.cache.read_bytes(), A)
        self.assertFalse(self.source.needReset)
        self.assertEqual(self.requests.get.call_count, 1)
        self.fetch(url, force=True)
        self.assertEqual(self.cache.read_bytes(), B)
        self.assertTrue(self.source.needReset)

    def test_unbound_legacy_cache_refreshes_once(self):
        self.cache.write_bytes(A)
        self.payload = B
        self.fetch('https://example.invalid/b.xml')
        self.assertEqual(self.cache.read_bytes(), B)
        self.fetch('https://example.invalid/b.xml')
        self.assertEqual(self.requests.get.call_count, 1)
        marker = self.cache.with_suffix('.xml.source').read_text()
        self.assertEqual(marker, hashlib.sha256(b'https://example.invalid/b.xml').hexdigest())

    def test_cache_hit_and_failed_fetch_preserve_another_fetch_staging(self):
        url = 'https://example.invalid/a.xml'
        self.fetch(url)
        sentinels = [self.profile / name for name in
                     ('xmltv.xml.tmp', 'xmltv.xml.tmp.decoded', 'xmltv.xml.other.tmp')]
        for sentinel in sentinels:
            sentinel.write_bytes(b'another fetch owns these bytes')
        self.fetch(url)
        self.assertFalse(self.source.needReset)
        self.assertEqual(self.requests.get.call_count, 1)
        for sentinel in sentinels:
            self.assertTrue(sentinel.exists(), 'cache hit deleted another fetch staging file')
        self.status = 503
        self.fetch('https://example.invalid/b.xml')
        self.assertEqual(self.cache.read_bytes(), A)
        for sentinel in sentinels:
            self.assertEqual(sentinel.read_bytes(), b'another fetch owns these bytes')
        self.assertEqual(set(self.profile.glob('*.tmp*')), set(sentinels))

    def test_failed_new_source_preserves_cache_binding_and_retries(self):
        for failure in ('http', 'request', 'stream', 'gzip', 'copy', 'replace'):
            with self.subTest(failure=failure):
                self.payload, self.status = A, 200
                self.requests.get.side_effect = self.download
                self.fetch('https://example.invalid/a.xml', force=True)
                marker = self.cache.with_suffix('.xml.source').read_bytes()
                self.payload = B
                url = 'https://example.invalid/b.xml'
                if failure == 'http':
                    self.status = 503
                elif failure == 'request':
                    self.requests.get.side_effect = OSError('synthetic request failure')
                elif failure == 'stream':
                    def chunks(size):
                        yield B[:10]
                        raise OSError('synthetic interrupted stream')
                    self.requests.get.side_effect = lambda *a, **kw: SimpleNamespace(
                        status_code=200, headers={}, iter_content=chunks)
                elif failure == 'gzip':
                    self.payload = b'\x1f\x8b\x08broken'
                elif failure == 'copy':
                    url = str(self.profile / 'unavailable.xml')
                    self.copy.side_effect = lambda *args: False
                replacement = patch.object(os, 'replace', side_effect=OSError('synthetic replace failure'))
                with replacement if failure == 'replace' else nullcontext():
                    self.fetch(url)
                self.assertEqual(self.cache.read_bytes(), A)
                # A missing binding after a failed replacement is also safe.
                if self.cache.with_suffix('.xml.source').exists():
                    self.assertEqual(self.cache.with_suffix('.xml.source').read_bytes(), marker)
                self.assertFalse(self.source.needReset)
                self.assertFalse(list(self.profile.glob('*.tmp*')))
                self.requests.get.side_effect = self.download
                self.copy.side_effect = self.copy_file
                self.payload, self.status = B, 200
                if failure == 'copy':
                    Path(url).write_bytes(B)
                self.fetch(url)
                self.assertEqual(self.cache.read_bytes(), B)
                self.assertTrue(self.source.needReset)

    def test_gzip_fallback_and_authentication(self):
        self.settings.update(gz='true', authentication='true', user='synthetic', password='synthetic')
        self.payload = gzip.compress(B)
        self.fetch('https://example.invalid/b.xml')
        self.assertEqual(self.cache.read_bytes(), B)
        self.requests.get.assert_called_with('https://example.invalid/b.xml.gz',
                                             auth=('synthetic', 'synthetic'), stream=True)
        self.payload = A
        def fallback(url, **kwargs):
            response = self.download(url, **kwargs)
            response.status_code = 404 if url.endswith('.gz') else 200
            return response
        self.requests.get.side_effect = fallback
        self.fetch('https://example.invalid/a.xml')
        self.assertEqual(self.cache.read_bytes(), A)
        self.requests.get.assert_called_with('https://example.invalid/a.xml',
                                             auth=('synthetic', 'synthetic'), stream=True)
        self.status = 503
        self.requests.get.side_effect = self.download
        self.fetch('https://example.invalid/unavailable.xml')
        self.assertEqual(self.cache.read_bytes(), A)
        self.assertFalse(self.source.needReset)

    def test_md5_reuse_is_only_for_same_source_and_mismatch_preserves_cache(self):
        self.settings['md5'] = 'true'
        first, second = 'https://example.invalid/a.xml', 'https://example.invalid/b.xml'
        self.fetch(first)
        self.requests.get.reset_mock()
        self.fetch(first, force=True)
        self.assertEqual(self.requests.get.call_count, 2)  # explicit force bypasses MD5 reuse
        self.requests.get.reset_mock()
        self.fetch(second)  # even identical content must establish the new source
        self.assertEqual(self.requests.get.call_count, 2)
        self.assertTrue(self.source.needReset)
        marker = self.cache.with_suffix('.xml.source').read_bytes()
        def mismatch(url, **kwargs):
            response = self.download(url, **kwargs)
            response.text = hashlib.md5(A).hexdigest()
            return response
        self.payload = B
        self.requests.get.side_effect = mismatch
        self.fetch(first)
        self.assertEqual(self.cache.read_bytes(), A)
        self.assertEqual(self.cache.with_suffix('.xml.source').read_bytes(), marker)
        self.assertFalse(self.source.needReset)
        self.requests.get.side_effect = self.download
        self.fetch(first)
        self.assertEqual(self.cache.read_bytes(), B)

    def test_unchanged_interval_expiry_always_and_local_timestamp(self):
        url = 'https://example.invalid/a.xml'
        self.fetch(url)
        self.payload = B
        os.utime(self.cache, (1, 1))
        self.fetch(url)
        self.assertEqual(self.cache.read_bytes(), B)
        self.settings['xmltv.interval'] = '0'
        self.payload = A
        self.fetch(url)
        self.assertEqual(self.cache.read_bytes(), A)
        local = self.profile / 'local.xml'
        local.write_bytes(B)
        self.fetch(str(local))
        self.copy.reset_mock()
        self.fetch(str(local), force=True)
        self.copy.assert_not_called()  # validated native bytes are hashed, not recopied
        os.utime(local, (time.time() + 10, time.time() + 10))
        local.write_bytes(A)
        self.fetch(str(local))
        self.assertEqual(self.cache.read_bytes(), A)

    def test_xmltv_slots_have_independent_source_bindings(self):
        for slot in ('xmltv.xml', 'xmltv2.xml', 'xmltv3.xml'):
            self.payload = A
            self.source.updateLocalFile(slot, 'https://example.invalid/a.xml', self.addon)
        self.payload = B
        self.source.updateLocalFile('xmltv2.xml', 'https://example.invalid/b.xml', self.addon)
        self.assertEqual((self.profile / 'xmltv2.xml').read_bytes(), B)
        for slot in ('xmltv.xml', 'xmltv3.xml'):
            self.assertEqual((self.profile / slot).read_bytes(), A)

    def test_marker_write_failure_cannot_bind_replaced_bytes_to_old_source(self):
        first, second = 'https://example.invalid/a.xml', 'https://example.invalid/b.xml'
        self.fetch(first)
        self.payload = B
        real_open = open
        def fail_marker(path, mode='r', *args, **kwargs):
            if str(path).endswith('.source') and mode == 'w':
                raise OSError('synthetic marker write failure')
            return real_open(path, mode, *args, **kwargs)
        with patch('builtins.open', side_effect=fail_marker):
            self.fetch(second)
        self.assertEqual(self.cache.read_bytes(), B)
        self.assertFalse(self.cache.with_suffix('.xml.source').exists())
        self.payload = A
        self.fetch(first)
        self.assertEqual(self.cache.read_bytes(), A)
        self.assertTrue(self.source.needReset)


if __name__ == '__main__':
    unittest.main(verbosity=2)
