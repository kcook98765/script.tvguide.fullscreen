# Ordinary AutoPlay data preservation (task11)

> Current notice (2026-11-21, unreleased): historical VPN-preservation statements
> below no longer describe current behavior. The scheduled VPN-only block is
> intentionally removed; callback guards, markers and verbatim media URLs remain.
> See [removal scope and limits](vpn-manager-removal.md).

> Historical task record: old activation-blocker / whole-campaign UNRUN statements
> below are superseded by the [current overview](modernization-status.md).
> Original failures and feature-specific unverified limits remain; later core
> native evidence is not blanket acceptance of this feature.

Refs #14, #7, #6, #1. Focused source repair, **not native acceptance**. Built on
`c96189c7a7a9d5ad20f8946d280166be0aa15e69`, the normal PR17 merge whose tree
equals reviewed `d712b23`. Original master remains `0e46733`.

## Data boundary and callback compatibility

Previously ordinary `autoplay.py` refused channel IDs containing apostrophes,
commas, parentheses, quotes or backslashes because it interpolated them into
nested AlarmClock/RunScript grammar. That provisional PR12 loss is not necessary.
Both fixed bundled callbacks now receive **one** opaque data argument:

```
v1_<unpadded URL-safe base64 of compact UTF-8 JSON [1,channel,start]>
```

`autoplay_data.py` bounds the decoded JSON to **65536 bytes** and bounds the
encoded token before decoding. It requires the exact version/schema, nonempty
text identities, strict `[A-Za-z0-9_-]` encoded alphabet and exact canonical
re-encoding. Padding, whitespace, alternative JSON escapes, noncanonical pad
bits, malformed UTF-8 and extra fields are refused. No punctuation/Unicode
normalization or character-denying channel rule is applied. The bound is a
transport/resource limit, not a Kodi-tested maximum command length.

Only the existing title/start digest name, a fixed installed `play.py`/`stop.py`
path, encoded payload, integer delay and fixed flags enter emitted grammar.
Channel **and start identity** are encoded; neither is interpolated raw. Decoded
values go to a parameterized SQLite lookup and existing settings markers, never
back into a builtin. Media remains `Player.play(item=url)` data. Imported `@` or
command-looking mappings are not interpreted as builtins or executable code.
No profile code, downloads, shell, arbitrary callback path or command execution
is introduced. `is_builtin_data` and its other boundary controls are unchanged.

The ordinary legacy callback entry `play.py channel start` / `stop.py channel
start` remains supported **as already parsed argv data**, subject to the same
bounded nonempty-text identity checks. The new form has one data argument; the
legacy form has two. A legacy ID beginning with `v1_` (even one equal to a valid
encoded packet) therefore remains that exact channel ID. Missing/extra arguments
and invalid new packets log only a fixed message and return before Addon/settings,
path translation, SQLite connection or playback. Legacy producers must not
interpolate raw untrusted text into command grammar; this add-on no longer does.

## Preserved behavior and small cancellation correction

- Once/always/daily selection and DB rows, GUI choices, service reconstruction,
  before/after settings, optional stop, whole-minute floor calculations and
  defaults are unchanged. No lateness expiry, new recurrence or catch-up rule.
  Even the inherited negative pre-padding interval behavior is retained; this
  task does not claim to repair every scheduling edge or inherited SQL rule.
- The callback still uses the custom stream mapping and existing optional VPN
  branch. It records exact `playing.channel`/`playing.start` data before playback;
  stop compares both, clears both and dispatches only fixed `PlayerControl(Stop)`.
  The SQLite read connection is now closed, and failed connect returns safely.
- Demonstrated bug: DB remove deletes the whole matching rule, but only the
  selected occurrence's alarm pair was cancelled; clear deleted rows/markers
  without cancelling pending alarms. Remove now cancels disappeared occurrences
  from before/after DB event snapshots plus the selected pair; clear cancels the
  DB-selected event pairs before the existing clear-entry marker reset.
- This is **not** a registry, nonce/claim protocol or concurrency redesign.
  Cancellation covers DB-selected events (including the existing five-day
  recurring horizon), not arbitrary orphaned alarms or old unsafe raw names.
  Existing title/start digest collisions, snapshots becoming stale during a
  concurrent service refresh, and already-dispatched callbacks remain limits.
  Cancel cannot retract an in-flight callback. Settings ownership is not a native
  player-instance lock: manual/external playback can outlive those markers, and
  repeated callbacks are not made at-most-once. Captures are not proof of native
  race safety.

## Focused evidence and remaining gates

