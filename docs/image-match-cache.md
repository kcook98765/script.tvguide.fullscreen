# Persistent image matches — Task12 source candidate

> Historical task record: old activation-blocker / whole-campaign UNRUN statements
> below are superseded by the [current overview](modernization-status.md).
> Original failures and feature-specific unverified limits remain; later core
> native evidence is not blanket acceptance of this feature.

Refs #14 / #5 / #7 / #1. This focused restoration starts at reviewed PR18 normal
merge `8b03cad38c9730449773458efc1a7dcdcbe68284` (tree equals reviewed `d47440d`).
Original `origin/master` remains `0e46733e9e5f7711f2381562cfbb98fd3b54b429`, an
ancestor of this base. GPLv2 manifest, GPL-2.0-or-later source notices, attribution,
Program + service and resources are preserved. No permanent feature removal is
proposed. The original cache head `5951059527ce6c54dc0dce8de1ed62d9598b25f2`
received independent source review without a requested implementation correction.
Normal merge `ffea37ace89a60f3373fe8c8720871741dab8800` incorporates pinned reviewed
main `6d1b9162289ccc20c3ba089302dc3a149150d0be` (PR19 metadata, retaining reviewed
skin/PVR work). A subsequent normal merge
`3bc6a084f49fb83c6c5c726e5e0a1bc193af828e` incorporates reviewed scheduler main
`a9e916e2e02f4125234cc7fd54d8ab4e2b5b7994` (PR20/PR23). Final combined source
review remains pending. AutoPlay/schedule-ownership changes come only from that
reviewed main; no independent scheduler changes are duplicated here.

## Behavior restored and original data meaning

Original `gui.py:439-451,476-481` loaded/dumped `tvdb.pickle`; the unsafe loader
was removed in PR12. At this task's base, each `TVGuide` construction initializes
an empty dictionary. A learned image match therefore disappears on reconstruction.
The original and current four writers are ordinary OMDb matches, TVDb matches,
IMDb matches, and **Delete programme image**, which assigns an empty string.
TVDb/IMDb misses also store empty strings. Empty entries suppress another lookup;
deletion must not simply remove the key and immediately relearn it.

`image_cache.ImageCache` supplies the existing membership/index/assignment surface.
Successful bounded assignments save immediately, including lookup-thread results
and empty-string suppression; no close-time dump is needed. A reconstructed guide
loads those entries. The existing reset modes **2** (full maintenance) and **3**
(match cache only) now clear this JSON through the same helper. A failed clear
logs a fixed warning rather than claiming durable success. Other maintenance
deletions in mode 2 remain unchanged; mode 1 (database only) and mode 4 (logos)
do not clear image matches.

Consumers pass the string to image controls or fill an absent `imageSmall` in the
context menu. No URL-only validation is introduced: Unicode, punctuation, quotes,
backslashes, tabs/newlines, empty values, relative/native filenames and Kodi
`special://` / `image://` strings round-trip as data. There is no URL rewriting,
title normalization, title-derived file path or command/builtin interpretation.
Existing XMLTV small/large image precedence, descriptions, optional lookup
settings/threads, endpoints and matching logic are untouched. The helper does
not make network requests. It does **not** fix or verify the old HTTP
OMDb/TVDb/IMDb services. Task10/PR19 is optional provider-owned lookup UI, **not**
guide plot/art injection and not a prerequisite for this cache.

## Fixed storage and safety bounds

Only `<translated add-on profile>/image-matches-v1.json` is used, via the existing
`getAddonInfo('profile')` and `xbmcvfs.translatePath` APIs. The pure helper accepts
the profile directory, not an output filename, and creates no directories.
The JSON is exactly an envelope `{"version":1,"entries":{"title":"image"}}`.

- Read **at most 2 MiB + 1 byte**, with regular-file/size checks before opening
  and again on the descriptor. At most **1000 entries**, **4096 title characters**
  and **16384 image characters**, and at most **2 MiB encoded JSON** on updates.
  Limits count Unicode characters separately from encoded bytes/JSON escaping.
- Plain stdlib JSON, no executable deserialization/object hooks, class imports
  from data, custom encoders or dynamic dispatch. A fixed numeric decoder rejects
  integer tokens over nine characters before `int()`, including on Python 3.8
  builds predating the integer-string limit. Schema version must be integer 1,
  not bool/float/string. Values must be UTF-8-encodable strings; nested objects,
  null/numeric values and unpaired surrogates are rejected. Default JSON duplicate
  names use the last value, still subject to byte/schema/entry bounds.
- Missing, malformed, wrong-schema, oversized or unreadable input becomes an
  empty rebuildable cache. No partial untrusted mapping is adopted. The bad file
  is not modified merely by loading; a later normal assignment/explicit clear
  can replace it with valid JSON. Overflow/invalid assignments are not cached;
  existing valid entries remain. There is no eviction/background cleanup.
