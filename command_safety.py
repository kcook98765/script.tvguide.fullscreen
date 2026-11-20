# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
"""Pure constraints for the few retained, nested Kodi alarm commands.

Do not escape arbitrary text through multiple builtin parses. Reject grammar
characters instead; media locations belong in Player.play, not builtin strings.
See docs/modernization-safety.md for the Kodi parser/AlarmClock references.
"""
import hashlib
import json
import re


def alarm_name(kind, title, start, channel=None, source=None):
    # Only callers' fixed namespaces and a digest ever enter command grammar.
    assert kind in ('notification', 'autoplay', 'catchup')
    key = (u'%s\n%s' % (title, start)).encode('utf-8')
    if channel is not None or source is not None:
        # A versioned tuple, not delimiter concatenation of imported identities.
        # The unscoped form remains only for catchup and known legacy cancellation.
        assert isinstance(channel, str) and isinstance(source, str)
        key = json.dumps([1, source, channel, title, str(start)],
                         ensure_ascii=True, separators=(',', ':')).encode('ascii')
    return 'tvguide-%s-%s' % (kind, hashlib.sha256(key).hexdigest())


def is_builtin_data(value):
    # Conservative for BOTH AlarmClock's parse and the later command's parse.
    # No quotes, escapes, argument separators, parentheses or control bytes.
    return bool(value) and not re.search(r'''[(),"'\\\x00-\x1f\x7f]''', value)