`tests/check_autoplay_data.py` runs six small pure/AST tests, without host Kodi,
stub imports or legacy-module initialization. It captures actual producer
commands and feeds their encoded arguments into extracted callback functions;
checks exact apostrophe/comma/parenthesis/quote/backslash/Unicode and inert
command-looking data, parameterized in-memory SQLite lookup, media-as-data,
legacy-prefix disambiguation, before/after/optional-stop/reconstruction,
add/remove/clear, unchanged selection SQL and retained DB row types. Malformed,
oversized and noncanonical packets cause only the fixed error log: no settings,
database initialization, playback or stop. Mismatched stop identities do not stop.
It is not a Kodi grammar emulator, full scheduler suite or native test.

The six other focused scripts (command data, source safety, Python3, reminders,
fixtures and PVR) independently exit **0**. Original unsafe-source/raw-command
negative controls remain; only the AutoPlay assertion requiring benign-data
refusal changed to assert encoded wiring. Changed runtime/tests parse with
Python3.8 grammar; the new helper uses Python3.8 stdlib APIs. Host CPython3.12
does not establish embedded Python3.8 behavior.

Narrow Matrix19.5-stub mypy for `autoplay_data.py`, `play.py`, `stop.py` exits **0**.
The explicit interpreter is Toolkit `.local/matrix/bin/python`, CPython3.12.3,
Kodistubs19.0.3, mypy2.4.0, checker0.0.36; `stub-lanes` ran first. A wrong-type
Player/settings/path/builtin control exits **1** with four argument diagnostics.
This is static signature reading, not stub execution or native Matrix19.4 proof.

Private receipts stay under `.git/modernization-evidence/task11-*`, never a runtime
export. `first-*` retains the failed pad-bit test-vector assumption and initial
direct-mypy import-untyped diagnostics (not valid API negative evidence); `review-*`
records the corrected final checks, subprocess returncodes and source hashes.
The task02/task05 evidence is retained unchanged. Existing GUI invalid-escape
warnings (11 per GUI parse), other inherited source warnings and failed controls
are not suppressed. No broad four-lane/CLI rerun: all six historical stages and
raw failures remain. In particular task07 Nexus validation **exited 1**, with
syntax/manifest/paths/package passing, types **FAIL651**, official checker
**FAIL73 problems / 11 warnings**. That receipt does not validate these new bytes;
neither does task03's older four-lane evidence. No new broad PASS is claimed.

Common main still targets Matrix19.4/Nexus20.5/Omega21.3/Piers22RC2. Matrix tools
are the qualified 19.5 major lane; Piers remains bounded prerelease evidence.
All native task08–11 stages are **unrun**. Full Program+service intake/structural
validation previously succeeded, but the observed installed enablement excluded
mixed manifests and qualified pure services only on Omega; historical evidence:
[Lab112](https://github.com/kcook98765/kodi-lab/issues/112#issuecomment-7023719173).
The latest owner decision is [Kodi Lab394 **DEFERRED**](https://github.com/kcook98765/kodi-lab/issues/394),
not an invitation to retry the blocker or introduce a workaround.
No native alarm parsing, playback, cancellation, service restart or UI acceptance
is claimed. Recording/AutoPlayWith, mappings/external players and the other #14
provisional gaps remain distinct; no permanent removal is proposed here.

## Normal main integration for independent review

After PR19's normal merge, live main was independently verified at
`6d1b9162289ccc20c3ba089302dc3a149150d0be` and normally merged into this branch as
`5fe91ea10e5a09c29f04a7be984b3ab9c6278434`, with **no conflicts**. Its parents are
original reviewed `d210c1cd199b8c28cb57ec901da98f07ba9b8205` and that pinned main;
the original commit remains unchanged in ancestry for Task13. No rebase or
scheduler-scope changes were needed. This follow-up changes only these notes.

All **nine** current pure-check scripts independently exit **0** on the integrated
runtime: AutoPlay, command data, passive skins (12 tests), metadata/search
(11 tests), fixtures, PVR, Python3, reminders and source safety. Narrow typing for
the three AutoPlay modules still exits **0**; the API wrong-type negative control
still exits **1** with four expected argument diagnostics. Python3.8 grammar checks
cover the AutoPlay runtime and all nine scripts. Existing warnings remain in raw
stderr; no six-stage/four-lane rerun or native compatibility claim is added.

Private `task11-integration-summary.json` and corresponding stdout/stderr retain
exact commands, subprocess exits, hashes and tested merge identity. Tree comparison
confirms **921 main entries outside the seven task11 paths have identical blobs
and modes**, including PVR, skins, metadata, safety and the full Program+service
manifest/functions. All task11 runtime/test blobs equal original `d210c1c`;
only this documentation differs after the merge. The final review identity is
recorded separately in `task11-integration-HANDOFF.md`; no runtime rerun is implied
by the documentation commit.

[Issue21](https://github.com/kcook98765/script.tvguide.fullscreen/issues/21) is the
separate Task13 channel/source selection, omitted new-only reconstruction and
title/start collision scope. This PR does not duplicate those fixes or redefine
intentional cross-channel regex reminders. PR20 remains draft pending independent
review; no permanent feature removal is introduced.
