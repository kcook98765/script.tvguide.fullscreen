# Intended reminder and ordinary AutoPlay event ownership (#21)

## Once cancellation follow-up (21 November 2026 campaign)

The former title-wide DELETE also removed a second once event at a different
start, every same-channel recurring rule and all matching source-wide patterns.
Actual-schema SQLite/producer/context reproduction on `41593d1` confirmed this;
it is not native Kodi evidence. The historical Task13 record below predates this
follow-up and does not imply that removal breadth was already corrected.

* Bare `removeNotification(program)` / `removeAutoplay(program)` now mean **only
  that once event**: source, channel, exact title/start and type0. Repeating that
  intent cannot fall through to recurring/pattern deletion.
* Context/listing and Schedulers Menu actions resolve applicable stored rules.
  One logical rule is unambiguous; several require the existing `Dialog.select`
  UI to choose **one**, with type/title/channel/saved start shown. Cancel, empty
  results or invalid selection do not remove anything. Distinct matching SQL
  LIKE patterns are not guessed or bulk-deleted. Wildcards still match all
  channels **in their source**, including `%`/`_` and existing case behavior.
* An explicit selection carries the exact five stored fields, not a transient
  list index or a title-only fallback. Exact duplicate rows have no distinct
  logical identity and are shown/removed as one rule. Historical NULL channel/
  start values can be explicitly matched with SQL `IS`; no missing identity is
  inferred, no row is migrated, and an intent from another source is declined.
* Existing before/after event cancellation retains shared scoped alarms and
  reminder JSON/token/phase claims when another rule still owns the event.
  The **clicked** event additionally uses the authoritative event predicate,
  so an eight-day-out once overlapped by a recurring rule stays armed even
  outside the normal five-day reconstruction horizon. Nonmatching new/daily
  rules survive, but do not keep an otherwise unowned once action armed.
* Explicit recurring/pattern cancellation removes that rule's occurrences under
  the existing reconstruction horizon, not independent once/rule owners. Global
  Clear All deliberately retains its broader all-source behavior. No unclicked
  horizon expansion, registry, schema/migration, timing, settings, callback-format
  or alarm-identity change. Already delivered/in-flight work cannot be undone.

`tests/check_once_cancellation.py` uses actual FK-on schema1.4.1, timestamp
adapters, model/query/producer methods and the existing inert popup/key adapters.
`--baseline` reads exact `41593d1` and must fail behavioral assertions;
`--mutation once-scope|event-scope|clicked-owner|clicked-autoplay-owner|selection|explicit-rule`
reverts one narrow production property in memory. No native command/callback runs.
Tests include exact survivor alarm-command/callback-byte comparisons in fresh
per-scheduler fixtures, both UI routes, shared ownership inside/outside the
horizon, and duplicates/NULL/stale-source controls.

Inherited recurrence tests now carry an explicit selected-rule tuple; their
occurrence cancellation, source-wide wildcard and Clear All assertions remain.
The old AutoPlay AST freeze excludes **only** the deliberately changed
`_removeAutoplay`; real DB tests replace that freeze with once/explicit recurring
behavior. The other original AST contracts and all padding/callback controls stay.

**Source-only follow-up. Native cancellation/delivery remains unverified.** Full
static gate/checker not rerun; inherited FAIL/warnings remain. New helper asserts
state existing initialized-DB/active-window preconditions, not new lifecycle
handling. The two prior context optional-DB diagnostics remain unresolved under
#2; no suppression or broad typing cleanup. Already-collided unscoped legacy
reminder owners remain unknowable: shared old data/claims are retained while
owned, but explicit final cancellation can invalidate the ambiguous old key.
This is not lost-identity recovery or a precise-second/race guarantee; #21 stays
open for its broader scope. Manifest, Program+service, release and assets unchanged.

> Historical task record: old activation-blocker / whole-campaign UNRUN statements
> below are superseded by the [current overview](modernization-status.md).
> Original failures and feature-specific unverified limits remain; later core
> native evidence is not blanket acceptance of this feature.

