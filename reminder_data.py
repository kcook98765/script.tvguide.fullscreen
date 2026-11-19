# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
"""Reminder-only JSON handoff. No Kodi imports or executable profile data."""
import json
import os
import re
import tempfile
import uuid
from typing import Callable

MAX_BYTES = 65536
PHASES = ('5mins', 'now')
CALLBACK = 'special://home/addons/script.tvguide.fullscreen/reminder_callback.py'


def valid_token(token):
    return isinstance(token, str) and re.fullmatch(r'[0-9a-f]{96}', token) is not None


def event_key(name):
    if not isinstance(name, str) or not re.fullmatch(r'tvguide-notification-[0-9a-f]{64}', name):
        raise ValueError('Invalid reminder name')
    return name.rsplit('-', 1)[1]


def alarm_command(name, token, phase, minutes):
    if (not valid_token(token) or event_key(name) != token[:64]
            or phase not in PHASES or type(minutes) is not int or minutes < 0):
        raise ValueError('Invalid reminder alarm')
    return 'AlarmClock(%s-%s,RunScript(%s,%s,%s),%d,True)' % (
        name, phase, CALLBACK, token, phase, minutes)


def validate(record):
    if (not isinstance(record, dict) or set(record) !=
            {'version', 'token', 'title', '5mins', 'now', 'icon', 'start', 'phases'}
            or type(record['version']) is not int or record['version'] != 1
            or not valid_token(record['token'])
            or record['phases'] not in (['now'], ['5mins', 'now'])
            or type(record['start']) not in (int, float)
            or not 0 <= record['start'] <= 253402300799):
        raise ValueError('Invalid reminder record')
    for key in ('title', '5mins', 'now', 'icon'):
        if not isinstance(record[key], str) or len(record[key].encode('utf-8')) > 16000:
            raise ValueError('Invalid reminder text')
    return record


class ReminderData:
    def __init__(self, profile):
        self.directory = os.path.join(profile, 'reminders')

    def _path(self, key):
        if not re.fullmatch(r'[0-9a-f]{64}', key):
            raise ValueError('Invalid reminder key')
        return os.path.join(self.directory, key + '.json')

    def _read(self, key):
        try:
            with open(self._path(key), 'rb') as handle:
                raw = handle.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError('Reminder too large')
            try:
                decoded = json.loads(raw.decode('utf-8'))
            except (ValueError, RecursionError):
                raise ValueError('Invalid reminder JSON') from None
            record = validate(decoded)
            if record['token'][:64] != key:
                raise ValueError('Mismatched reminder')
            return record
        except FileNotFoundError:
            return None

    def save(self, name, title, early, now, icon, start, five_minute=True):
        key = event_key(name)
        # Reconstructing alarms must not rearm already delivered phases.
        previous = self._read(key)
        token = previous['token'] if previous else key + uuid.uuid4().hex
        phases = previous['phases'] if previous else (['5mins', 'now'] if five_minute else ['now'])
        record = validate(dict(version=1, token=token, title=title,
                               **{'5mins': early, 'now': now, 'icon': icon, 'start': start, 'phases': phases}))
        raw = json.dumps(record, ensure_ascii=False).encode('utf-8')
        if len(raw) > MAX_BYTES:
            raise ValueError('Reminder too large')
        os.makedirs(self.directory, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=self.directory)
        try:
            with os.fdopen(fd, 'wb') as handle:
                handle.write(raw)
            os.replace(temporary, self._path(key))
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return token

    def take(self, token, phase, now):
        if not valid_token(token) or phase not in PHASES:
            return None
        record = self._read(token[:64])
        if not record or record['token'] != token or phase not in record['phases']:
            return None
        start = record['start']
        # AlarmClock uses whole minutes, so up to 60 seconds early is expected.
        lower = start - (360 if phase == '5mins' else 60)
        if now < lower:
            return None
        claim = os.path.join(self.directory, token + '-' + phase + '.claimed')
        try:
            fd = os.open(claim, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return None
        os.close(fd)
        # A cancellation or replacement between read and claim invalidates it.
        current = self._read(token[:64])
        if not current or current['token'] != token:
            return None
        return record

    def finish(self, token, phase):
        if not valid_token(token) or phase not in PHASES:
            raise ValueError('Invalid reminder completion')
        record = self._read(token[:64])
        if record and record['token'] == token:
            fd = os.open(os.path.join(self.directory, token + '-' + phase + '.done'),
                         os.O_WRONLY | os.O_CREAT, 0o600)
            os.close(fd)

    def cancel(self, name):
        key = event_key(name)
        try:
            record = self._read(key)
        except (ValueError, UnicodeError):
            record = None
        try:
            os.unlink(self._path(key))  # Invalidate callbacks before deleting claims.
        except FileNotFoundError:
            pass
        if record:
            for phase in PHASES:
                for suffix in ('.claimed', '.done'):
                    try:
                        os.unlink(os.path.join(self.directory, record['token'] + '-' + phase + suffix))
                    except FileNotFoundError:
                        pass

    def names(self):
        if not os.path.isdir(self.directory):
            return []
        return ['tvguide-notification-' + name[:-5] for name in os.listdir(self.directory)
                if re.fullmatch(r'[0-9a-f]{64}\.json', name)]

    def clear(self):
        names = self.names()
        for name in names:
            self.cancel(name)
        return names

    def prune_completed(self, now):
        for name in self.names():
            try:
                record = self._read(event_key(name))
            except (ValueError, UnicodeError):
                self.cancel(name)
                continue
            # No lateness expiry: pending callbacks remain valid until cancel.
            # A consumed event can go once reconstruction would skip its start.
            if record and record['start'] < now and all(os.path.exists(os.path.join(
                    self.directory, record['token'] + '-' + phase + '.done')) for phase in record['phases']):
                self.cancel(name)


def deliver(store: ReminderData, token: str, phase: str, now: float,
            notify: Callable[[str, str, str, int, bool], None]) -> bool:
    record = store.take(token, phase, now)
    if record is None:
        return False
    # Notification builtin defaults: 10000 ms and sound on. Strings stay data.
    notify(record['title'], record[phase], record['icon'], 10000, True)
    store.finish(token, phase)
    return True
