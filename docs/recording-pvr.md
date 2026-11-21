# First optional recording slice: Kodi PVR (source-only partial replacement)

> Historical task record: old activation-blocker / whole-campaign UNRUN statements
> below are superseded by the [current overview](modernization-status.md).
> Original failures and feature-specific unverified limits remain; later core
> native evidence is not blanket acceptance of this feature.

Refs #14, #7, #6, #1. Targets: Matrix **19.4**, Nexus **20.5**, Omega **21.3**,
Piers **22 RC2**. This is a focused draft implementation, not native acceptance,
arbitrary XMLTV/M3U recording parity, or permanent disposition of AutoPlayWith.

## What users can do

The existing context-menu recording button (all three bundled skins), scheduler
menu and Record key open **Record (Kodi PVR)** choices. Lists gains **PVR timers /
cancel**. Existing user-assigned PLAY_AUTOPLAYWITH / AUTOPLAYWITHS /
STOP_AUTOPLAYWITH aliases open the new interactive menu/list/active-timer list;
they never execute old commands. No default ordinary playback/reminder setting
changes. Program + service, resources, manifest/dependencies and GPL are retained.

1. **Record now:** explicitly choose a real TV/radio PVR channel, with channel ID,
   backend name/client ID displayed, then confirm. The guide channel/title/time is
   **reference only**, not an identity mapping or a recording duration.
2. **Schedule once:** explicitly choose that PVR channel and then a future PVR
   EPG broadcast (title, start/end **UTC**, broadcast ID displayed). Confirm that
   it is the intended guide event. No title-based automatic mapping, cached
   mappings, guide offsets applied to PVR times, or recurring-rule creation.
   Broadcasts already having a timer are excluded; manage them in the timer list.
3. **Inspect/cancel/stop:** list real Kodi PVR timers, including other sources'
   timers. Select one timer, review its real channel/backend/title/UTC times/ID,
   and explicitly confirm deletion or stopping the selected active recording.
   Only writable, non-reminder, non-rule timers in `scheduled` or `recording`
   state are cancellable here. Rules/other states are view-only; use Kodi PVR.

**Prerequisite:** the user must already have configured a recording backend and
enabled Kodi PVR client, e.g. Tvheadend/NextPVR, with recording **and** timer
capabilities. Future scheduling also needs that client's EPG. This add-on does
not install/configure them. IPTV Simple playlist/catchup/VOD support is not proof
of a capture backend. Missing/unsupported PVR gives an explanatory dialog, not
an inert callback or silently saved local recording row.

## Exact boundary and safety

[`pvr_recording.py`](../pvr_recording.py) is a small stdlib-only interactive
controller; `gui.py` supplies `xbmc.executeJSONRPC` and `xbmcgui.Dialog`. It reads
`PVR.GetProperties(available)` and `PVR.GetClients` capabilities, then real PVR
channel/broadcast/timer lists and details. XMLTV IDs, programme titles, guide
times and URLs **never become PVR IDs**. Only positive non-bool signed-int IDs
obtained from these responses can reach the three fixed mutation payloads:

```json
{"method":"PVR.Record","params":{"channel":41,"record":true}}
{"method":"PVR.AddTimer","params":{"broadcastid":901,"timerrule":false,"reminder":false}}
{"method":"PVR.DeleteTimer","params":{"timerid":77}}
```

IDs above are inert test examples. Requests use complete JSON-RPC 2.0 envelopes,
incrementing IDs and `json.dumps`; responses require the same integer ID, version,
no error, and explicit `"OK"` mutation acknowledgement. Metadata stays decoded
JSON/Dialog data, never builtin/shell grammar. No raw command dispatcher, profile
code, executable/download, subprocess, process-name stop or arbitrary RPC input.

After selection and confirmation, backend capabilities and displayed item
identities/details are re-read before mutation. Stale items, past/invalid times,
existing channel recordings, unsupported/invalid IDs, cancellation and read
errors produce **no mutation**. An error/lost reply **after dispatch** may mean
the backend changed: no success claim, no automatic retry; inspect Kodi PVR
before trying again. `"OK"` means Kodi accepted the request, **not that a saved
recording exists or will finish**. Conflict/storage/tuner/backend failures remain
possible. Snapshots and writes are not atomic; Kodi offers no compare-and-act
transaction here, so concurrent backend changes remain a native acceptance risk.

`PVR.Record(record=true)` is deliberately **not** toggle/current-channel mode.
There is no broad `PVR.Record(record=false)` stop: stopping uses one rechecked
real timer ID and explicit user intent. Timers need not have been created by
this guide, and the confirmation says so. Deleting a rule occurrence does not
delete its parent rule; backend recreation policies require Kodi/backend review.