Task13 is a focused source/database correction for final review against main,
**not native acceptance**. Its original implementation/evidence base is exact
PR20 commit `d210c1cd199b8c28cb57ec901da98f07ba9b8205`.
PR20 was normally merged as `7b130e1aa17a147e02db49e6bf2ad3f5abc350f7`;
that pinned main was then normally merged into the private Task13 branch,
without rewriting either history. The earlier stacked dependency is resolved.
Refs #21, #14, #4, #6, #7, #1; all remain open.

## Observed before / after, not a native reproduction

`tests/check_schedule_ownership.py --baseline` reads the pinned Git objects.
The normal invocation reads this worktree. Both AST-extract the actual
`Database` methods and actual `Channel`/`Program` classes, without importing
`source`, `utils`, Kodi, stubs, or any legacy module. They use real in-memory
SQLite, `sqlite3.Row`, and **Database.adapt_datetime / convert_datetime**:
Unix `time.mktime` storage and local `fromtimestamp` reads, not ISO timestamps.
Fixtures retain the `(id, source)` channel key and programme
`UNIQUE(channel,start_date,end_date)` constraint; the second source has a
different end time so its otherwise identical event is valid stored data.
Only reviewed pure helpers are loaded. Commands/delivery are inert captures;
JSON is written only into disposable temporary profiles.

| Small fixture / observation | Pinned PR20 | Corrected source |
| --- | --- | --- |
| One ordinary once/always/daily rule; two channels, two sources, repeated title/start | 8 rows, including wrong channel/source/display-channel joins | 1 intended active-source/channel row |
| Ordinary new-only rule with new and rerun episodes | 0 rows | Only literal `is_new == 'New'` episodes; no rerun |
| Daily: next-day same time and another time | Same-time dates selected | Same dates retained; other time excluded |
| Reminder `Show%` rule | 8 mixed-source/channel rows | Both channels in its source, exactly 2 rows |
| Two same-title/start events on different channels | One alarm pair; one reminder JSON record overwritten | Two alarm pairs; two reminder JSON registrations |
| Remove one of those corrected events | Legacy collision prevents independent ownership | Other event's scoped alarms/JSON remain; subsequent clear cancels it |
| Global clear: directly scheduled recurring active-source event 10 days out, plus another source's near event | AutoPlay leaves the far event's pair queued after deleting all rules | No captured queued pairs remain, in either source |

The intermediate active-source-only implementation also failed the global-clear
test (four alarms left). That evidence is retained, not called a pass.
Reminder clear already enumerates all its JSON registrations and also clears
the other-source/far-future case and a pending past-start record explicitly.
Additional captures cover all four AutoPlay clear-query rule predicates,
recurring removal, source-scoped keys, delimiter separation, safe legacy
records/phase claims, and pending callbacks delivered days late.

## Small implementation and preservation boundary

* Only `_getFullNotifications` / `_getFullAutoplays` reconstruction SQL changes:
  join channel/source and rule/channel/source, bind the active source as a SQL
  parameter, and reconstruct type2 alongside always using the existing literal
  `New` flag. Once keeps exact start matching without a horizon; always/new/daily
  retain end-date bounds and the existing five-day default; daily keeps SQLite
  `time(...,'unixepoch')` equality. Adding new-only from a rerun saves the rule
  but does not arm that rerun.
* Historical reminder “regex” is **SQL LIKE**, not a Python regex language.
  The existing `_getProgramList` marker and `_removeNotification` paths establish
  intentional cross-channel/source-local behavior. `%`, `_`, and SQLite's existing
  case behavior remain. No ordinary-channel predicate is imposed on type4.
  Changelog 0.0.93–95 retains AutoPlay and scheduler-list intent; it does not
  override these more specific stored-rule/marker/removal semantics.
* The current digest interface gains optional source/channel inputs encoded as
  an unambiguous versioned JSON tuple before SHA-256. Fixed namespaces/prefixes,
  bounded reminder names, JSON tokens, data callbacks, both reminder phases,
  10000ms/sound=True, before/after and optional stop remain. Text never becomes
  command grammar. Catchup's unscoped interface is unchanged.
