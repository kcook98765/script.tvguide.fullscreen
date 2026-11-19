# Opt-in native acceptance inputs — task07

Refs #4 / #6; parent #1, related #3 / #5 / #14 and native #8–#11.
**Source-only fixture preparation, not native or full static qualification.**
OpenCode owns implementation; Codex independently reviews. One shared payload
targets Matrix **19.4**, Nexus **20.5**, Omega **21.3**, Piers **22 RC2**.
No provider, loader, GUI, database, manifest, setting default, safety helper,
reminder callback or service behavior is changed. No user-facing feature is
removed; #14's provisional feature losses remain provisional.

## Data and provenance

Only these three files are runtime data, under
`resources/fixtures/native/` (not docs/tests or private evidence):

| File | Purpose | SHA-256 |
| --- | --- | --- |
| `guide.xml` | 3 channels, 8 adjacent 15-minute slots each, UTF-8 XMLTV | `a66ee418bbf80e09e77c8435cc4b627ef7e28750d95b3ca8030a6b921d15a9f0` |
| `mapping.m3u` | matching `tvg-id`s, all mapped to the local clip | `762a03b50ebba238dc9fd89a91cd8690cc94d6985c74b3e9887e2a1bc9062f56` |
| `clip.mp4` | finite 240-second synthetic VIDEO, 439183 bytes | `52807a551971e085aac02a19a4c2ab531a972ea13abfd73f8769ad9e11037917` |

Guide names/text are original fictional examples, not a scraped schedule. Series
has XMLTV zero-based `xmltv_ns` episodes `0.0.` through `0.7.` and `<new/>`;
movies have category `Movie` and date `1999`; culture has Unicode. Each channel's
titles include `Doctor's diary`, `He said "Hello"`, `News, Weather & Sport`,
`Film (1999)` and `Café — 日本語 📺`. These are data, not executable commands.
With the existing default `xmltv.date=true`, movie titles gain ` (1999)`;
the literal `Film (1999)` consequently displays `Film (1999) (1999)` there.
No remote icons/streams, embedded XMLTV `<stream>` bypass, LAN URLs or credentials.

The clip is FFmpeg's algorithmic `testsrc2`: moving shapes, no third-party media,
fonts, branding, speech or music. Original fixture data/generator/tests are
provided under the repository's GPL-2.0-or-later terms. FFmpeg/x264 are tools,
not bundled executable dependencies. The installed host tools were used without
downloads or installation: `/usr/bin/ffmpeg` **6.1.1-3ubuntu5**, built with
gcc 13 (Ubuntu 13.2.0-23ubuntu3); libavcodec 60.31.102, libavformat 60.16.100;
libx264 **core 164 r3108 31e19f9**. Exact synthesis argv, from repository root:

```sh
/usr/bin/ffmpeg -nostdin -hide_banner -loglevel info -n -f lavfi -i testsrc2=size=160x90:rate=2 -t 240 -an -c:v libx264 -profile:v baseline -level:v 1.0 -pix_fmt yuv420p -preset veryslow -crf 35 -threads 1 -g 20 -map_metadata -1 -fflags +bitexact -flags:v +bitexact -movflags +faststart resources/fixtures/native/clip.mp4
/usr/bin/ffprobe -v error -show_format -show_streams -of json resources/fixtures/native/clip.mp4
/usr/bin/ffmpeg -nostdin -v error -xerror -i resources/fixtures/native/clip.mp4 -map 0:v:0 -f null -
```

`-n` refuses overwrite. Probe: one H.264 **Constrained Baseline level 1.0**
video track, yuv420p 8-bit, 160×90, 2fps, 480 frames, duration **240.000000s**,
no B-frames, no audio/subtitle/attached-picture tracks. Low frame rate is
intentional; visible motion and advancing playback time distinguish it from
artwork. It ends once; no loop, background generator or orchestration. Baseline
H.264/MP4 is selected for common decoding on all four Kodi releases, but host
decoding **does not prove any native Kodi/platform playback**. It is silent and
does not test audio (including notification sound). Encoder builds/CPUs can
produce different bytes: the checked-in hash is authoritative, not a promise
that every FFmpeg build is bit-identical.

