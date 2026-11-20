"""Rebuildable title -> image string data; no Kodi imports or legacy migration.

GPL-2.0-or-later; see LICENSE.txt. Writes are best effort, atomic on a local
filesystem, and serialized within this instance, not between guide processes.
"""
import json
import os
import stat
import tempfile
import threading
from typing import Dict, Optional

FILENAME = 'image-matches-v1.json'
MAX_BYTES = 2 * 1024 * 1024
MAX_ENTRIES = 1000
MAX_TITLE = 4096
MAX_IMAGE = 16384


def _integer(text):
    # Older embedded Python 3.8 has no interpreter-level integer digit limit.
    # Only schema version 1 is useful; never construct an enormous integer.
    if len(text) > 9:
        raise ValueError('Oversized cache number')
    return int(text)


def _entry(title, image):
    if not (type(title) is str and type(image) is str and
            len(title) <= MAX_TITLE and len(image) <= MAX_IMAGE):
        return False
    try:
        title.encode('utf-8')
        image.encode('utf-8')
        return True
    except UnicodeError:
        return False


class ImageCache:
    def __init__(self, profile: str):
        self._lock = threading.RLock()
        self._entries: Dict[str, str] = {}
        self._profile = profile
        self._path: Optional[str] = None
        try:
            # Only an already translated local profile directory, never a URI or
            # a title-derived path. Do not create directories or follow links.
            if type(profile) is not str or not os.path.isabs(profile):
                return
            self._profile = os.path.normpath(profile)
            self._path = os.path.join(self._profile, FILENAME)
            self._load()
        except (OSError, ValueError, TypeError):
            self._path = None

    def _safe_directory(self):
        directory = self._profile
        while True:
            if not stat.S_ISDIR(os.lstat(directory).st_mode):
                raise ValueError('Cache needs an existing local directory without symlinks')
            parent = os.path.dirname(directory)
            if parent == directory:
                return
            directory = parent

    def _load(self):
        try:
            if self._path is None:
                return
            self._safe_directory()
            before = os.lstat(self._path)
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
                return
            flags = (os.O_RDONLY | getattr(os, 'O_BINARY', 0) |
                     getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
            with os.fdopen(os.open(self._path, flags), 'rb') as stream:
                after = os.fstat(stream.fileno())
                if (not stat.S_ISREG(after.st_mode) or after.st_size > MAX_BYTES or
                        (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)):
                    return
                raw = stream.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                return
            value = json.loads(raw.decode('utf-8'), parse_int=_integer)
            if (type(value) is not dict or set(value) != {'version', 'entries'} or
                    type(value['version']) is not int or value['version'] != 1):
                return
            entries = value['entries']
            if (type(entries) is dict and len(entries) <= MAX_ENTRIES and
                    all(_entry(k, v) for k, v in entries.items())):
                self._entries = entries
        except (OSError, ValueError, TypeError, RecursionError):
            pass

    def _save(self):
        temporary = None
        try:
            if self._path is None:
                return False
            self._safe_directory()
            # replace never follows a final symlink; refuse it anyway, along
            # with directories/devices. Never open the destination for writing.
            if os.path.lexists(self._path) and not stat.S_ISREG(os.lstat(self._path).st_mode):
                return False
            raw = self._encode(self._entries)
            if len(raw) > MAX_BYTES:
                return False
            fd, temporary = tempfile.mkstemp(prefix='.image-matches-', suffix='.tmp', dir=self._profile)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self._path)
            temporary = None
            return True
        except (OSError, ValueError, TypeError, RecursionError):
            return False
        finally:
            if temporary is not None:
                try:
                    os.unlink(temporary)
                except OSError:
                    pass

    @staticmethod
    def _encode(entries):
        return json.dumps({'version': 1, 'entries': entries}, ensure_ascii=False,
                          separators=(',', ':')).encode('utf-8')

    def __contains__(self, title):
        with self._lock:
            return title in self._entries

    def __getitem__(self, title):
        with self._lock:
            return self._entries[title]

    def __setitem__(self, title, image):
        if not _entry(title, image):
            return
        with self._lock:
            if title not in self._entries and len(self._entries) >= MAX_ENTRIES:
                return
            candidate = dict(self._entries)
            candidate[title] = image
            try:
                if len(self._encode(candidate)) > MAX_BYTES:
                    return
            except (ValueError, UnicodeError):
                return
            self._entries = candidate
            # Keep usable in-memory entries even when persistence is unavailable.
            self._save()

    def __delitem__(self, title):
        with self._lock:
            del self._entries[title]
            self._save()

    def clear(self):
        with self._lock:
            self._entries.clear()
            return self._save()
