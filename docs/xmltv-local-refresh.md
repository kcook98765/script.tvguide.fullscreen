# Same-path XMLTV refresh (#85)

For later integrated-runtime qualification and still-pending versioned-package
acceptance, see [0.1.3 Beta preparation](beta-0.1.3.md#qualification). The source
checkpoints below retain their original scope; they are not new native results.

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
and positive duration. XMLTV channel declarations are optional: programme-only
supplements can reference primary or saved channels. The normal merged SQL
foreign-key transaction rejects actual orphan references without deleting rows.
The existing per-row date filtering remains: a partially usable feed may still
replace its slot and omit rejected rows. This is not completeness detection or
per-event last-good merging, nor a check that listings cover the current day.

The main cache is mandatory. An absent optional cache without a successful
`.source` binding is skipped, allowing an initially unavailable feed to coexist
with a useful primary. A missing previously bound optional cache instead rolls
back the import, preserving all existing rows until recovery. Present enabled
caches must contribute usable programmes. Deliberately disabling a slot removes
its programmes on the next successful import. If both a slot's cache and binding
are externally deleted, previous ownership cannot be inferred; restoring the
cache/binding together is required for this protection.

Ordinary HTTP non-200/request errors retain Beta's notification-only outcome;
XMLTV `.retry` bookkeeping drives fresh attempts without adding a blocking
startup dialog. The existing gzip fallback double-non-200 error branch remains
unchanged (including its XMLTV blocking error dialog). Other FileFetcher callers
retain their prior HTTP outcomes and do not write XMLTV retry markers.

Programmes, source-scoped cleanup and the imported content/configuration key
commit together. Cancellation and import failures roll back. A process exiting
after cache promotion but before import leaves a differing durable DB key, so
the next instance imports without relying on in-memory flags or wall clocks.
An already committed import is reused, not repeated on every redraw.

Existing channel order, visibility, category/lineup, non-null automatic streams,
manual/alternative mappings and reminder/AutoPlay rules survive refresh,
including Reset on Start. Explicit Reset Database remains separate.
The bounded [fresh-profile order follow-up](xmltv-initial-order.md) distinguishes
initial automatic M3U seeding from saved user order without reordering upgrades.

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

### Compatibility checkpoint, 2026-11-25

The four new regressions failed before correction (initial optional absence,
programme-only promotion, tracked HTTP classification and startup dialog).
After correction, **70 tests pass** across `check_xmltv*.py`, service safety and
M3U channel updates. The shared-channel XML fixtures use distinct times and the
real merged importer/schema with foreign keys enabled. Missing/malformed/empty
supplement refreshes preserve its usable cache; an actual orphan rolls back the
database. Staging validation is not a DTD validator or merged-reference preflight:
an orphan-bearing but structurally usable file can be promoted and needs a
corrected feed before DB refresh can succeed. The old DB remains intact.

Static checkpoint only: `/home/kyle/kodi-development/toolkit/.venv/bin/python`,
CPython 3.12.3/Linux, `stub-lanes` reports qualified Nexus 20.5 readiness with
Kodistubs 20.0.1, mypy 2.4.0, checker 0.0.36. Same-interpreter `validate . --branch
nexus --cache /home/kyle/kodi-development/toolkit/.local/index-cache` passes
syntax (Python 3.10 target), manifest and paths; package fails because `issue-85`
is not the manifest ID. Types fail with 941 errors in 47 files; official checker
completes with 4 errors (folder name plus three legacy locale directories) and
57 warnings, including workspace bytecode, API-version advice, complex entry
points and unverified online URLs. This is not a clean static acceptance or a
before/after type comparison. Matrix/Omega/Piers were not rerun in this checkpoint;
their historical limits remain. No native actions were taken; candidate native
upgrade acceptance is separate.