## Clock: align before EACH version's future native session

The immutable checked-in UTC reference is **2026-11-19T12:00:00Z**. Slot 0
starts **11:45Z**, slot 1 at **12:00Z**, and slot 7 ends **13:45Z**. At the
reference+10 minutes, slot 1 is now, slot 2 is next in five minutes, and seven
slots including now remain. The fixture is deliberately dated, **not current
unless aligned**; never change the system clock to fit it.

Preferred recipe: preserve the exact reviewed XML bytes and use the existing
`xmltv.offset` (signed integer minutes). Choose an explicit actual UTC minute
`T` just before each version's separately authorized native run:

```text
xmltv.offset = whole_minutes(T - 2026-11-19T12:00:00Z) - 10
```

Developer-only calculator (prints one integer; no writes/clock access):

```sh
/home/kyle/kodi-development/toolkit/.venv/bin/python -I -B tools/native_fixtures.py --align 2026-11-20T09:40:00Z
```

Output **1290**. At 09:40Z, now is `He said "Hello"`, next is
`News, Weather & Sport` at 09:45Z, the window is 09:15–11:15Z.
Use the **new actual UTC minute**, not this example, for each sequential version.
Record `T`, the offset, actual local timezone, source commit and all three
hashes in that session's evidence. Recalculate if setup consumes the short
reminder window. Beyond the 95 remaining minutes, realign/reload rather than
silently testing stale guide data. The loader converts XMLTV `+0000` to Kodi
local wall time then adds the offset; **do not add the timezone offset again**.
DST behavior is inherited (the loader uses the current local DST state).

Alternative developer regeneration (not required for native alignment):

```sh
/home/kyle/kodi-development/toolkit/.venv/bin/python -I -B tools/native_fixtures.py --check
/home/kyle/kodi-development/toolkit/.venv/bin/python -I -B tools/native_fixtures.py --reference 2026-11-20T09:30:00Z
```

