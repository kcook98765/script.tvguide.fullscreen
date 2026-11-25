# -*- coding: utf-8 -*-
#
# TV Guide Fullscreen
# Copyright (C) 2016 primaeval.dev@gmail.com
#
#      Original for FTV Guide
#      bluezed.apps@gmail.com
#
#      Modified for TV Guide Fullscreen (2016)
#      by primaeval - primaeval.dev@gmail.com
#
# This Program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this Program; see the file LICENSE.txt.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
import xbmc
import xbmcvfs
import xbmcgui
import xbmcaddon
import os
import datetime,time
import zlib
import gzip
import requests
import hashlib
import uuid
import sqlite3
import json

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

def log(x):
    xbmc.log(repr(x))


class FileFetcher(object):
    INTERVAL_ALWAYS = 0
    INTERVAL_12 = 1
    INTERVAL_24 = 2
    INTERVAL_48 = 3
    INTERVAL_7 = 4
    INTERVAL_14 = 5

    FETCH_ERROR = -1
    FETCH_NOT_NEEDED = 0
    FETCH_OK = 1

    TYPE_DEFAULT = 1
    TYPE_REMOTE = 2

    basePath = xbmcvfs.translatePath(os.path.join('special://profile', 'addon_data', 'script.tvguide.fullscreen'))
    filePath = ''
    fileUrl = ''
    addon = None
    fileType = TYPE_DEFAULT

    def __init__(self, url, path, addon, track_source=False, validator=None):
        self.addon = addon
        self.track_source = track_source
        self.validator = validator

        if url.startswith("http://") or url.startswith("https://"):
            self.fileType = self.TYPE_REMOTE
            self.fileUrl = url
            self.fileName = path.split('/')[-1]
            self.filePath = path
        else:
            self.fileType = self.TYPE_DEFAULT
            self.fileUrl = url
            self.fileName = path.split('/')[-1]
            self.filePath = path

        # make sure the folder is actually there already!
        if not os.path.exists(self.basePath):
            os.makedirs(self.basePath)

    @staticmethod
    def acquireXMLTVLock():
        # SQLite's OS lock coordinates Kodi interpreters and releases on crash.
        # Never unlink this file: doing so would split the lock's identity.
        lock = sqlite3.connect(os.path.join(FileFetcher.basePath, 'xmltv.cache.lock'), timeout=0)
        try:
            lock.execute('BEGIN EXCLUSIVE')
        except Exception:
            lock.close()
            raise
        return lock

    @staticmethod
    def fileDigest(path):
        digest = hashlib.sha256()
        with open(path, 'rb') as data:
            for chunk in iter(lambda: data.read(1024 * 1024), b''):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def fileSignature(path):
        # Installed caches are native files. Include replacement identity AND
        # change time: same-size/same-mtime rename and in-place edits both matter.
        st = os.stat(path)
        if not st.st_ino:
            return None  # Unreliable identity: callers must compare bytes.
        return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)

    def diagnosticSlot(self):
        # Only reviewed local cache names may enter visible diagnostics. Neither
        # source basenames nor arbitrary destination names are safe to display.
        if self.fileName in ('xmltv.xml', 'xmltv2.xml', 'xmltv3.xml',
                             'categories.ini', 'mapping.ini', 'addons.ini'):
            return self.fileName
        return 'cache file'

    def fetchFile(self,force=False):
        # Never clean up another foreground/service fetch's staging files.
        tmpFile = os.path.join(self.basePath, self.fileName+'.'+uuid.uuid4().hex+'.tmp')
        lock = None
        try:
            if self.track_source:
                try:
                    lock = self.acquireXMLTVLock()
                except sqlite3.OperationalError:
                    # Another fetch/import owns the caches; keep last-good data.
                    return self.FETCH_NOT_NEEDED
            return self._fetchFile(force, tmpFile)
        except Exception:
            xbmc.log('[script.tvguide.fullscreen] Failed to fetch cache file', xbmc.LOGERROR)
            return self.FETCH_ERROR
        finally:
            if lock is not None:
                lock.close()
            for path in (tmpFile, tmpFile+'.decoded', tmpFile+'.validated'):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def _fetchFile(self, force, tmpFile):
        assert self.addon is not None  # Provided by __init__ before fetching.
        slot = self.diagnosticSlot()
        retVal = self.FETCH_NOT_NEEDED
        retry_pending = self.track_source and os.path.exists(self.filePath+'.retry')
        source_changed = False
        if self.track_source:
            # Store no URL/path credentials; an unbound legacy cache refreshes once.
            source_id = hashlib.sha256(self.fileUrl.encode('utf-8')).hexdigest()
            try:
                with open(self.filePath+'.source', 'r') as marker:
                    source_changed = marker.read() != source_id
            except (OSError, UnicodeError):
                source_changed = True
        fetch = False
        if not os.path.exists(self.filePath):  # always fetch if file doesn't exist!
            fetch = True
        elif force == True or source_changed or (self.track_source and (
                self.fileType == self.TYPE_DEFAULT or retry_pending)):
            fetch = True
        else:
            interval = int(self.addon.getSetting('xmltv.interval'))
            if interval != self.INTERVAL_ALWAYS:
                modTime = datetime.datetime.fromtimestamp(os.path.getmtime(self.filePath))
                td = datetime.datetime.now() - modTime
                # need to do it this way cause Android doesn't support .total_seconds() :(
                diff = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6) / 10 ** 6
                if ((interval == self.INTERVAL_12 and diff >= 43200) or
                        (interval == self.INTERVAL_24 and diff >= 86400) or
                        (interval == self.INTERVAL_48 and diff >= 172800) or
                        (interval == self.INTERVAL_7 and diff >= 604800) or
                        (interval == self.INTERVAL_14 and diff >= 1209600)):
                    fetch = True
            else:
                fetch = True

        if fetch:
            # A failed forced HTTP refresh must retry even if the old cache's
            # interval has not elapsed. This marker never authorizes deletion.
            retry = self.filePath+'.retry'
            if self.track_source and self.fileType == self.TYPE_REMOTE:
                with open(retry, 'w'):
                    pass
            receipt = None
            repair = self.addon.getSetting('xmltv.and')
            if self.track_source and self.validator is not None and not source_changed:
                try:
                    with open(self.filePath+'.validated', 'r') as marker:
                        candidate = json.load(marker)
                    signature = self.fileSignature(self.filePath)
                    if (signature is not None and candidate.get('version') == 1 and
                            candidate.get('cache') == list(signature) and
                            candidate.get('repair') == repair):
                        receipt = candidate
                except (OSError, ValueError, TypeError, AttributeError):
                    pass
            # Native local inputs still get a robust full content comparison,
            # never an mtime shortcut, but need not be copied or parsed again.
            if receipt is not None and self.fileType == self.TYPE_DEFAULT and os.path.isfile(self.fileUrl):
                if self.fileDigest(self.fileUrl) == receipt.get('raw'):
                    return self.FETCH_NOT_NEEDED
            user = ''
            password = ''
            new_md5 = ''
            auth = None
            if self.addon.getSetting('authentication') == 'true':
                user = self.addon.getSetting('user')
                password = self.addon.getSetting('password')
                auth = (user, password)
            if self.fileType == self.TYPE_DEFAULT:
                xbmc.log('[script.tvguide.fullscreen] VFS copy: %s' % slot, xbmc.LOGDEBUG)
                if not self.track_source and not source_changed and xbmcvfs.exists(self.filePath):
                    st = xbmcvfs.Stat(self.fileUrl)
                    src_modified = st.st_mtime()
                    st = xbmcvfs.Stat(self.filePath)
                    dst_modified = st.st_mtime()
                    if src_modified <= dst_modified:
                        return self.FETCH_NOT_NEEDED
                if not xbmcvfs.copy(self.fileUrl, tmpFile):
                    xbmc.log('[script.tvguide.fullscreen] VFS copy failed: %s' % slot, xbmc.LOGERROR)
                    return self.FETCH_ERROR
            else:

                if self.addon.getSetting('md5') == 'true':
                    file = self.filePath+".md5"
                    url = self.fileUrl+".md5"
                    old_md5 = xbmcvfs.File(file,"rb").read()
                    try:
                        r = requests.get(url,auth=auth)
                        if r.status_code == requests.codes.ok:
                            new_md5 = r.text[:32]
                    except Exception:
                        xbmc.log('[script.tvguide.fullscreen] MD5 request failed: %s' % slot, xbmc.LOGERROR)
                    if ((not self.track_source or not (force or retry_pending)) and not source_changed and
                            old_md5 and old_md5 == new_md5 and self.addon.getSetting('xmltv.refresh') == 'false'):
                        if self.track_source:
                            os.remove(retry)
                        return self.FETCH_NOT_NEEDED
                xbmc.log('[script.tvguide.fullscreen] HTTP download: %s' % slot, xbmc.LOGDEBUG)
                total = 0
                fileUrl = self.fileUrl
                if ADDON.getSetting('gz') == 'true':
                    fileUrl = fileUrl + '.gz'
                try:
                    r = requests.get(fileUrl,auth=auth, stream=True)
                    if r.status_code != requests.codes.ok:
                        if ADDON.getSetting('gz') == 'true':
                            r = requests.get(self.fileUrl,auth=auth, stream=True)
                            if r.status_code != requests.codes.ok:
                                xbmc.log('[script.tvguide.fullscreen] HTTP download failed: %s (status %d)' % (slot, r.status_code), xbmc.LOGERROR)
                                xbmcgui.Dialog().notification("TV Guide Fullscreen", "Download failed: %s (HTTP %d)" % (slot, r.status_code),xbmcgui.NOTIFICATION_ERROR)
                                return self.FETCH_ERROR
                        else:
                            xbmc.log('[script.tvguide.fullscreen] HTTP download failed: %s (status %d)' % (slot, r.status_code), xbmc.LOGERROR)
                            xbmcgui.Dialog().notification("TV Guide Fullscreen", "Download failed: %s (HTTP %d)" % (slot, r.status_code),xbmcgui.NOTIFICATION_ERROR)
                            # Keep ordinary HTTP failures notification-only.
                            # XMLTV's retry marker schedules another attempt.
                            return self.FETCH_NOT_NEEDED
                    if "Content-Length" in r.headers:
                        total = int(r.headers['Content-Length'])
                except Exception:
                    xbmc.log('[script.tvguide.fullscreen] HTTP request failed: %s' % slot, xbmc.LOGERROR)
                    xbmcgui.Dialog().notification("TV Guide Fullscreen", "Download request failed: %s" % slot,xbmcgui.NOTIFICATION_ERROR)
                    return self.FETCH_NOT_NEEDED

                d = xbmcgui.DialogProgressBG()
                d.create('TV Guide Fullscreen', 'downloading %s' % slot)
                chunk_size = 16 * 1024
                size = 0
                oldtime = time.time()
                try:
                    with open(tmpFile, 'wb') as f:
                        for chunk in r.iter_content(chunk_size):
                            f.write(chunk)
                            size = size + chunk_size
                            if total:
                                percent = 100.0 * size / total
                                now = time.time()
                                diff = now - oldtime
                                if diff > 1:
                                    d.update(int(percent))
                                    oldtime = now
                    d.update(100, message="Done")
                finally:
                    d.close()
            raw_digest = self.fileDigest(tmpFile) if self.track_source else ''
            # VFS inputs must be copied (their stat is not authoritative), but
            # identical validated raw bytes need no decompression/repair/parse.
            if receipt is not None and self.fileType == self.TYPE_DEFAULT and raw_digest == receipt.get('raw'):
                return self.FETCH_NOT_NEEDED
            # Decode and check the staged bytes before replacing a usable cache.
            with open(tmpFile, 'rb') as staged:
                magic = staged.read(3)
            if magic == b"\x1f\x8b\x08":
                with gzip.open(tmpFile, 'rb') as compressed, open(tmpFile+'.decoded', 'wb') as decoded:
                    for chunk in iter(lambda: compressed.read(1024 * 1024), b''):
                        decoded.write(chunk)
                os.replace(tmpFile+'.decoded', tmpFile)
            check_md5 = new_md5 and (self.addon.getSetting('md5') == 'true')
            if check_md5:
                md5 = hashlib.md5()
                with open(tmpFile, 'rb') as staged:
                    for chunk in iter(lambda: staged.read(1024 * 1024), b''):
                        md5.update(chunk)
                md5_file = md5.hexdigest()
                if md5_file != new_md5:
                    xbmc.log('[script.tvguide.fullscreen] MD5 check failed: %s' % slot, xbmc.LOGERROR)
                    xbmcgui.Dialog().notification("TV Guide Fullscreen", "MD5 check failed: %s" % slot,xbmcgui.NOTIFICATION_ERROR)
                    return self.FETCH_ERROR
            # XMLTV validation (including optional legacy entity repair) happens
            # only on our staging file, never on the usable last-good cache.
            if self.validator is not None:
                self.validator(tmpFile)
            unchanged = (self.track_source and self.fileType == self.TYPE_DEFAULT and
                         not source_changed and os.path.exists(self.filePath) and
                         self.fileDigest(tmpFile) == self.fileDigest(self.filePath))
            # Invalidate first: a marker-write failure must never bind new bytes
            # to the previous source. Missing/partial markers safely force retry.
            if not unchanged:
                if self.track_source and os.path.exists(self.filePath+'.source'):
                    os.remove(self.filePath+'.source')
                os.replace(tmpFile, self.filePath)
            if self.track_source:
                if not unchanged:
                    with open(self.filePath+'.source', 'w') as marker:
                        marker.write(source_id)
                if self.validator is not None:
                    with open(tmpFile+'.validated', 'w') as marker:
                        json.dump(dict(version=1, raw=raw_digest, repair=repair,
                                       cache=self.fileSignature(self.filePath)), marker)
                    os.replace(tmpFile+'.validated', self.filePath+'.validated')
                if os.path.exists(retry):
                    os.remove(retry)
            if check_md5:
                xbmcvfs.File(self.filePath+".md5","wb").write(new_md5)
            retVal = self.FETCH_NOT_NEEDED if unchanged else self.FETCH_OK
            xbmc.log('[script.tvguide.fullscreen] Cache updated: %s' % slot, xbmc.LOGDEBUG)
        return retVal