- Require an existing absolute local directory with no symlink components.
  Reject symlink/nonregular cache files; use no-follow/nonblocking flags where
  available and descriptor identity checks for reads. Temporary files are
  exclusively created by `mkstemp` **in that same profile directory**, written,
  flushed, fsynced, closed, then installed by `os.replace`. The destination is
  never opened for writing; neither a final symlink nor hardlink target is
  overwritten through an existing link. Ordinary failed writes remove only
  their own temporary file and leave the previous complete JSON in place.

**No pickle migration.** Neither `tvdb.pickle` nor `tvdb_banners.pickle` is opened,
decoded, converted, overwritten or deleted by these cache paths, including the
updated reset actions. Unrelated user files are untouched by the helper. The
cache rebuilds only from the existing normal writers; no migration subprocess or
new permission prompt is involved. This is a current difference, not a permanent
owner-approved loss of previously learned matches.

## Best-effort limits — not a database or concurrency framework

Each instance serializes mutation + save under a small `RLock`, so the existing
lookup threads cannot interleave/truncate one instance's writes. Independent
guide processes/instances can each publish a **complete** stale snapshot:
**last writer wins**, with possible lost updates or resurrection after another
instance clears/deletes. Clear with the guide closed for reliable next-launch
rebuilding; in-flight legacy lookup results can also relearn a deleted image.
No interprocess locks, merging, orchestration, cross-process invalidation or
provider-thread cancellation is claimed or added.

Ordinary save errors leave bounded valid entries available in memory, not
guaranteed on disk; the next mutation retries its current snapshot, not a queued
job. Clear failures may leave the older disk cache. No retry-at-close/crash
recovery or full power-loss durability is promised (no directory fsync). A hard
crash can leave a private temp file; no global cleanup scans are added. Remote
VFS/linked/unavailable profiles or unsupported local replacement semantics fall
back to memory. Synchronous bounded writes can add lookup latency. Checks are
not a sandbox against a hostile same-user process replacing directory components
between checks; Kodi, its profile directory and local filesystem are trusted.

## Focused evidence and explicitly unperformed stages

Private, ignored evidence stays **inside the Task12 worktree** at
`.cache/task12/` (not Git/runtime/package input). The baseline receipt extracts
the real base constructor and reproduces learned-entry loss on reconstruction;
the original source receipt records unsafe pickle load/dump without execution.
Only selected tracked source/history was read; no profile, excluded configuration
or protected task worktree/evidence was inspected.

`tests/check_image_cache.py`: **12 pure/AST tests**, with isolated disposable
directories, actual helper calls and extracted real constructor/four assignments,
delete/context consumer and reset helper/calls. Covers exact Unicode/punctuation,
empty and local/special image strings, update/delete/clear/reload; old pickle and
unrelated bytes unchanged/unopened; malformed/schema/depth/huge-number/file,
entry/string/encoded-size limits; missing/nonlocal/nonregular/symlink/hardlink
paths; read/create/partial-write/fsync/replace failures; destination bytes intact
until replace; concurrent lookup writes; XMLTV context-art precedence. These are
not Kodi imports, native profiles, executed builtins, live network or UI tests.

All eight focused scripts exit **0**: cache12, skin12, PVR12, reminder6, fixture4,
safety, command-data and Python3. The safety script retains its original unsafe
source controls; command-data rejection controls remain. Changed runtime files
parse as Python **3.8**; only stdlib APIs available by 3.8 are used (no newer
`Path.is_relative_to`, `missing_ok`, union/generic annotation runtime dependence).
The test harness itself runs on host Python 3.12, not an embedded 3.8 interpreter.

Selected interpreter: `/home/kyle/kodi-development/toolkit/.local/matrix/bin/python`.
Standalone CLI `stub-lanes` runs first: CPython3.12.3/Linux, Kodistubs19.0.3,
mypy2.4.0, checker0.0.36. Narrow Toolkit Matrix type-stage helper + relevant Kodi
API-signature fixture **passes (subprocess.returncode=0)**. Its deliberately bad
signature control **fails as expected (subprocess.returncode=1, three errors)**;
raw stdout/stderr, commands, annotation-overlay details and status are preserved.
The driver exiting0 only confirms both expectations, not that the negative
validator passed. No Kodi/stub module is imported by the runtime tests.