* Remove compares scoped identities before/after deleting rules and cancels
  only removed events plus the clicked event when no rule still selects it.
  It also cancels the corresponding known old hashed names, never raw legacy
  commands. For AutoPlay future reconstruction, only that known old pair is
  cancelled before the new scoped pair is armed; past-start callbacks are not
  disturbed by that replacement path.
* **Global Clear All is separate from active-source reconstruction.** Reminder
  clear uses its existing global JSON-name inventory, including late records.
  AutoPlay clear reads a small dedicated DB identity query before deletion:
  all sources, all still-stored matching programme dates, no five-day filter,
  the same once/always/new/daily predicates. It cancels only those scoped and
  known legacy hashes. There is no Kodi CancelAll, scheduler/registry framework,
  profile reset, DB migration, or unrelated SQL cleanup.

## Legacy and delivery limits (not absolute guarantees)

Old reminder JSON has no stored source/channel identity. If its title/start
hash exists, reconstruction retains its **original data, token and phase
claims**, using its old safe hashed alarm names, rather than guessing an owner,
overwriting it with another channel's description, or duplicating delivered
phases. Such an already-collided legacy registration cannot be separated into
two trustworthy owners retroactively. New independent registrations use scoped
keys once that old registration is completed/explicitly cancelled. Explicit
remove may cancel that ambiguous shared legacy registration; it cannot affect
another event's *new scoped* key. Already parsed safe AutoPlay legacy argv and
PR20's canonical data callbacks remain unchanged.

A past-start reminder which cannot be newly scheduled is **not** invalidated by
reconstruction. Pending records have no lateness expiry. Explicit cancel/clear
invalidates their tokens; completed-only cleanup is unchanged. API handoff may
already be in flight: cancellation is not an undo for delivered notifications
or started playback. AutoPlay still uses its existing channel/start playback
markers, not a new transactional playback owner. Service/restart/race/platform
behavior needs native acceptance.

The AutoPlay global clear query can recover only identities whose rule and
programme data are still present. It cannot recover discarded programme rows,
already-deleted rules, unknown/raw historic alarm names, or an already-lost
legacy collision's intended owners. Remove retains the ordinary reconstruction
horizon for *unclicked* recurring occurrences; the clicked event is cancelled
explicitly. No general persistent alarm registry is introduced to hide those
limits. Other Kodi/add-ons' alarms are never enumerated or cleared.

## Focused validation / evidence

Run with the explicitly selected Matrix-lane interpreter:

```text
/home/kyle/kodi-development/toolkit/.local/matrix/bin/python -I -B tests/check_schedule_ownership.py --baseline
/home/kyle/kodi-development/toolkit/.local/matrix/bin/python -I -B tests/check_schedule_ownership.py
```

Local evidence is outside the worktree/package in the common Git directory:
`.git/modernization-evidence/task13-*`. It includes original stdout/stderr,
commands and actual `subprocess.returncode`, before/intermediate/final captures,
initial fixture uniqueness failures, and the initial typing-harness failure.
These are diagnostic history, not passing tests. Evidence and Git/config files
are not copied into validation/runtime snapshots or committed.

Intended shared runtime syntax is Python3.8 stdlib, for Matrix19.4, Nexus20.5,
Omega21.3 and Piers22RC2. The available Matrix static lane is **19.5**, not a
native19.4 substitute: CPython3.12.3 tools, Kodistubs19.0.3, mypy2.4.0,
checker0.0.36. Changed-file Python3.8 AST and narrow helper/callback typing are
separate from full-addon qualification. The wrong-signature API control must
actually exit1 with its three expected diagnostics; existing unsafe-source,
raw-command, punctuation/data and legacy-callback controls remain intact.

Only one release lane is used for bounded full static comparison, not a new
four-lane gate. Original six-stage failures/warnings and prior negative controls
remain; no metadata/typing cleanup is in scope. Cached offline URL checks remain
unverified. Full static validation is **not a pass** (see review receipts).

