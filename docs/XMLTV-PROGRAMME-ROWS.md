# XMLTV programme row handling (Alpha 2, X1)

This bounded change relates to #4 / #2; it does **not** close either broad issue.

The XMLTV reader skips a programme with a missing, empty or whitespace-only
channel identity, or with a missing/empty/unparseable start or stop under the
existing date parser. It then continues to later rows in that file and the
remaining enabled source slots. A missing stop can be permitted by XMLTV, but
cannot be represented by this add-on's current timed grid; no end is invented.

Only the two date-conversion calls catch `ValueError` / `IndexError`; the existing
parser's `None` result is also treated as unusable. XML syntax errors and unrelated
failures still propagate. There are no new skip logs exposing feed or programme
content. Existing ID normalization/routing, valid metadata, date/timezone parsing,
source ordering and per-source minute offsets are retained. There is no new
duration or title policy, schedule inference or XML syntax repair.

## Checks and boundaries

`tests/check_xmltv_programme_rows.py` runs the real extracted XMLTV methods and
models against tiny synthetic in-memory files, using the existing offsets test
adapter. It covers required fields in each source slot, good leading/trailing
rows, complete model attributes, both timestamp bounds, channel shortcuts,
ordinary malformed XML and unrelated-error propagation. It does not start Kodi
or establish native guide/grid acceptance. Full static qualification and native
startup are outside this implementation batch.

## Deferred cache investigation (#4)

Automatic settings invalidation remains deferred after real-schema preservation
failures: naive additional tracked settings delete rules; flag-only invalidation
deletes inactive-source programmes; narrowing SQL deletion to one source exposes
cross-source programme uniqueness / foreign-key failures. None is an accepted
solution. This batch changes no cache keys, invalidation flags, SQL, schema or
migration behavior. Existing source-switch cache tests protect earlier behavior,
not the unresolved settings/inactive-source preservation problem. Separate
real-schema preservation evidence and independent review are required before
that work can proceed; #4 must not be reported as fully resolved here.
