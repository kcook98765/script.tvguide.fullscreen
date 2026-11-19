# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
"""Optional, interactive Kodi PVR recording. No XMLTV IDs, legacy jobs or commands.

The caller supplies Kodi's JSON-RPC function and Dialog; this module is also
testable without importing Kodi (or running its stubs) on the host.
"""
import datetime
import json


CHANNEL_FIELDS = ['channel', 'channeltype', 'clientid', 'isrecording']
BROADCAST_FIELDS = ['title', 'starttime', 'endtime', 'clientid', 'hastimer']
TIMER_FIELDS = ['title', 'channelid', 'clientid', 'starttime', 'endtime',
                'state', 'istimerrule', 'isreadonly', 'isreminder']
BACKEND_REQUIRED = ('Recording needs an enabled Kodi PVR client with a recording/'
                    'timer backend (for example Tvheadend or NextPVR). '
                    'An XMLTV/M3U source alone is not a recorder. '
                    'Configure the backend separately in Kodi.')


class RecordingError(Exception):
    pass


def valid_id(value):
    # Kodi Library.Id, also confined to the signed int consumed by Kodi C++.
    return type(value) is int and 0 < value <= 2147483647


def utc_time(value):
    # Tagged Kodi serializers use DB datetime from the UTC PVR time members.
    return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(
        tzinfo=datetime.timezone.utc)


