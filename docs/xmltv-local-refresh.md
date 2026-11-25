# Same-path XMLTV refresh (#85)

Reopening the guide or running its supported background update compares local
XMLTV content even when the source timestamp is equal to or older than the
installed cache. There is no filesystem watcher or navigation-time source poll.
Publish complete XML atomically rather than overwriting a feed while it is read.

## Cost and cache behavior

- Native local input is hashed on reopen. Once validated, identical raw bytes
  need no further copy, gzip decode, entity repair or XML parse. An atomic
  `.validated` receipt binds that comparison to the installed cache's native
  identity and the repair setting. Legacy/missing/corrupt receipts revalidate.
- Kodi VFS URIs still require a staging copy: their timestamps are not reliable
  evidence of unchanged content. Identical validated raw bytes skip parsing.
  Changed gzip input is decoded in bounded chunks. Entity repair still uses
  its existing whole-document implementation, on staging bytes only.
- Redraw checks memoize content digests per source instance against native
  device/inode/size/nanosecond modification/change times. Unchanged caches are
  not opened/read and no writer lock is acquired. Same-time replacements and
  in-place edits invalidate the memo. Filesystems without usable inode identity
  fall back to content comparison; native platform/filesystem qualification is
  still required, particularly for coarse change times.
- Source identity remains the hashed `.source` binding. Changing the configured
  path/URL rebinds even identical bytes; no credentials are stored in receipts.
- HTTP retains interval fetching. Explicit force bypasses XMLTV MD5 reuse.
  Failed/interrupted HTTP fetches leave a `.retry` marker so the next normal
  construction retries before the old cache interval expires. Redraw never
  fetches a provider. Non-XMLTV FileFetcher callers retain their cache policy.

## Last-good data and interruptions

Missing, malformed, wrong-root and zero-usable-programme replacements do not
replace a last-good cache. Programmes need a channel identity, parseable bounds
and positive duration; staged feeds must declare the channels they reference.
The existing per-row date filtering remains: a partially usable feed may still
replace its slot and omit rejected rows. This is not completeness detection or
per-event last-good merging, nor a check that listings cover the current day.

Every enabled slot must have a cache contributing usable programmes at import;
a missing/empty legacy or first-load optional cache cannot silently erase that
slot's previous rows just because another feed succeeds. Deliberately disabling
a slot does remove its programmes on the next successful import.

Programmes, source-scoped cleanup and the imported content/configuration key
commit together. Cancellation and import failures roll back. A process exiting
after cache promotion but before import leaves a differing durable DB key, so
the next instance imports without relying on in-memory flags or wall clocks.
An already committed import is reused, not repeated on every redraw.

Existing channel order, visibility, category/lineup, non-null automatic streams,
manual/alternative mappings and reminder/AutoPlay rules survive refresh,
including Reset on Start. Explicit Reset Database remains separate.

XMLTV cache producers and all current DB importers coordinate using the same
SQLite OS lock (`xmltv.cache.lock`), released on process exit. Never unlink it.
XMLTV neither obeys nor creates/deletes the legacy `db.lock` sentinel; non-XMLTV
importers retain that sentinel policy while sharing the OS lock. No startup
lock/journal deletion is introduced. Running older add-on code concurrently
is not a supported coordination contract.

The installed programme UNIQUE constraint still omits source. A same-channel,
same-time collision with another provider therefore rolls back the XMLTV
import instead of deleting the other provider's event. This schema limitation
is not migrated here; conflicting providers cannot both occupy that key.

## Source regressions (not native acceptance)

```sh
python3 -m unittest discover -s tests -p 'check_xmltv*.py'
python3 tests/check_service_safety.py
python3 tests/check_m3u_channel_updates.py
git diff --check
```

Fixtures execute extracted production constructors/fetcher/parser/models,
schema/adapters, importer and normal/Quick redraw paths with synthetic Kodi VFS
and HTTP adapters. They do not execute Kodi/stub modules. `--draft` on
`tests/check_xmltv_local_refresh.py` replays the reviewed source revision
`1062edb5eb23d9fc03f52c3931a58a5cdbabc3d2` without checkout. The separately
recorded published-Beta Nexus baseline must not be repeated for this revision.