The first compares exact checked-in text bytes; the second rewrites **only**
`guide.xml`/`mapping.m3u` at fixed source paths, with no implicit `now`. In the
example, use offset 0 for 09:40Z. Regeneration changes the reviewed source digest
and requires new hashes/review/intake/validation; it is **not** permission to
refresh the registered source/workspace. To restore canonical bytes run the
generator with no arguments (fixed reference, not today's date). It never
regenerates media or writes Kodi settings/profiles. Python ≥3.9 is needed for
this developer tool's `ElementTree.indent`, not for runtime data loading.

## Future explicit opt-in using ordinary settings (NOT applied by task07)

Only after source review and separately authorized managed-native preparation,
an authorized tester/administrator can select these existing settings on a
disposable development profile. This table is a recipe, **not a settings file**
or a request to mutate a target now:

| Existing setting | Value |
| --- | --- |
| `source.source` | `xmltv` |
| `xmltv.type` | `0` (File) |
| `xmltv.file` | `special://home/addons/script.tvguide.fullscreen/resources/fixtures/native/guide.xml` |
| `xmltv.offset` | calculated signed minute offset above |
| `mapping.m3u.enabled` | `true` (explicit import opt-in) |
| `mapping.m3u.type` | `0` (File) |
| `mapping.m3u.file` | `special://home/addons/script.tvguide.fullscreen/resources/fixtures/native/mapping.m3u` |
| `mapping.m3u.key` | empty; no encryption |
| `mapping.m3u.encode` | `false` |

These paths assume the ordinary development installation under
`special://home/addons/script.tvguide.fullscreen`, as the add-on itself already
assumes in callbacks. Confirm that supported deployed layout before testing;
do not invent a mount if it differs. All playlist entries point to
`special://home/addons/script.tvguide.fullscreen/resources/fixtures/native/clip.mp4`.
The three channels intentionally share one local video; no live-edge/seek/catchup
or channel-specific content claim is made.

Use an authorized disposable profile with other XMLTV sources, optional mapping
imports/subscriptions, network metadata/artwork/logo lookup and background
updates inactive; don't overwrite owner/LAN configuration. Those controls are
ordinary settings, not an added fixture mode. Defaults are unchanged. This
fixture supplies no provider network traffic, but the **add-on as a whole is
not made offline** (e.g. existing startup background downloads in `addon.py`,
optional metadata and logo integrations). A later campaign must account for
those separately, not assume local input disables them.

Apply settings through the supported administrator/native path only. Close and
reload/update guide data through the ordinary UI after offset/source changes;
the source cache may otherwise retain previous programme dates. Confirm the
displayed shifted now/next times before scheduling a reminder. Do not directly
edit settings.xml/SQLite, assume a live cache changed, or treat settings-write
receipt/launch acceptance as functional success. Future checks should observe
guide rows/categories/episode/movie data, M3U mapping, actual video playback
and advancing time, pause/stop/end, and punctuation-bearing reminder display
and sound separately on each approved release. No such observations occurred here.

## Loader/check scope and handoff boundaries

`XMLTVSource.__init__` / `getDataFromExternal2` / `FileWrapper` in `source.py`
use the existing local FileFetcher/VFS byte path, ElementTree iterparse and
`parseXMLTV`/`parseXMLTVDate`. `TVGuide.loadChannelMappings` in `gui.py` reads
the existing M3U as UTF-8 bytes and maps `tvg-id` to channel IDs. These fixtures
exercise those formats; there is no alternate parser or `<stream>` shortcut.
No demonstrated parser defect required a runtime fix.

`tests/check_native_fixtures.py` runs four bounded checks: exact regeneration,
UTC/offset and non-UTC display arithmetic, metadata/adjacent rows, real M3U
mapping and pinned finite-video identity. It AST-extracts the **actual** XMLTV
methods, M3U mapping method and plain Channel/Program classes into an in-memory
harness with unexpected I/O refused. No add-on imports/initialization, Kodi/stub
execution, network, real profile writes or SQLite; this is **not** end-to-end
VFS/cache/UI/player acceptance. Wrong-ID and truncated-media controls remain
negative; no broader safety check is weakened. Original syntax warnings remain.

Task06 remains frozen: source `7562fd88-35b1-458a-bc6e-4990e57c0ffe`, workspace
`0e4c75c0-b56f-43ed-8364-99961aea9933`, generation **0**, digest
`sha256:06743f2f0b9342ecf5e6b4b52d9dbff62bddf08b6bc97bb8a0480b949e8dd004`.
This task **does not** refresh/scan/capture/import/validate that workspace or its
registered input. A later supported intake must explicitly review the new
`resources/fixtures/native` directory **and binary .mp4 resource policy**, and
exclude `tools/**` in addition to `docs/**`, `tests/**`, `.gitignore`, local
`opencode.json`, Git/caches/evidence. Being in Git/runtime resources does not
prove a current Lab allowlist will accept a new directory or binary.
No private workspace filesystem writes or grant/source changes are authorized.
Program+service is retained; task06 structural validation is not native
acceptance, and its fixed-video smoke rejection is not resolved by these data.
Future inventory/enablement, generation-bound intake/deploy and supported Program
execution/inspection require their own authority and evidence.

## Local results (2026-11-19)

- `env -i PATH=/usr/bin:/bin /home/kyle/kodi-development/toolkit/.venv/bin/python -I -B tests/check_native_fixtures.py`:
  **4 tests PASS**. Initial harness failure (class constant assigned on instance
  instead of extracted class) is retained privately; the harness was corrected,
  not the add-on. Existing invalid-escape `SyntaxWarning`s remain in raw stderr.
- Same minimal environment/interpreter, `tools/native_fixtures.py --check`:
  both text payloads byte-identical; `--align 2026-11-20T09:40:00Z`: **1290**.
- Same minimal environment/interpreter, `tests/check_safety.py`: **PASS**,
  including original unsafe-source negative controls. No add-on/Kodi/stub import.
  Command-data, reminder and Python3 regression scripts and all their runtime
  inputs are **unchanged**; reuse their task05 results, do not claim a rerun.
- FFprobe identity above and full `ffmpeg -xerror` decode: **PASS**, exit 0,
  no decode errors; this is host decoding only.
- `git diff --check` / `git diff --cached --check`: **PASS**.

The trusted standalone CLI has no stage selector. A Nexus six-stage run was
made on a runtime-only staged-blob export (no source configuration read), not
on the canonical root with its excluded local files:

```sh
/home/kyle/kodi-development/toolkit/.venv/bin/python -m kodi_agent_toolkit.cli stub-lanes
/home/kyle/kodi-development/toolkit/.venv/bin/python -m kodi_agent_toolkit.cli validate /home/kyle/kodi-development/addons/script.tvguide.fullscreen/.git/modernization-evidence/task07-fixtures/final-static-input/script.tvguide.fullscreen --branch nexus --cache /home/kyle/kodi-development/toolkit/.local/index-cache
```

Observed CPython **3.12.3/Linux**, Kodistubs **20.0.1**, mypy **2.4.0**,
checker **0.0.36**, Nexus lane ready. It does not qualify the other stub lanes.
Export: **904 files / 4858794 bytes**, SHA256SUMS digest
`sha256:48b9669b034102d1b8cc7051621f93452c8648a3c5847c43f124bdd38a7bf640`.
Tracked Git blobs only; exclude docs/tests/tools/.gitignore; no `.git`, evidence,
cache or excluded `opencode.json`. The export is local static input, **not a
registered-source refresh or installable release**; no ZIP is published.

| Stage | Current Nexus export result |
| --- | --- |
| syntax | PASS |
| manifest | PASS |
| paths | PASS |
| package | PASS |
| types | FAIL: 651 diagnostics, 20 files / 43 checked source files |
| official checker | FAIL: 73 problems, 11 warnings |

An initial same-lane report is retained too: after review, XMLTV movie `date`
was placed before `category` in conventional XMLTV element order and the exact
final payload was re-exported/rechecked. No loader logic changed; all six final
stage statuses/counts are the same. A same-host second synthesis to private
evidence produced the identical clip SHA-256; its full encoder output is saved.

The JSON itself says `passed=false`, `exit_code=1`, despite the CLI process
exiting 0; process completion is not validation success. All six raw stages
and full diagnostics are retained. No 73-metadata/662-typing cleanup was attempted.
The 651 count is current Nexus evidence after the merged reminder changes,
not a claimed task07 type repair; task07 changes no runtime Python bytes.
Checker problems remain 69 legacy language directories, metadata schema,
undeclared icon/fanart assets and icon transparency. All **11 warnings** remain:
three blocked/unverified metadata URLs; Nexus Python minimum advice 3.0.1;
beautifulsoup4 missing version; complex Program/service entrypoints; new fixture
**non-whitelisted `mapping.m3u` extension**; and three existing pytz `.tab`
extensions. The M3U warning is intentionally not hidden by renaming the file or
changing checker policy. Fixture package-stage acceptance is **not official
repository compliance**. Offline index cache fetched **2026-10-20**, manifest
SHA-256 `6ee4ed59f94aafd48469336f06e8ffb7286786e3d1e7607dcbb6e75f956c5f9f`;
all per-index hashes and network-blocked warnings remain in the JSON.

No full suite or four-lane rerun. Historical task03 six-stage reports remain
unchanged: all four syntax/manifest/path/package PASS, types 662 in
Matrix/Nexus/Omega and 636 in Piers, checker 73 findings each. Those receipts
apply to their old bytes, **not these new fixture bytes or current head**.
Matrix static lane is 19.5 major evidence, not native 19.4; Piers retains bounded
RC2/prerelease coverage and stale checker advice. The current task is **PASS for
bounded fixture checks, PARTIAL for overall static qualification, NATIVE PENDING**.

Exact frozen source head is recorded in the draft PR; private raw evidence,
export inventory, stdout/stderr and initial failure are under
`.git/modernization-evidence/task07-fixtures/`.
No Lab calls, selection/lifecycle/Reset/deploy/enable/launch/navigation, target
settings changes, UI/logs/screenshots, production access, releases/tags or
distribution publication are part of task07. Stop for independent source review.
