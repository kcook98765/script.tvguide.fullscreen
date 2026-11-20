# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-or-later
"""Read compatibility for retained legacy settings; never rewrites stored values."""


def is_meta_catchup(value):
    # labelenum stores the label. Older defaults exposed the literal string "0".
    # Keep accepting it as Meta without converting Direct or touching profiles.
    return value in ('0', 'Meta?')