**No new full-add-on/six-stage or four-lane validation is claimed.** Reuse the
historical [six-stage receipts](native-fixtures.md#local-results-2026-11-19):
syntax/manifest/paths/package PASS; types **FAIL651** and official checker
**FAIL73 / 11 warnings** in the latest historical Nexus report. Those are not
measurements of Task12 bytes. All legacy warnings/negative controls remain;
no broad typing/metadata cleanup, packaging export, index refresh or dependency
download was attempted. The historical validators actually exited1; a subsequent
summary reader's exit0/completed status is not validator success. Matrix static
19.5 is not native19.4; Piers remains bounded RC2, not stable/full qualification.

### Reviewed-main integration evidence

The first integration base was exactly `6d1b9162289ccc20c3ba089302dc3a149150d0be`;
the merge preserves both parents without rebase or rewriting the reviewed cache
commit. The helper, reset integration, cache tests and complete manifest remain
**byte-identical** to `5951059`. The merged `gui.py` is exactly pinned main plus
the three reviewed cache edits (import, construction, deletion display); all
metadata callbacks and existing artwork/details behavior coexist unchanged.
All other tracked paths equal pinned main, apart from the five Task12 paths.

All nine combined focused scripts **exit0**: cache12, metadata11, skin12, PVR12,
reminder6, fixture4, safety, command-data and Python3. Changed-runtime Python3.8
AST and the preservation assertions also **exit0**; legacy warnings are retained.
Private `integration-*` receipts in `.cache/task12/` preserve actual subprocess
returncodes, stdout/stderr and byte-preservation assertions. The unchanged narrow
Matrix type/API receipts and their expected exit1 negative control remain valid
for their exact unchanged inputs; no broad six-stage rerun is claimed.

### Final scheduler-main integration evidence

Remote main was verified at exactly `a9e916e2e02f4125234cc7fd54d8ab4e2b5b7994`
before merging. Normal merge `3bc6a084f49fb83c6c5c726e5e0a1bc193af828e` preserves
both the prior Task12 head `873f00187e246dfb981191fbbbf7d22401d881cb` and pinned
main as parents. No conflict resolution, import rearrangement or runtime edit was
needed. **Helper, reset integration, cache tests and manifest remain byte-identical
to independently reviewed `5951059`; the complete GUI is byte-identical to
`873f001` and equals current main plus exactly the original three cache edits.**

The complete main-relative delta remains only the five Task12 paths:
`image_cache.py`, `gui.py`, `ResetDatabase.py`, `tests/check_image_cache.py`, and
this document. All other main files are unchanged. Additional explicit byte/hash
checks preserve `play.py`/`stop.py` decoded callbacks, `autoplay_data.py`, scoped
`autoplay.py`/`notification.py`/`command_safety.py`, `source.py` selection/clear
joins, reminder helpers, both entrypoints, metadata/PVR/skin helpers and manifest.
This combines reviewed implementations; it does not broaden their documented
ownership, callback, recurring-selection or in-flight cancellation guarantees.

**Eleven focused scripts exit0**: cache12, schedule-ownership7, AutoPlay6,
reminders6, metadata11, skins12, PVR12, fixtures4, safety, command-data and Python3.
Python3.8 AST, main-relative path/byte preservation and diff checks also exit0.
`.cache/task12/scheduler-integration-*` stores commands, raw stdout/stderr, actual
subprocess returncodes and SHA-256 assertions; previous evidence is retained.
Test commands use isolated Python with PATH-only child environments and ordinary
disposable temp directories: HOME/home/CODEX_HOME are not repurposed. No broad
six-stage rerun or new native qualification is claimed; unchanged narrow cache
type/API receipts, negative controls and historical broad failures remain.

### Native routing status — explicitly DEFERRED

**Native #8–#11 remain UNRUN on Matrix19.4/Nexus20.5/Omega21.3/Piers22RC2.**
The focused routing issue is now [Lab394](https://github.com/kcook98765/kodi-lab/issues/394),
**DEFERRED per owner**; the closed broad Lab112 discussion is historical context,
not the current focused issue or proof of whole-add-on failure. Task06's existing
observations establish that full registered-source mixed-manifest intake and
workspace validation **pass** for their frozen source/generation, not these new
bytes or native operation. The source-predicted gap is a **qualified, consented
cold FIRST ACTIVATION** contract. It is not a blanket byte-copy/deployment failure
or evidence that Kodi cannot run the combined manifest. Fixed-video smoke
ineligibility is only that narrow capability's limit. Declared script launch and
actual service startup **and functional work** require separate evidence; an
enabled Boolean, parse/validation result or script UI alone is not acceptance.

Both `xbmc.python.script` (`addon.py`) and `xbmc.service` (`service.py`), their
original responsibilities and complete resources remain mandatory across all
four targets. No split/strip workaround or permanent feature removal is approved.
There is **no continued investigation, activation attempt or workaround** in this
task. No Lab calls, lifecycle/selection/source/workspace/grant changes, deployment,
enablement, launch/smoke, settings, input, UI/logs/screenshots, infrastructure,
Toolkit, configuration, production or release changes. Stopped/archived profiles
and earlier runtime receipts remain untouched. Source-only restoration proceeds
independently; native filesystem/image/UI/service acceptance remains deferred.

### Exact API basis (reusing Task04 scope)

Task04's [cache recommendation and preservation inventory](https://github.com/kcook98765/script.tvguide.fullscreen/issues/14)
already separates bounded JSON persistence from optional metadata providers.
No new provider/API contract is researched here. The existing translated profile
APIs are common Kodi19–22 operations; checked narrowly against oldest Matrix
stubs, not inferred from `xbmc.python` alone. Python3.8 references:
[JSON limits/Unicode/data conversion](https://docs.python.org/3.8/library/json.html),
[mkstemp exclusive same-directory creation](https://docs.python.org/3.8/library/tempfile.html#tempfile.mkstemp),
[os.replace / fdopen / fstat / fsync / lstat](https://docs.python.org/3.8/library/os.html#os.replace).