## Tagged official contract evidence

Reuses issue14/TASK04 primary research; only exact field/time/ID and mutation
implementation details were rechecked for this slice on 2026-11-19:

| Kodi tag | Official commit | `PVROperations.cpp` SHA-256 |
| --- | --- | --- |
| [19.4-Matrix][matrix] | `e12e66e019af29ba9d5f5a2614315b15a138b81a` | `623c467ba540b5f5547554fe7ba5d0234a7e3006df8989817587e0983cba0b5b` |
| [20.5-Nexus][nexus] | `4b95737efaddf7c869736e539318f18433413ff1` | `a6d2e5d9e55030cf9f8e8a5892d83ae1c77029b3148020f652305f7aad609607` |
| [21.3-Omega][omega] | `a3a448d26b8d560a65655dab2cd122994dc4e146` | `ba6e7bc82274dd629049af08da061a63fc2fe47aa5587e08386ff3762f333baa` |
| [22.0rc2-Piers][piers] | `d686683a55d50e576dd282f53fb2bf9914931b38` | `4995362c9be1c2dab72680a972ccab9aefe81bad8ceba50eb16c5196449ec97a` |

At **each tag** the relevant paths under `xbmc/` are:

- `interfaces/json-rpc/schema/methods.json` and `types.json`: all eleven used PVR
  methods/fields, `Library.Id` minimum 1, `alltv`/`allradio`, `clientid`,
  `supportsrecordings`, `supportstimers`, `supportsepg`, `isrecording`,
  `hastimer`, timer `state`/`isreadonly`/`istimerrule`/`isreminder`.
- `interfaces/json-rpc/PVROperations.cpp`: resolves native channel DB IDs,
  globally unique EPG DB IDs, exact timer IDs; returns errors when unavailable.
  `Record(true, channelid)` differs from `AddTimer(broadcastid, false, false)`.
  DeleteTimer calls `DeleteTimer(timer, timer->IsRecording(), false)`; that final
  false means **not** delete its rule.
- `pvr/channels/PVRChannel.cpp::CanRecord`: Matrix checks recordings;
  Nexus–Piers check recordings **and** timers. This slice requires both throughout,
  avoiding recordings-only playlist clients.
- `pvr/epg/EpgInfoTag.cpp/.h` and `pvr/timers/PVRTimerInfoTag.cpp/.h`:
  serializers use UTC time members' `GetAsDBDateTime()` (`YYYY-MM-DD HH:MM:SS`),
  not guide-local time. Broadcast IDs are database IDs, not backend EPG UIDs.
  `CreateFromEpg` with rule=false excludes `PVR_TIMER_TYPE_IS_REPEATING`; if no
  suitable one-shot EPG timer type exists, AddTimer fails instead of falling back
  to a recurring rule. This API accepts no arbitrary URL/start/end/padding.
- `pvr/timers/PVRTimers.cpp::DeleteTimer`: selects the passed timer, only resolving
  a parent rule if `bDeleteRule` is true. Backend-specific cancellation and timer
  types still require runtime acceptance.

These are **source/API contracts, not installed backend availability or recording
tests**. Source existence and a catalogue entry cannot establish native success.

## Focused evidence and reproducibility

Base is normal PR16 merge `9d0c225cf060594159028ecf2da48f724e6747b3`, tree
`ba9d38244d296217fb4e97125543ae2d6ede671d`, exactly the reviewed
`2023a88ba364cc628f65a708a7bec0c02f8f8b49` tree. Both PR16 commits and original
`origin/master` `0e46733e9e5f7711f2381562cfbb98fd3b54b429` remain.

Selected interpreter **before** static checks:
`/home/kyle/kodi-development/toolkit/.local/matrix/bin/python`.
`-m kodi_agent_toolkit.cli stub-lanes` actually exited **0**, reporting CPython
3.12.3/Linux, Kodistubs19.0.3, mypy2.4.0, checker0.0.36, Matrix static readiness.
This is the Matrix19.5 static lane, **not native Matrix19.4** or other lanes.
Matrix's validator-only annotation corrections and Piers' bounded RC2 limits
remain; CPython3.12 tooling does not establish Kodi's embedded Python version.

`env -i PATH=/usr/bin:/bin <interpreter> -I -B tests/<name>.py`:

