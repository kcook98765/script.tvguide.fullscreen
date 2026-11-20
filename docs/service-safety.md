# Task18 — service startup safety and bounded schedule repair

Refs #2 / #3 / #7 / #14 / #1. Source-only, pending independent review.
Base: `6d1b9162289ccc20c3ba089302dc3a149150d0be`;
branch: `fix/service-startup-safety`. No release/distribution authorization.

## Confirmed startup defect and ownership trace

At the base, `service.py` main unconditionally deletes `source.db-journal`
and `db.lock` **before** checking `autostart` or `background.service`. Neither
filename establishes ownership; both deletes happen with both settings disabled.
The new startup does neither, and does not substitute stale-file detection,
lock stealing, database reset, or another cleanup framework.

Primary basis, read before changing the code:
[SQLite file locking, sections 4, 4.1 and 6](https://www.sqlite.org/lockingv3.html).
SQLite writes pre-change pages into `database-name-journal`; a hot journal can
be necessary after interruption. SQLite checks/replays it under its own locks
before reading the DB. Deleting it can prevent rollback and leave the database
inconsistent. A leftover filename alone does **not** prove a journal is hot,
stale, or safe to remove. This patch leaves that decision to SQLite.

Existing `source.py` at the base (unchanged here):

* `Database.__init__`, lines 111–114: translated add-on profile + `source.db`.
* `_initialize`, lines 316–362: `sqlite3.connect`, foreign keys, dummy lock-check
  table and existing schema setup. SQLite remains responsible for normal
  journal recovery. Operational locking errors take the existing bail/retry path.
* `_close`, lines 368–376: rollback uncommitted changes, then close.
* `_updateChannelAndProgramListCaches`, lines 455–478 and 619–651: an existing
  `db.lock` causes an early return; an update that proceeds creates the marker,
  uses its existing transaction/error paths, clears `updateInProgress` and closes
  the cursor in `finally`, then deletes the marker on the normal continuation.
  **The marker delete is after, not inside, `finally`.** No marker acquisition,
  SQL, data, schema, transaction, threading or normal cleanup code is changed.

### Retained maintenance / database limitations

The marker protocol is not atomic, contains no owner identity, and can leave a
marker after a crash or an exception escaping cleanup. Removing the blind startup
delete deliberately means a genuinely stale `db.lock` can continue blocking
updates. Restarting the service no longer promises to clear it. There is no safe
automatic ownership inference here and no new maintenance UI. If such a marker
needs intervention, an administrator must first establish that **all** guide and
update users of that exact profile are stopped and arrange profile backup and
explicit maintenance. Do not delete SQLite journals as stale-lock maintenance.
A supported ownership-aware/manual UI would be a separate reviewed task.

Also retained, not endorsed as newly safe: `_initialize`'s pre-existing
`sqlite3.DatabaseError` branch can unlink a purportedly broken database. This
patch does not reach into that separate recovery/concurrency policy or claim to
make the entire DB lifecycle nondestructive. `ResetDatabase.py` / Reset Everything
remains a separate explicit user action, unchanged and not called by this patch.
No real profile or database was opened or modified during testing.

## Confirmed scheduler defects and exact fallbacks

The old daily branch leaves `timeLeft` unset for an empty time; missing colon,
out-of-range hour/minute, bad interval and invalid timestamp conversions can
abort the service. Literal legacy default `service.type=Period` accidentally
takes the daily branch, despite the numeric enum's `0` period meaning.

The small stdlib-only `_time_left` function stays in `service.py` and reads the
same saved strings; it does not rewrite schedule settings:

| Input | Behavior |
| --- | --- |
| type `0`, `Period`, empty or unknown | Period schedule; unknown/empty falls back to period |
| type `1` or `Time` | Daily schedule |
| interval `0` / `1` / `2` / `3` | Unchanged 7200 / 21600 / 43200 / 86400 seconds |
| malformed/empty/unknown interval | Existing six-hour default |
| valid previous update timestamp | Existing local `fromtimestamp` + interval arithmetic |
| empty history | Existing epoch/due-now semantics |
| malformed/nonfinite/platform-out-of-range timestamp | Due now; normal dispatch records fresh history, subsequent iteration waits the interval |
| valid daily hour/minute | Existing local-naive replace, roll forward 24h only when earlier than now |
| empty/malformed/out-of-range daily time | Existing declared daily default **03:33**, today or next day using the same rule |

Whole-second truncation, zero-delay due updates, valid daily equality semantics,
local-time/DST limitations and the real `Monitor.waitForAbort(timeLeft)` remain.
No polling loop or arbitrary minimum/maximum wait was introduced. An additional
abort check before dispatch closes the old zero-wait abort gap. The existing
seconds-to-wait DEBUG message remains; the redundant interval-only debug message
is no longer emitted by the extracted arithmetic. Settings changes still take
effect on the existing iteration boundary, not through a new live scheduler.

Autostart, login update, fixed folder update, cache update, finish notification,
reminder and ordinary AutoPlay reconstruction remain in their original control
flow. Service callbacks are unchanged. There is no reminder/adapter/UI change,
new API, dependency or database. Task14 owns declarations/defaults/catchup; the
legacy consumer contract was communicated on issue #3 for normal later merge.

## Focused regression evidence (not native acceptance)

From this worktree, with an environment containing only `PATH=/usr/bin:/bin`:

```
/home/kyle/kodi-development/toolkit/.local/matrix/bin/python -I -B tests/check_service_safety.py
/home/kyle/kodi-development/toolkit/.local/matrix/bin/python -I -B tests/check_safety.py
/home/kyle/kodi-development/toolkit/.local/matrix/bin/python -I -B tests/check_command_data.py
/home/kyle/kodi-development/toolkit/.local/matrix/bin/python -I -B tests/check_python3.py
```

Five service tests cover baseline deletions as AST **data only**, actual extracted
baseline arithmetic failures/wrong default selection/zero-wait abort, current
helper period/daily/fallback arithmetic, actual main-body captures with disposable
journal/lock/DB sentinels (including both settings disabled), abortable waits,
fresh-history recovery to a six-hour wait, startup/folder calls and callback
reminder/AutoPlay/notify data. No whole legacy module or Kodi/stub is imported.
Sentinels are not real/hot journals; these captures do not demonstrate SQLite
crash recovery, native startup, real scheduling, display or DB concurrency.

The original command test's whole-service equality was narrowed **only** over the
reviewed arithmetic, added abort check and removed startup deletes/import. AST
equality still protects all other module/control-flow bytes semantically; callback
and literal command comparisons are explicit. Original RCE/TLS/source/raw-command
and delimiter negative controls remain, not relaxed to accept a failure.

Private complete stdout/stderr is under the owned Git admin directory
`.git/worktrees/task18-service-safety/evidence/`, outside tracked/runtime content.
The initial pre-edit run retained the confirmed negative controls and three
expected missing-helper test errors (not a native failure). Final focused runs
exit 0; existing invalid-escape SyntaxWarnings remain in the source checks.
Changed-file Python 3.8 grammar is checked; tool Python is not embedded Python 3.8.

No broad six-stage/four-lane gate was rerun. Prior six-stage results, type/checker
failures, warnings and negative controls remain historical, not passes for these
bytes. Matrix19.5 static stubs do not establish Matrix19.4 native compatibility;
Piers remains bounded RC2. Intended releases remain **Matrix19.4 / Nexus20.5 /
Omega21.3 / Piers22RC2**, with both script and service manifest entries retained.
**Lab394 remains DEFERRED.** No Lab/native/profile/Toolkit/config/production call
or change, lifecycle/import/deploy/launch/smoke, UI/navigation/screenshot/log work,
packaging, release or distribution. No runtime generation/identity/receipt exists
for this task. Original master/history, GPL and upstream credit are preserved.
Stop at draft PR for supervisor review; do not merge.