class PVRRecording:
    def __init__(self, execute, dialog, now=None):
        self.execute = execute
        self.dialog = dialog
        self.now = now or (lambda: datetime.datetime.now(datetime.timezone.utc))
        self.request_id = 0

    def _rpc(self, method, **params):
        self.request_id += 1
        request = {'jsonrpc': '2.0', 'id': self.request_id,
                   'method': method, 'params': params}
        try:
            response = json.loads(self.execute(json.dumps(request)))
        except Exception as exc:
            # A lost mutation reply is uncertain. NEVER retry or claim success.
            raise RecordingError('No reliable Kodi reply. Check Kodi PVR before '
                                 'trying again; the request may have taken effect.') from exc
        if (not isinstance(response, dict) or response.get('jsonrpc') != '2.0'
                or type(response.get('id')) is not int
                or response['id'] != self.request_id or 'error' in response
                or 'result' not in response):
            raise RecordingError('Kodi did not confirm %s. Check PVR/backend status '
                                 'in Kodi before trying again.' % method)
        return response['result']

    def _clients(self):
        if self._rpc('PVR.GetProperties', properties=['available']).get('available') is not True:
            raise RecordingError(BACKEND_REQUIRED)
        clients = self._rpc('PVR.GetClients')['clients']
        capable = {c['clientid']: c for c in clients
                   if valid_id(c.get('clientid')) and c.get('supportsrecordings') is True
                   and c.get('supportstimers') is True}
        if not capable:
            raise RecordingError(BACKEND_REQUIRED)
        return capable

    def _choose(self, heading, rows, labels):
        if not rows:
            raise RecordingError('No supported PVR items available. Check the '
                                 'backend/channel EPG in Kodi. Nothing was changed.')
        index = self.dialog.select(heading, labels)
        if type(index) is not int or not 0 <= index < len(rows):
            return None
        return rows[index]

    def _channel_label(self, channel, clients):
        client = clients[channel['clientid']]
        return '%s [%s; channel %d; %s / client %d]' % (
            channel.get('channel') or channel.get('label', ''),
            channel['channeltype'], channel['channelid'],
            client.get('label') or client.get('addonid', ''), channel['clientid'])

    def _channel(self, clients):
        channels = []
        for group in ('alltv', 'allradio'):
            channels.extend(self._rpc('PVR.GetChannels', channelgroupid=group,
                                      properties=CHANNEL_FIELDS)['channels'])
        channels = [c for c in channels if valid_id(c.get('channelid'))
                    and valid_id(c.get('clientid')) and c['clientid'] in clients
                    and c.get('channeltype') in ('tv', 'radio')
                    and type(c.get('isrecording')) is bool]
        return self._choose('Choose the actual PVR channel (no automatic mapping)',
                            channels, [self._channel_label(c, clients) for c in channels])

    def _unchanged(self, method, key, id_key, item, fields):
        fresh = self._rpc(method, **{id_key: item[id_key], 'properties': fields})[key]
        if any(type(fresh.get(k)) is not type(item.get(k)) or fresh.get(k) != item.get(k)
               for k in [id_key, 'label'] + fields):
            raise RecordingError('PVR item changed. Nothing further was sent. '
                                 'Reopen the list and check your selection.')

    def _accepted(self, method, **params):
        if self._rpc(method, **params) != 'OK':
            raise RecordingError('Kodi did not acknowledge the request. Check Kodi '
                                 'PVR before trying again; do not assume success.')
        self.dialog.ok('Kodi PVR', 'Kodi accepted the request. Verify the timer/'
                       'recording and any backend conflicts in Kodi PVR. '
                       'This is not confirmation of a completed recording.')
        return True

    def _record(self, clients, future, guide_hint):
        channel = self._channel(clients)
        if channel is None:
            return False
        label = self._channel_label(channel, clients)
        self._unchanged('PVR.GetChannelDetails', 'channeldetails', 'channelid',
                        channel, CHANNEL_FIELDS)
        if future:
            if clients[channel['clientid']].get('supportsepg') is not True:
                raise RecordingError('This PVR client does not report EPG support. '
                                     'Use Kodi PVR to inspect its timer options.')
            broadcasts = self._rpc('PVR.GetBroadcasts', channelid=channel['channelid'],
                                   properties=BROADCAST_FIELDS)['broadcasts']
            broadcasts = [b for b in broadcasts if self._future(b, channel)]
            broadcasts.sort(key=lambda b: b['starttime'])
            broadcast = self._choose('Choose the actual future PVR broadcast (UTC)',
                                     broadcasts, [self._event_label(b) for b in broadcasts])
            if broadcast is None:
                return False
            question = ('Schedule ONLY this PVR broadcast, once?\n%s\n%s\n'
                        'Guide reference only: %s\nConfirm the channel and event match. '
                        'Backend padding/conflict policy applies.' %
                        (label, self._event_label(broadcast), guide_hint))
        else:
            if channel['isrecording']:
                raise RecordingError('This PVR channel is already recording. '
                                     'Use PVR timers to inspect/cancel one exact timer.')
            question = ('Record NOW on this PVR channel?\n%s\nGuide reference only: %s\n'
                        'This does not schedule the guide programme. Duration/end '
                        'is chosen by Kodi/backend, not the XMLTV programme.' %
                        (label, guide_hint))
        if not self.dialog.yesno('Confirm Kodi PVR recording', question):
            return False
        # Re-read after user interaction. IDs and displayed facts must still agree.
        if self._clients().get(channel['clientid']) != clients[channel['clientid']]:
            raise RecordingError('The selected PVR backend changed. Reopen and check it.')
        self._unchanged('PVR.GetChannelDetails', 'channeldetails', 'channelid',
                        channel, CHANNEL_FIELDS)
        if future:
            self._unchanged('PVR.GetBroadcastDetails', 'broadcastdetails', 'broadcastid',
                            broadcast, BROADCAST_FIELDS)
            if not self._future(broadcast, channel):
                raise RecordingError('The selected broadcast is no longer in the future.')
            return self._accepted('PVR.AddTimer', broadcastid=broadcast['broadcastid'],
                                  timerrule=False, reminder=False)
        return self._accepted('PVR.Record', channel=channel['channelid'], record=True)

    def _future(self, broadcast, channel):
        try:
            return (valid_id(broadcast.get('broadcastid'))
                    and type(broadcast.get('clientid')) is int
                    and broadcast['clientid'] == channel['clientid']
                    and broadcast.get('hastimer') is False
                    and self.now() < utc_time(broadcast['starttime'])
                    < utc_time(broadcast['endtime']))
        except (ValueError, TypeError, KeyError):
            return False

    def _event_label(self, item):
        return '%s — %s to %s UTC [id %d]' % (
            item.get('title') or item.get('label', ''), item['starttime'],
            item['endtime'], item.get('broadcastid', item.get('timerid')))

    def _timers(self, clients, active_only):
        timers = self._rpc('PVR.GetTimers', properties=TIMER_FIELDS)['timers']
        timers = [t for t in timers if valid_id(t.get('timerid'))
                  and valid_id(t.get('clientid')) and t['clientid'] in clients
                  and (not active_only or t.get('state') == 'recording')]
        labels = ['%s; channel %s; client %d; %s%s' % (
            self._event_label(t), t.get('channelid'), t['clientid'], t.get('state'),
            ' [view only]' if not self._can_cancel(t) else '') for t in timers]
        timer = self._choose('Kodi PVR timers (all sources; select to cancel/stop)', timers, labels)
        if timer is None:
            return False
        if not self._can_cancel(timer):
            raise RecordingError('Rules, reminders, read-only or unknown timers are '
                                 'view-only here. Manage them in Kodi PVR.')
        channel = self._rpc('PVR.GetChannelDetails', channelid=timer['channelid'],
                            properties=CHANNEL_FIELDS)['channeldetails']
        if (not valid_id(channel.get('channelid')) or not valid_id(channel.get('clientid'))
                or channel['channelid'] != timer['channelid']
                or channel['clientid'] != timer['clientid']):
            raise RecordingError('The timer channel/backend could not be verified. Use Kodi PVR.')
        question = ('Stop this recording and delete ONLY this timer?' if
                    timer['state'] == 'recording' else 'Delete ONLY this PVR timer?')
        if not self.dialog.yesno('Confirm PVR timer cancellation',
                                 '%s\n%s\n%s\n'
                                 'May include timers created outside this guide. '
                                 'A parent rule is not deleted.' %
                                 (question, self._event_label(timer),
                                  self._channel_label(channel, clients))):
            return False
        if self._clients().get(timer['clientid']) != clients[timer['clientid']]:
            raise RecordingError('The selected PVR backend changed. Reopen and check it.')
        self._unchanged('PVR.GetChannelDetails', 'channeldetails', 'channelid',
                        channel, CHANNEL_FIELDS)
        self._unchanged('PVR.GetTimerDetails', 'timerdetails', 'timerid', timer, TIMER_FIELDS)
        return self._accepted('PVR.DeleteTimer', timerid=timer['timerid'])

    def _can_cancel(self, timer):
        return (valid_id(timer.get('channelid'))
                and timer.get('istimerrule') is False and timer.get('isreadonly') is False
                and timer.get('isreminder') is False
                and timer.get('state') in ('scheduled', 'recording'))

    def run(self, action='menu', guide_hint=''):
        """One interactive operation. False means cancelled, refused or unconfirmed."""
        try:
            if action == 'menu':
                choice = self.dialog.select('Optional Kodi PVR recording (backend required)',
                                            ['Record now on a PVR channel…',
                                             'Schedule a future PVR broadcast once…',
                                             'PVR timers / cancel or stop…'])
                if type(choice) is not int or not 0 <= choice < 3:
                    return False
                action = ('now', 'future', 'timers')[choice]
            if action not in ('now', 'future', 'timers', 'stop'):
                return False
            clients = self._clients()
            if action in ('now', 'future'):
                return self._record(clients, action == 'future', guide_hint)
            return self._timers(clients, action == 'stop')
        except (RecordingError, ValueError, TypeError, KeyError, AttributeError) as error:
            message = str(error) if isinstance(error, RecordingError) else (
                'Unexpected Kodi PVR data. Nothing further was sent. Check Kodi PVR.')
            self.dialog.ok('Kodi PVR recording unavailable', '%s\n%s' % (message, BACKEND_REQUIRED))
            return False
