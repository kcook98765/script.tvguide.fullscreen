# Fresh-profile XMLTV order — Beta 0.1.3 / PR #92 follow-up

Later clean isolated Omega order-off/order-on and repeated-open evidence is in
[0.1.3 qualification](beta-0.1.3.md#qualification). The original source-only
checkpoint and proposed handoff below are retained; later finite evidence does
not qualify every proposed native case or the still-pending versioned 0.1.3 ZIP.

Source-only change based on PR #92 head `548b674`. No release/version change,
native Kodi actions, upload, push or merge are part of this turn.

## Startup and ownership

`Database.__init__` loads optional files and constructs the source/cache producer
before the DB event loop runs `_initialize`. Initialization opens SQLite, enables
foreign keys, runs `_createTables`, then snapshots watched settings.

Foreground `onSourceInitialized` exports saved channels, reconstructs schedulers,
calls `loadChannelMappings`, and only then redraws/imports XMLTV. The first M3U
save therefore assigns weights before XMLTV has seen a declaration. A second
M3U save applies **explicit** `mapping.m3u.order=true` weights. Service startup
constructs `Database(True)` and imports in `onInit`; it does not load M3U mappings.

An empty programme history, epoch channel timestamp, missing cache receipt,
`settingsChanged`, or channel weights resembling a playlist cannot establish a
fresh profile. In particular, published Beta **0.1.2** has no #92 import receipt.

## State transitions (no schema migration)

The existing `settings(key,value)` table holds one private provenance record:
`xmltv.initial.order=pending`.

| State/event | Result |
| --- | --- |
| First schema creation, no existing SQLite tables, XMLTV source | Commit `pending` with schema initialization. |
| Any existing database without that record | Never infer freshness or create the record, even with empty history. |
| Automatic foreground M3U seed | Insert missing channels only; keep pending provenance. Never overwrite an existing row from a potentially stale foreground read. |
| User channel save or explicit M3U reorder | Delete pending provenance in the same save transaction. Existing chosen weights become authoritative. |
| First successful XMLTV import, pending, M3U order off | Assign declaration order once; first occurrence of a duplicate ID wins across primary/secondary/tertiary iteration. |
| Undeclared/M3U-only rows on that first import | Retain after declarations in prior weight/rowid order, including the synthetic catchup row. |
| Successful XMLTV import | Remove provenance with programme changes and imported cache key in the existing transaction. |
| Cancellation, empty import, parser/SQL/commit failure or process exit during import | Roll back the import; committed seed/provenance remains for retry after restart. |
| Subsequent imports, refreshes and restarts | Preserve saved weights and visibility; append new rows with the established source-scoped max-weight+1 rule. Retain absent channel rows, mappings and rules; successfully refreshed programmes reflect current membership. |

Explicit M3U order remains authoritative. A service-first import can finish
before foreground startup applies that explicit playlist order. No channel
delete/replace/recreation is added. The schema stays **1.4.1**; exact Beta-created
`sqlite_master` definitions are checked unchanged on initialization. Generic
channel saves and non-XMLTV providers retain their established behavior.

#92's producer/cache identity, HTTP/VFS outcomes, optional-source routing,
writer locking, rollback and provider code are unchanged. Automatic XMLTV M3U
seeding is now insert-only so a service import between foreground read/save
cannot restore incidental old weights or visibility. The explicit reorder path
still updates weights. Existing M3U mapping/category merge behavior is not
redesigned; the XMLTV importer never takes ownership of those saved values.

## Deterministic source evidence — 2026-11-25

`tests/check_xmltv_initial_order.py` adds **13 methods** using extracted production
initialization, schema/adapters, M3U loader, XMLTV constructor/parser/importer,
public blocking channel-save wrappers, and foreground/service callbacks. DB
dispatch and redraw are synchronous adapters, not a Kodi event-loop simulation.
Inputs are synthetic local fixtures; URLs use `example.invalid` only.

- XMLTV order: `zulu, alpha, mike`; M3U order:
  `mike, zulu, alpha, playlist-only` (neither is alphabetical).
- Fresh explicit off/on; merged/duplicate declarations and stable undeclared tail.
- Failed initial import/retry with persisted DB and source reconstruction;
  interruption after seeding; cancellation, empty input and deferred FK failure
  at commit, after order/key bookkeeping, each preserving all committed rows.
- A separate interpreter calls `os._exit(0)` with the first import transaction
  open. Reopening recovers the committed seed, pending provenance and zero
  programmes, then completes XMLTV ordering. Disposable child caches belong to
  the parent fixture and are cleaned after process exit, not while locked.
- Exact published `8fe6ede` Beta 0.1.2 schema creation plus populated/customized
  and empty-history profiles, without either new receipt/provenance: preserved
  channel rowids/weights/hidden state/lineup, categories, manual/alternative
  mapping values, reminder/AutoPlay/AutoPlayWith rules over repeated foreground
  loads, refreshes and DB reopen.
- Membership additions/removals retain old rows and append additions in encounter
  order; user edits before first success cancel seeding ownership.
- Both foreground-first and service-first callbacks, explicit off/on, repeated
  callbacks, and service import interleaved between M3U read/save. Mapping saves
  legitimately advance `sources.channels_updated`; that timestamp is not claimed
  byte-identical. Other source save policy is a separate control.

Negative control: before editing, fresh-off failed with actual M3U order. The
bounded `--baseline` replay reads only `source.py`/`gui.py` at `548b674` via Git,
without checkout. Its selected fresh-off test **fails as expected**, while
explicit-on and existing customized Beta-profile preservation **pass**. This
distinguishes the new decision from #92 behavior already working.

Final checks: **130 unittest methods pass**, plus **two assertion scripts**:

```sh
python3 -m unittest discover -s tests -p 'check_xmltv*.py'  # 78 (65 existing + 13 new)
python3 tests/check_m3u_channel_updates.py                # 2
python3 tests/check_service_safety.py                     # 5
python3 tests/check_channel_listing_source.py            # 5
python3 tests/check_channel_search_empty.py              # 5
python3 tests/check_reminders.py                         # 6
python3 tests/check_autoplay_data.py                     # 10
python3 tests/check_schedule_ownership.py                # 7
python3 tests/check_typed_mappings.py                     # 12
python3 tests/check_dependencies_settings.py             # assertions
python3 tests/check_python3.py                           # assertions
git diff --check
```

Regression interpreter: `/usr/bin/python3`, CPython **3.12.3**, Linux, SQLite
**3.45.1**. Available requests **2.31.0**, dateutil **2.8.2**, pytz **2024.1**,
Pillow **10.2.0**; BeautifulSoup is not installed in this interpreter but is not
used by these extracted paths. No selected case was skipped for a dependency.
Python **3.8** grammar passes for both changed runtime files and the new suite;
the existing Python compatibility assertion script also passes. Legacy invalid
escape/deprecation warnings remain, and intentionally injected import failures
print expected tracebacks. An intermediate whole-snapshot assertion was corrected
to account for the legitimate M3U channel timestamp update; the final rerun passes.

## Outstanding validation and proposed PR update

The current Toolkit development, validation and version-compatibility skills
were loaded. Sandbox access denied both the requested Claw `AGENTS.md` and
managed-v2 skill reference files. The documented Nexus isolated interpreter's
`stub-lanes` invocation was also denied before execution; matching Toolkit
validation/types/official addon-check therefore remains **NOT RUN**, not passed.
No alternate interpreter is presented as a substitute static lane. Existing
Matrix/Nexus/Omega/Piers qualification limits and historical warnings remain;
no fresh version-specific compatibility claim is made here. Obtain those
permissions and run branch-matched static validation before claiming acceptance.

Suggested #92 update (draft only, not posted):

> Implemented the bounded fresh-profile ordering decision: XMLTV declarations
> win on first successful import with M3U order off; explicit M3U order wins.
> A new-DB-only settings marker survives failed imports/process restart and is
> consumed atomically, or cancelled by a user save/explicit reorder. No schema
> migration or channel deletion is added. Existing Beta 0.1.2/customized profiles
> without provenance are never reordered; additions append and absent rows stay.
> Automatic M3U seeding is insert-only to avoid a stale foreground save undoing a
> service import. 130 methods plus two assertion scripts pass, including 13 new
> regressions. Baseline fresh-off fails while on/upgrade controls pass. #92 cache,
> HTTP/VFS, locking, rollback, optional sources and provider behavior are retained.
> Toolkit static validation is permission-blocked and native acceptance remains
> pending; this is not release or merge approval.

Native acceptance still needs an authorized **kodi-managed-lab** round: genuinely
fresh off/on profiles, failed-first-import recovery/restart, exact 0.1.2 upgrade
with customized hidden channels/mappings/categories/schedulers, membership
refresh, and real foreground/service event-loop behavior. Source callbacks and
SQLite process-exit tests do not qualify Kodi UI, installer, scheduler execution,
cross-platform filesystems or runtime concurrency. Do not use external Kodi or
production feeds for those tests.
