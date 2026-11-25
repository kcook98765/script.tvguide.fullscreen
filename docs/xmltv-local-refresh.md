# Same-path XMLTV refresh (#85)

## Source correction; native qualification still required

The 0.1.2 Beta baseline is `0c4a3c3`. Before runtime edits, five new
production-path fixture methods failed with **13 assertions**, including all
nine primary/secondary/tertiary × newer/equal/older source-timestamp cases.
The guide parser kept `Old` / `Removed` instead of `New` / `Added`.
Other assertions detected malformed cache promotion, primary-only freshness,
unnecessary unchanged-cache replacement and a committed partial import after
10,000 items. The initial fixture run also exposed a test-inheritance setup
mistake; the corrected five-method baseline run is the reproduction evidence.

Historical context: #37 / PR #38 fixed source *identity*, not same-path
content; PR #34 established additive channel preservation. PRs #44 / #64 / #67
retain slot offsets, unusable-row handling and missing-name behavior. Both
`origin/krypton:fileFetcher.py` and its XMLTV source contain interval/timestamp
shortcuts too: the historical source inspection does not prove the reporter's
older installation behaved differently.

## Semantics and preservation boundary

- Only source-tracked XMLTV local/Kodi-VFS files bypass the HTTP cache interval
  and source-mtime shortcut. Construction on reopen or supported background
  update copies through `xbmcvfs.copy`, decodes gzip, validates, and compares
  decoded content. Equal/older/coarse or unavailable VFS timestamps are not
  evidence of unchanged content. There is no filesystem watcher/live polling.
- Identical decoded/repaired local content leaves the cache, binding and
  database alone. Source-identity changes still establish the existing hashed
  `.source` marker even for identical content. Other FileFetcher callers keep
  their historical behavior. HTTP interval, explicit force, MD5 reuse/auth and
  gzip fallback retain their transport behavior; freshness checks do not fetch
  HTTP sources.
- Before cache promotion, the actual streaming XMLTV parser/models validate
  the staged bytes with optional legacy entity repair. Validation suppresses
  logo lookups, progress UI and category-count output. Missing, malformed,
  wrong-root, failed and zero-usable-programme inputs retain the old cache and
  source binding and remain retryable. Zero usable programmes are deliberately
  treated as failure, not permission to erase the guide.
- A content/configuration digest covering enabled slots and their identity
  markers is recorded in the existing DB `settings` table as
  `xmltv.imported.cache`, **in the successful import transaction**. No schema
  or user-setting migration is required. A legacy database imports once
  additively; no channel/DB reset is required. Secondary/tertiary-only changes,
  disabled slots, missing update bookkeeping and timestamp precision are not
  inferred from the primary cache's wall clock.
- XMLTV imports no longer globally delete update rows or commit every 10,000
  items. Deletes/inserts/fill adjustments and freshness commit together for
  XMLTV only. Cancellation, empty imports and SQL/model failures roll back;
  retry state survives. Existing programmes can still be returned by normal
  and Quick guide getters after a failed refresh.
- Existing channel identity, order, visibility, category/lineup and non-null
  automatic stream mapping survive XMLTV refresh, including the legacy
  refresh-ON/keep-channels-OFF path. Manual/alternative mappings, reminder and
  AutoPlay rows and other sources are not reset. Omitted channels remain;
  removed programme events do not. Explicit Reset Database is unchanged.
- A separate SQLite coordination file, `xmltv.cache.lock`, serializes XMLTV
  cache writes and imports across Kodi interpreters. Its OS lock is released
  by connection close/process exit; **never unlink that file**. A busy attempt
  defers without stealing the owner's lock and retries on a subsequent normal
  operation/reopen/service run. Existing `db.lock` compatibility is retained.
- The legacy programme uniqueness constraint omits source. A conflicting
  other-source event therefore fails/rolls back the XMLTV import rather than
  silently replacing that event; resolving the schema limitation is deferred.

## Reproducible source checks

No add-on/Kodi/stub module is imported or executed by these fixtures. They
extract the production constructors, fetcher, parser/models, real SQLite
schema/adapters, freshness check and importer with explicit synthetic adapters.

