# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
"""Bounded data transport for the fixed ordinary AutoPlay callbacks (Python 3.8).

This is encoding, not authority or a registry. Never decode into command grammar.
The one-argument wire format and two-argument legacy data entry are disjoint.
"""
import base64
import json
import re
from typing import Sequence, Tuple

MAX_BYTES = 65536
MAX_TOKEN = 3 + 4 * ((MAX_BYTES + 2) // 3)


def encode_identity(channel: str, start: str) -> str:
    if not isinstance(channel, str) or not channel or not isinstance(start, str) or not start:
        raise ValueError('Invalid autoplay identity')
    # Reject oversized input before serialization; no character restrictions.
    if len(channel) > MAX_BYTES or len(start) > MAX_BYTES:
        raise ValueError('Oversized autoplay identity')
    raw = json.dumps([1, channel, start], ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    if len(raw) > MAX_BYTES:
        raise ValueError('Oversized autoplay identity')
    return 'v1_' + base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')


def decode_identity(token: str) -> Tuple[str, str]:
    if not isinstance(token, str) or len(token) > MAX_TOKEN or not re.fullmatch(r'v1_[A-Za-z0-9_-]+', token):
        raise ValueError('Invalid autoplay payload')
    encoded = token[3:]
    raw = base64.b64decode(encoded + '=' * (-len(encoded) % 4), altchars=b'-_', validate=True)
    if len(raw) > MAX_BYTES:
        raise ValueError('Oversized autoplay payload')
    try:
        record = json.loads(raw.decode('utf-8'))
    except (RecursionError, UnicodeError) as exc:
        raise ValueError('Invalid autoplay payload') from exc
    if (not isinstance(record, list) or len(record) != 3
            or type(record[0]) is not int or record[0] != 1):
        raise ValueError('Invalid autoplay version/schema')
    channel, start = record[1:]
    if encode_identity(channel, start) != token:
        raise ValueError('Noncanonical autoplay payload')
    return channel, start


def callback_identity(argv: Sequence[str]) -> Tuple[str, str]:
    if len(argv) == 2:
        return decode_identity(argv[1])
    if len(argv) == 3:
        # Already parsed argv is data, not a license to interpolate it in a builtin.
        # In particular, a valid old ID beginning with v1_ stays a channel ID.
        channel, start = argv[1:]
        encode_identity(channel, start)  # Apply the same bounded identity checks.
        return channel, start
    raise ValueError('Invalid autoplay arguments')