Pre-integration receipts: `task13-final-summary.json`, `task13-final-syntax38.json`,
`task13-validation-baseline-matrix-six-stages.stdout`,
`task13-validation-final2-matrix-six-stages.stdout`, and
`task13-validation-final2-review.json`. Seven focused ownership tests, six
reminder tests, six AutoPlay-data tests, four fixture tests (23 total), plus
command-data/safety/Python3 scripts exit0. The API-negative control exits1 with
three expected argument-type errors. Changed-file Python3.8 AST and narrow
Matrix helper/callback typing pass. Initial test-harness failures and a temporary
new optional-connection diagnostic are retained; the new DB operation now
asserts its initialized connection precondition rather than ignoring typing.

| Matrix runtime-only snapshot stage | Exact PR20 baseline | Reviewed pre-integration Task13 |
| --- | --- | --- |
| Syntax / manifest / paths / package | PASS / PASS / PASS / PASS | Same |
| Full-addon types | FAIL, exit1, 652 errors | FAIL, exit1, 652 errors |
| Official checker | FAIL, exit1, 73 errors, 10 warnings | Same |
| Overall validator subprocess | exit1 | exit1 |

Normalized type diagnostics (including multiplicity) have no added/removed
lines. Runtime-only snapshots exclude Git/config/evidence/docs/tests/tools;
their inventory hashes are retained privately. Historical broader receipts
(including 651-error/11-warning snapshots with different input composition)
are **not overwritten or reclassified**. All ten current original warnings,
legacy escape warnings, and historical warnings remain in raw outputs.
Cache manifest SHA256 is
`6ee4ed59f94aafd48469336f06e8ffb7286786e3d1e7607dcbb6e75f956c5f9f`
(2026-10-20); no refresh/download was performed. These snapshots are local
validation inputs, not released/installed ZIPs or new native evidence.

## Main reconciliation for final source review

Initial independent review accepted the focused source direction at
`0a8a78289518f2cdae1ddef0617456b8b05046c3`. A normal, conflict-free merge of
pinned main `7b130e1aa17a147e02db49e6bf2ad3f5abc350f7` produced
`abc79d038955f9f501851cbf5c4fe3a3ea975537`, with those two commits as its
ordered parents. No rebase, force push or other worktree/ref changes.

`task13-main-preservation.json` records Git blob/mode identities: **all 922
files outside the eight Task13 files exactly match pinned main**. This includes
the combined PVR, skins and metadata source/resources/tests. The four runtime
files (`source.py`, `notification.py`, `autoplay.py`, `command_safety.py`) remain
byte-identical to the independently reviewed Task13 head and retained validation
snapshot. The data helpers, fixed callbacks, manifest and both declared entry
points are likewise unchanged. This is preservation evidence, not a native pass.

`task13-main-check-summary.json` records actual subprocess returncode0 for the
pinned-baseline reproduction and all ten combined pure scripts: ownership,
reminders, AutoPlay data, PVR, custom skins, metadata search, command data,
safety, Python3 and native-fixture **source** checks. Raw stdout/stderr, existing
warnings and Python3.8 syntax evidence (`task13-main-syntax38.json`) are retained.
No full static comparison was rerun for the integrated tree. The earlier narrow
API/type and expected-negative evidence is reused only because its runtime
helpers/callbacks are unchanged; it does not qualify the newly combined tree or
resolve existing broad failures. Final independent review and any merge remain
separate; no PR merge has been performed.

**All four native stages remain DEFERRED/UNRUN for this task.** The owner has
deferred the [Lab394 infrastructure dependency](https://github.com/kcook98765/kodi-lab/issues/394).
No further native/Lab retries, research, workarounds or modifications are part
of Task13. The historical
[Lab112 comment](https://github.com/kcook98765/kodi-lab/issues/112#issuecomment-7023719173)
is context only. A video-smoke refusal would not establish whole-add-on failure;
genuine native acceptance must include service execution evidence as well as
the Program entry point. Both declarations and their original source paths
remain unchanged; all remaining provisional feature gaps remain open.
No Lab calls, profiles, source inputs, workspace/grant/settings changes,
lifecycle, selection, Reset, enable/deploy/launch/smoke, UI, logs, screenshots,
production, infrastructure, Toolkit edits, or release/distribution publication.
The complete Program+service manifest, dependencies, GPL/history and other
preservation work remain intact. No permanent feature removal is proposed.