```sh
python3 tests/check_xmltv_local_refresh.py --baseline LocalRefresh.test_same_path_changes_each_slot_with_new_equal_and_older_mtimes LocalRefresh.test_unchanged_local_does_not_replace_or_import LocalRefresh.test_malformed_cache_keeps_last_good_and_retries LocalRefresh.test_enabled_secondary_cache_is_checked_without_need_reset LocalRefresh.test_import_failure_after_10000_items_keeps_entire_database
python3 -m unittest discover -s tests -p 'check_xmltv*.py'
python3 tests/check_m3u_channel_updates.py
python3 tests/check_service_safety.py
python3 tests/check_python3.py
python3 tests/check_safety.py
python3 tests/check_dependencies_settings.py
python3 tests/check_command_data.py
git diff --check
```

The fixed-revision `--baseline` replay does not check out or modify runtime
files; those five methods must fail. Final focused XMLTV coverage is **45
passing methods**, including 14 new methods, the nine same-path cases through
real parser **and DB rows**, optional slots enabled alone, VFS URI/gzip,
entity repair, failed-source retry, mapping/rule/other-source preservation,
interleaved fetch/import locks and late failure/cancellation/SQL rollback.
M3U (2) and service safety (5), plus the four listed standalone assertion
scripts (including conservative Python 3.6 grammar/API guards), pass. Historical
invalid-escape warnings and expected injected-failure tracebacks remain.

Host checks used `/usr/bin/python3`, CPython 3.12.3/Linux x86_64; this is **not**
Kodi's embedded Python or version-specific Toolkit acceptance. The documented
Omega interpreter's `stub-lanes` command was denied by the task permission
policy; no matching types/checker pass is claimed. `../LEDGER.md` and nested
Toolkit reference-file reads were also denied. A plain invocation of the
separate official-pytz check failed its explicit isolated-interpreter/library
precondition; it was not a dependency qualification.

Final full-suite discovery ran **244 methods**, ending with **7 assertion
failures (including subtests) and 1 import error**; it is not an all-green gate.
Package metadata needs missing `polib`; artwork tests assert historical
README/manifest text; a historical
exact-payload license test also rejects later skin changes and these intended
runtime changes. License/header text, manifest/version, settings XML, skins
and entry points are untouched by this correction.

## Separate native steps (unrun in this source session)

Use **kodi-managed-lab**, current authenticated tools, the acquired owner lease
and Codex-provisioned disposable profile/generation only. No external Kodi,
user profile, production package or provider setting is authorized here.

1. **Exact-Beta reproduction:** verify the published 0.1.2 ZIP/checksum and
   baseline installed bytes. Use a small synthetic current-window XMLTV feed
   with stable channel IDs; save harmless manual/automatic/alternative mappings,
   order/hidden/category state and reminder/AutoPlay rules. Snapshot through
   supported tools. Keep refresh OFF and the 24-hour interval. Change title,
   times and add/remove events at the *same path*, then reopen normally and
   exercise the supported background update path. Record source/cache hashes,
   read-only stopped DB rows and rendered guide. Repeat equal/older timestamps
   and each enabled optional slot independently. Save the baseline failure.
2. **Newly packaged acceptance:** independently package the reviewed commit
   without a version change, record ZIP and source hashes, install through the
   native installer in the approved disposable upgrade profile, then confirm
   fresh execution. Repeat the exact reproductions; include unchanged input,
   force, missing/malformed/empty/recovered files, gzip/VFS and synthetic HTTP
   interval/failure controls. Check DB integrity and every preserved field/rule
   before/after; qualify foreground/service overlap without deleting locks or
   journals. A source-test pass or deploy/launch acknowledgement is not native
   acceptance. Archive logs/screens/preservation receipts and stop/release.

Large local/VFS feeds now incur a full copy/validation on source construction,
and cached content hashing on freshness checks; XMLTV imports use one larger
transaction. Measure I/O, latency and memory on the actual Kodi/platform.
Generated category counts are still derived parser output, not transactional
user category mappings. Abrupt termination can still leave the pre-existing
legacy `db.lock`; no ownership-blind cleanup/reset is introduced. Producers
should publish complete XML atomically rather than writing a live feed in place.
