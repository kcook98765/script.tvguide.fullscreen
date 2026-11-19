# Persistent image matches — Task12 source candidate

Refs #14 / #5 / #7 / #1. This focused restoration starts at reviewed PR18 normal
merge `8b03cad38c9730449773458efc1a7dcdcbe68284` (tree equals reviewed `d47440d`).
Original `origin/master` remains `0e46733e9e5f7711f2381562cfbb98fd3b54b429`, an
ancestor of this base. GPLv2 manifest, GPL-2.0-or-later source notices, attribution,
Program + service and resources are preserved. No permanent feature removal is
proposed. Independent review and later supervisor-coordinated main reconciliation
remain separate; this branch does not incorporate the metadata/AutoPlay tasks.

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

**Native #8–#11: BLOCKED / UNRUN on all four versions**, under the existing
[mixed Program+service blocker](https://github.com/kcook98765/kodi-lab/issues/112#issuecomment-7023719173).
No Lab stages, lifecycle/selection/source/workspace/grant changes, deployment,
enablement, launch/smoke, settings, input, UI/logs/screenshots or production access.
Stopped/archived profiles and earlier runtime receipts remain untouched. This
candidate is source-only restoration, not native filesystem/image/UI acceptance.

### Exact API basis (reusing Task04 scope)

Task04's [cache recommendation and preservation inventory](https://github.com/kcook98765/script.tvguide.fullscreen/issues/14)
already separates bounded JSON persistence from optional metadata providers.
No new provider/API contract is researched here. The existing translated profile
APIs are common Kodi19–22 operations; checked narrowly against oldest Matrix
stubs, not inferred from `xbmc.python` alone. Python3.8 references:
[JSON limits/Unicode/data conversion](https://docs.python.org/3.8/library/json.html),
[mkstemp exclusive same-directory creation](https://docs.python.org/3.8/library/tempfile.html#tempfile.mkstemp),
[os.replace / fdopen / fstat / fsync / lstat](https://docs.python.org/3.8/library/os.html#os.replace).