| Focused check | Actual child exit / result |
| --- | --- |
| `check_pvr_recording` | **0**, 12 pure/AST-extracted checks; exact read/write payloads, manual choice, data preservation, cancellations, absent/incapable backend, errors/ambiguous replies, invalid IDs, stale details, elapsed event, rules/read-only controls, timer-scoped stop, GUI/keymap wiring |
| `check_safety` | **0**, original unsafe-source negative controls and runtime source scan retained; provisional inert-recording assertions replaced with PVR-only boundary checks; unrelated external metadata still disabled |
| `check_command_data` | **0**, original raw-command/delimiter controls retained |
| `check_reminders` | **0**, all six checks, original text/phase/cancel/duplicate controls retained |
| `check_python3` | **0**, existing pure shared-port regression |
| `check_native_fixtures` | **0**, four existing real-loader/fixture checks, **not Kodi playback** |
| Changed Python files, Python3.8 AST grammar | **PASS**, parse only |
| Narrow mypy (`--check-untyped-defs --follow-untyped-imports`) | **0**, pure PVR module + static JSON-RPC/Dialog signature probe (2 files), no broad legacy typing claim |
| Deliberately invalid static API signature probe | **1**, **six expected diagnostics**, not a passing validator |
| `git diff --check` | **0** |

Four in-memory **negative-control mutations** are detected: record=false,
timerrule=true, wrong timer ID, bypassed confirmation. They are not deployed.
Test children receive PATH only, no publishing credentials; no host Kodi/stub or
legacy-module imports. Existing GUI invalid-escape SyntaxWarnings remain visible.
First PVR harness run actually exited **1**: its capture returned broadcast900
instead of the explicitly requested901, correctly refused by the implementation.
Only the capture lookup was corrected; the rejection was not weakened.

Raw stdout/stderr, initial failure transcription (full raw also in tool receipt),
actual child exit summaries, file hashes and positive/negative API probes are
private `.git/modernization-evidence/task08-*`, never add-on/package payload.
The final narrow rerun follows the timer channel-name recheck and keymap capture;
unchanged reminder/fixture/command checks reuse the preceding successful run.

**No new six-stage full validation:** CLI help confirms no stage selector. Retain
historical TASK03 four-lane syntax/manifest/paths/package **PASS**, types and
official checker **FAIL**, all warnings and negative controls; these receipts
are not validation of new bytes. Latest PR16 Nexus receipts retain **651 typing
diagnostics, 73 checker problems, 11 warnings**. Both original validators had
actual metadata **exit1** and structured JSON **exit1 / passed=false**. Only the
summary reader exited0; completed tool status is not validator success.
No new full-lane pass is claimed, no blanket suppressions or environment changes.

## Explicit remaining differences / next practical path

- Arbitrary M3U/plugin capture and external-player AutoPlayWith remain temporarily
  disabled; no arbitrary URLs or command templates are handed to the PVR backend.
- Old once/always/new/daily semantics, user padding, guide scheduling markers,
  legacy schedule lists and automatic legacy-row migration are **not restored**.
  PVR once is a new optional route, not equivalent to those saved rules. Existing
  legacy DB rows are neither executed nor modified. PVR timers persist through
  the backend/Kodi, not the old service scheduler.
- Record-now end/duration, default padding, conflicts, storage/tuners and rule
  child recreation belong to Kodi/backend policy; there is no hardcoded four-hour
  limit or old broad taskkill/pkill stop. Inspect the real timer in Kodi.
- Next: separately authorized native acceptance with an existing lawful recording
  backend, then one focused preservation slice for proven one-shot mappings or
  backend-specific rules/padding UI. If the backend prerequisite is unacceptable,
  owner should assess a separate trusted administrator-selected desktop FFmpeg
  fixed-argv/owned-child design (no downloads/freeform commands), with platform,
  stream/header/plugin/DRM and output-ownership tests. None is silently rejected
  forever or included in this slice.

**All four native stages (#8–#11) remain BLOCKED/UNRUN**: no qualified complete
mixed Program+service enablement path, as already recorded in
[Lab112](https://github.com/kcook98765/kodi-lab/issues/112#issuecomment-7023719173).
Do not strip/split service/resources or retry native preparation to fit tools.
No lifecycle/selection/Reset/deploy/enable/launch/smoke/settings/UI/log/screenshot
operation was performed. Backend availability, real recording, cancellation and
native UI remain untested. This implementation is independent of that blocker.
No release/distribution publication; tracking issues remain open.

[matrix]: https://github.com/xbmc/xbmc/tree/e12e66e019af29ba9d5f5a2614315b15a138b81a/xbmc
[nexus]: https://github.com/xbmc/xbmc/tree/4b95737efaddf7c869736e539318f18433413ff1/xbmc
[omega]: https://github.com/xbmc/xbmc/tree/a3a448d26b8d560a65655dab2cd122994dc4e146/xbmc
[piers]: https://github.com/xbmc/xbmc/tree/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc
