# Source safety assessment — tasks 01 and 02

## Task 02 correction (2026-11-19; awaiting independent review)

Continues `fe5e72f9b0bb6ffe37ec5b7ac72eaaa99251bb7f` on the same branch and
draft [PR #12](https://github.com/kcook98765/script.tvguide.fullscreen/pull/12),
responding to the supervisor's **PARTIAL / changes requested** comment, refs #7 / #1.
This is the command/data safety correction, **not** issue #2's Python 3 port.
All sections headed Task 1 below are historical evidence at the earlier revision.

* `notification.py` / `autoplay.py`: alarm names are now fixed namespaces plus
  SHA-256 of title/time, including cancellation. The small pure `command_safety.py`
  helper rejects empty values, commas, parentheses, either quote, backslashes and
  ASCII controls in reminder title/localized descriptions/icon and autoplay channel
  ID **before** building either nested command. Refusal logs contain no feed data.
  This intentionally skips delimiter-bearing reminders/IDs (including ordinary
  apostrophes/commas, and Windows icon paths containing backslashes); it does not
  pretend arbitrary nested builtin quoting is safe. No new scheduler or framework.
* `play.py` uses `xbmc.Player().play(item=url)`. Both ordinary and fallback GUI
  plugin playback always use the existing Player data API. The obsolete alternative
  RunPlugin mode/setting is removed; stale stored settings cannot restore it.
* GUI play-beginning and meta catchup encode **each** title/language/season/episode
  URL component as UTF-8 with `urllib.quote(..., safe='')`; configured plugin suffix
  must match the entire `[a-z0-9_.-]+` string. No pre-encoding of spaces or lossy
  ASCII conversion. Play-beginning and direct catchup use Player. Scheduled meta
  catchup retains only a fixed RunPlugin template with encoded data and a digest
  alarm name. Profile-saved cancellation names must exactly match
  `tvguide-catchup-` plus 64 lowercase hex digits. Old/raw names are **not** replayed
  through CancelAlarm, nor migrated; old installed alarms still require clean setup.
* Related service startup/cache-refresh calls were traced: their reminder/autoplay
  entrypoints reach these same guards. Service RunAddon/RunScript commands are
  fixed literals, `stop.py` has a fixed PlayerControl command, and the GUI action
  dispatcher still reads only installed bundled actions. `service.py` is unchanged.
  This does not authorize any installed plugin/VPN/provider side effect.

API/grammar basis checked against official **19.4-Matrix** source:
[Player.h](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/interfaces/legacy/Player.h)
documents `play(item=...)` filename/URL/playlist data;
[Util.cpp](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/Util.cpp)
`SplitExecFunction` / `SplitParams` parse parentheses, commas, double quotes and
backslash escapes;
[GUIBuiltins.cpp](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/interfaces/builtins/GUIBuiltins.cpp)
`AlarmClock` stores argument 1 as the later executable command. Hence validating
only the displayed Notification or URL is insufficient: the **alarm name** could
replace the executable argument. Percent-encoding is URL data encoding, not a
general Kodi command escaper. Installed plugins receiving decoded URLs remain a
separate trust boundary.

### Task 02 actual managed discovery (read-only only)

After loading MCP testing and current managed/role/contract references,
`tvguide_lab_target_list({})` and `tvguide_lab_managed_status({})` both succeeded.
The actual exposed session schema includes all **46** `tvguide_lab_*` tools;
older aliases are not exposed. This supersedes Task 1's unavailable-alias report,
but listed schemas are not proof that every mutation is authorized or usable.

| Catalog release | Target ID | Observed state |
| --- | --- | --- |
| Matrix **19.4** | `84408fd1-cfe7-5359-851b-0d3523744f05` | provisioned, stopped |
| Nexus **20.5** | `f304dbe9-abda-5dd1-b666-32668864cc2b` | provisioned, stopped |
| Omega **21.3** | `908822fe-132a-5283-ac40-04e26d387db3` | provisioned, stopped |
| Piers **22.0-rc.2** | `48fc9315-05ca-54b5-a7ee-2865a4c457e5` | provisioned, stopped |
| Piers **22.0-rc.1** | `78041e72-ad35-51f1-b8c3-3eed0b50cf49` | unprovisioned, stopped; not an acceptance target |

Four version slots report `authorized=true`, `native_ready=false`, no pending
operation/request, Bridge `unknown` (`stored_identity_requires_observation`) and
workspace authority `not_assessed`. These are **catalog/status observations**, not
live native build, Bridge, inventory or feature acceptance. Exact profile/runtime
identities and read-only results are retained privately. No Start, Stop, Reset,
native launch/mutation, navigation, workspace creation/validation/deployment,
execution, UI, screenshot, logs or production access. No workspace generation or
mutation receipt was created. Inventory must be inspected before any later
authorized deployment; a disabled add-on requires supported administrator enablement.
Current launch-tool availability has not been exercised or qualified for this
mixed Program/service manifest.

### Task 02 focused evidence / remaining gates

`/home/kyle/kodi-development/toolkit/.local/matrix/bin/python -I -B tests/check_command_data.py`
passes inert captures extracted from actual `fe5e72f` templates: malicious alarm
names substitute `RunScript(INERT_MARKER)` into the executable argument; raw URL
commas split PlayMedia/RunPlugin arguments. No captured command is dispatched.
Positive reminder/catchup captures retain the expected argument counts after
validation/digesting/encoding; hostile delimiters cannot become additional command
syntax. Only the **new pure helper** is loaded; legacy modules and Kodi stubs are
never imported or initialized. AST wiring checks are not runtime callback tests.
The existing source-only safety check and `git diff --check` also pass. Full output,
including preexisting invalid-escape SyntaxWarnings, is in
`.git/modernization-evidence/task02-*`, outside the runtime payload and commits.

No four-lane Toolkit rerun: reuse Task 1's six-stage **FAIL/PASS/FAIL/PASS/SKIPPED/
SKIPPED** record below, with all warnings and negative controls preserved. Five
Python 2 syntax failures and Toolkit [#31](https://github.com/kcook98765/kodi-agent-toolkit/issues/31)
remain; no fake `login`, manifest workaround, tool/config/dependency edit or port.
Ancestor instruction reads remained policy-denied in this session; no bypass was
used. Shared instructions and original skills were read. Local excluded
`opencode.json` was neither read nor edited/committed.

**Stop for independent #7 review.** The identified command-grammar paths are
corrected in source, not natively accepted or a full hostile-input audit. Remaining
launch gates: independent approval; Python 3/API/dependency work (#2/#3); later
authorized known-clean installed tree/old-alarm handling, enabled inventory,
exact profile/workspace generation and validation/deployment/launch authority;
then fresh native feature observations on each approved version. The broader
feed/SQL/path/resource/privacy/plugin risks in Task 1 remain open. No merge,
release, tag, package or distribution publication is part of this correction.

---

# Task 1: historical source safety assessment

Scope: parent #1 / safety #7, starting at
`0e46733e9e5f7711f2381562cfbb98fd3b54b429`, branch
`safety/remove-remote-code`, targeting fork `main`. This is source hardening,
**not a runnable Python 3 port, release, or native-safety approval**. Original
primaeval/Tommy Winther/FTV attribution, GPL headers, `LICENSE.txt`, manifest
identity/version and upstream metadata are preserved. `master` is not edited.
All source and documentation changes in this branch are OpenCode's implementation;
Codex is the independent acceptance reviewer.

## Instructions and authority

Read the original Toolkit development, validation, version compatibility and MCP
testing skills, their validation/version and current managed/role/contract
references, and shared `COMMON-INSTRUCTIONS.md` / `KODI-TOOLKIT-LOCAL.md`.
Ancestor instruction reads were denied by session policy; the supervisor supplied
the applicable `/home/kyle/kodi-development/AGENTS.md` requirements directly.
No sibling-project scan or permission workaround was used after that instruction.
No project-local `AGENTS.md` was found.

Read-only discovery: exposed `kodi_lab_target_list({})` and
`kodi_lab_dev_target_list({})` each returned
`{"next_cursor":null,"schema_version":1,"targets":[]}`. These connections work,
but supplied no authorized target under those credentials. Subsequently the
supervisor reported a supported campaign alias `tvguide_lab` with Full Development;
that alias's tools were **not exposed in this session's tool schema** and could not
be called here. This is a session/authority availability limit, not a Lab defect.
The supervisor reports stopped Matrix **19.4**, Nexus 20.5, Omega 21.3 and Piers
22.0-rc.2; these are not independently observed runtime receipts. Historically,
19.5 was requested but absent. The owner subsequently **authorized Matrix 19.4**
as the acceptance target and the supervisor updated #1/#8: the version-mismatch
blocker is resolved by that scope decision, with no 19.5 acquisition required.
No production target was inspected.

Task 1 authorizes no native mutation or launch: no Start/Stop/Reset, workspace
creation/import/validation/deployment/execution, screenshots or native logs were
performed. No workspace generation, deployment or execution receipt exists.
Future enabled-inventory and exact-generation gates remain required. A Program
script plus service is not eligible for the control-free fixed video smoke;
`workspace_execute` is not a generic launcher and `workspace_launch` is unavailable
in this session. Do not alter the manifest just to obtain a smoke receipt.

## Core entrypoints and retained behavior

* `addon.xml:13-16`: Program script `addon.py` and login service `service.py`.
* `addon.py` opens `gui.TVGuide` / `script-tvguide-main.xml` modally. It also sets
  launch category/source/channel and fetches two fixed PNG backgrounds, not code.
* `gui.py`: fullscreen/quick EPG, categories, channel/program navigation,
  stream setup, internal program search and ordinary Kodi playback remain.
* `source.py`: database, XMLTV primary/secondary/tertiary inputs, and legacy
  provider adapters; `fileFetcher.py`: data fetch/gzip; `streaming.py`: mappings.
* `service.py`: background data updates, ordinary reminders/autoplay and optional
  self-autostart remain. `notification.py`, `autoplay.py`, `play.py`, `stop.py`
  implement these non-recording schedulers.
* Settings invoke packaged maintenance helpers (`ResetDatabase.py`, `editor.py`,
  `ReloadAddonFolders.py`, logo/image/subscription/shortcut utilities). These are
  source entrypoints too, not evidence they have been run or modernized.

## Removed executable and obsolete paths

Line references below are **original checkpoint lines**, so deletions can be
reviewed with `git show 0e46733:<path>` without executing anything.

| Original path / lines | Concrete removal or restriction |
| --- | --- |
| `service.py:76-85` | Removed both encoded short-URL HTTP requests, version/id referer and downloaded `exec(main)`. Removed requests/base64 imports. The version-setting update remains local only. |
| `playwith.py:156,170-172`, `playwithchannel.py:153`, `stopwith.py:20-22`, `stopwithchannel.py:17-20` | Deleted executable helpers, including configurable ffmpeg/Popen, shell process killing, and profile Python override dispatch. |
| `resources/playwith/{playwith,playwithchannel,stopwith,stopwithchannel}.py` and `resources/playwith/Android/` equivalents | Deleted all eight bundled external-player/process examples, plus their obsolete readme/playercorefactory example. No downloadable replacement. |
| `autoplaywith.py:51-88`, `service.py:60-62`, `gui.py:4071,4076` | Deleted recording scheduler and removed its GUI/service initialization; stale stored recording rows are not scheduled. Database tables retained, no destructive migration. |
| `gui.py:3173-3218` | Removed configured external-player/ffmpeg and profile-script execution. Old method/keymap callbacks are inert returns. Recording scheduler menu/list entries and settings removed; all bundled popup recording buttons hidden/disabled. |
| `addon.py:30-45` | Removed unused imports and dormant executable-bit/ffmpeg block. |
| `gui.py:439-451,476-481` | Removed profile `pickle.load` and pickle writes entirely. Image cache remains in memory; old pickle files are never read/migrated and are not deleted from any user profile. |
| `gui.py:131-139` | Removed profile/external skin roots. Allow only bundled `Default`, `Dark`, `CatBar`, with fallback; removed external skin settings. No remote skin Python downloader was found in the checked-in runtime. |
| `gui.py:1443-1445,4095-4103` (initial safety baseline) | Removed MINE custom builtin execution. Task17 restores profile action-bar choices only through the code-owned closed catalog, never raw profile commands; see [action-bar customization](action-bar.md). Old settings cannot restore arbitrary execution. |
| `search.py:74-116`, `resources/favourites.xml` | Deleted external search/builtin-template dispatcher and obsolete bundled templates. Popup Search now uses internal guide search. |
| `gui.py:1135-1178,2203-2245` | Removed external ExtendedInfo RunScript dispatch and its obsolete shared API-key requests; popup controls hidden and keymaps cannot re-enable it. |
| `gui.py:3141-3146,3246-3250` | Removed `@` RunPlugin command mappings and direct imported `ActivateWindow` execution, including fallback route. Ordinary media/plugin playback retained. |
| `fileFetcher.py:150,153` | Removed explicit TLS-verification bypasses from XMLTV/data fetch. Invalid HTTPS certificates must fail, not silently downgrade verification. |
| `sdAPI.py:63-64,80-82,94-95,121-123`; `utils.py:120-121` | Removed token, response-body, POST-body and setting-value logging (provider credentials included). Kept status/severity diagnostics. |

## Runtime-tree audit and residual gates

Reviewed executable sinks and their callers/settings across all root Python,
bundled Python (including pytz), skin XML, settings, JSON and favourite templates;
retained the file/sink inventory privately. This is a manual/source scan, not a
formal proof. No remaining runtime exec/eval, subprocess/Popen, shell runner,
profile Python loader or archive member extraction was found. Vendored pytz's
pickle doctests/reduction hooks are not a profile `pickle.load` sink and were
not modified. AES/base64 in source/mapping import is data transformation, not
evaluation; the old unauthenticated ECB format is not trustworthy encryption.

* **Independent #7 review is still required before any native add-on launch.**
  Remaining formatted Kodi builtins in reminders/autoplay and catchup use
  channel IDs, titles, URLs and settings. Their argument quoting/command grammar
  is **not proven safe for arbitrary hostile feeds**. In particular inspect
  `notification.py:62-77`, `autoplay.py:62-77`, `play.py:37`, and `gui.py`'s
  `catchup_meta`, play-beginning and alternative-playback RunPlugin paths. They
  are not Python downloaders, but form a residual command-injection review gate;
  do not represent this PR as closing all untrusted-input safety concerns.
* Installed plugin playback, fixed favourites windows, RPC directory enumeration
  (`ReloadAddonFolders.py`, stream setup), and VPN Manager API integration can
  invoke other installed add-ons or change VPN state. Retained for later #6/#7
  review, not implicitly authorized in fixtures or native acceptance.
* `backup.py` only imports/exports fixed-profile channel mappings, not credential
  archives or uploads. Autosave mapping files can nevertheless contain private
  stream URLs/credentials. No remote backup/uploader was found. SchedulesDirect
  POST/PUT/DELETE calls are provider account/data operations, not backup upload.
  Stored credentials, URL logging, provider error dialogs and imported URLs need
  a broader privacy policy before real-user testing; use no real credentials.
* No ZIP/tar extraction was found. `fileFetcher.py:193-199` decompresses gzip to
  a predetermined data destination; decompressed size/download time are unbounded.
  XMLTV/HTML/image parsing, logo filenames derived from titles (`utils.getLogo`),
  legacy HTTP URLs, unchecked feed sizes, redirects and SQL construction in
  `source.py` need hostile-input/path/resource-limit review in #4/#6/#7.
  Five yo.tv HTTP scrape calls retain `verify=False` in `source.py`; this PR
  repairs XMLTV's bypass, not every legacy provider transport.
* Source removal does not prove deletion of files already installed in a Kodi
  profile. No user data, scripts, timers, old settings or installed trees were
  touched. Later testing requires an administrator-prepared known installation;
  stale installed recording files/alarms must not be treated as removed by a copy.

## Static evidence (not native acceptance)

Private full output: `.git/modernization-evidence/`, deliberately not committed
or part of the runtime payload. Commands run from the actual add-on Git root:

```
/home/kyle/kodi-development/toolkit/.local/matrix/bin/python -m kodi_agent_toolkit.cli stub-lanes
/home/kyle/kodi-development/toolkit/.local/matrix/bin/python -m kodi_agent_toolkit.cli validate /home/kyle/kodi-development/addons/script.tvguide.fullscreen --branch matrix --cache /home/kyle/kodi-development/toolkit/.local/index-cache
/home/kyle/kodi-development/toolkit/.local/matrix/bin/python -I -B tests/check_safety.py
```

Matrix baseline retains all six stages: syntax **FAIL** (Python 2 in
`ResetDatabase.py`, `pyaes.py`, `service.py`, `source.py`, `streaming.py`), manifest
**PASS**, paths **FAIL** (`login`), package **PASS** as reported, types **SKIPPED**
(syntax), official checker **SKIPPED** (paths). No original failure was converted
into a pass claim. Final branch-matched runs retain these blockers; see each
`*-final.json` and `*-stub-lanes.json` for actual output, warnings and scope.
No dependency downloads, cache refresh, config changes or tool installation.
The Matrix baseline and all four final validation processes exited **1**, matching
their JSON returncode (confirmed by supervisor tool-state metadata). There is no
CLI exit-status defect. Stage results, not a completed tool call, determine this
assessment.

All four final runs reported the same six-stage result above. Each ran its own
`stub-lanes` first, then `validate` with its matching branch and the explicit cache:

| Target | Toolkit-relative interpreter | Observed Kodistubs |
| --- | --- | --- |
| Matrix 19.4 | `.local/matrix/bin/python` | 19.0.3 |
| Nexus 20.5 | `.venv/bin/python` | 20.0.1 |
| Omega 21.3 | `.local/omega/bin/python` | 21.0.0 |
| Piers 22.0 RC2 | `.local/piers/bin/python` | 22.0.1rc1 |

All reported CPython 3.12.3/Linux, mypy 2.4.0 and kodi-addon-checker 0.0.36.
These static runs preceded the owner's Matrix 19.4 scope update; the Toolkit's
`stub-lanes` catalog labels its Matrix runtime mapping 19.5. The actual evidence
is Matrix-major static checking with Kodistubs 19.0.3, not a 19.4 native result or
an assertion of patch-specific API coverage. No source/stub environment was
silently switched to implement the owner decision.
The focused check passed on 40 runtime Python files, retaining 11 preexisting
invalid-escape SyntaxWarnings from parsing `gui.py`. Piers retains the explicit
checker-3.0.1-versus-RC2-3.1.1 coverage warning. No checker index replay/cache
provenance was established because the official stage was skipped, not passed.

Focused source-only regression checks include original-checkpoint negative
controls for service exec, pickle, process execution and shell-kill paths; inspect
inert callbacks, bundled action loading, missing removed files/settings, XML
visibility and TLS change. They never import/execute a legacy add-on file or Kodi
stub. A first test-development failure on the broader legacy TLS scan is retained
in `check-development-notes.txt`; TLS assertions are deliberately XMLTV-scoped.

### Reproducible Toolkit defect for supervisor triage

`toolkit-service-start-repro-clean.json` uses the inert, never-executed
`.git/modernization-evidence/service-start-fixture/{addon.xml,service.py,LICENSE.txt}`.
Its manifest declares `library="service.py" start="login"`; only the library is
a file. `validate.py:181` and `checker_runner.py:128` instead treat **start** as a
path, reject missing `login`, and suppress official checker execution. Reproduce
with the same Matrix CLI/cache and the fixture root. Do not create a fake `login`
file or remove lifecycle metadata to hide the defect. Initial fixture packaging
failures and the cleaned fixture result are retained separately. No tooling edit
was made. Supervisor filed the reproduced defect as
[kodi-agent-toolkit #31](https://github.com/kcook98765/kodi-agent-toolkit/issues/31).

The source-root validator snapshot also includes `.git` metadata/evidence hashes;
its package PASS is not proof of a distributable ZIP excluding development files.
No package was built. Full JSON stays private (no auth file contents were read).
Supervisor-owned local `opencode.json` is excluded by `.git/info/exclude` and must
not be committed, copied into fixtures, or included in any future package. The
supervisor independently verified the campaign catalog has 46 tools server-side;
this session's cached schema still does not expose the alias. An idle exact-project
refresh is supervisor-owned, not part of this task.

## Minimal next shared work and version boundaries

Smallest next task (#2): mechanically convert the five known Python 2 syntax
failures, then shared imports (`thread`, `urllib2`, `ConfigParser`, `HTMLParser`,
`izip_longest`), `unicode`/bytes/text/iteration and division semantics. Replace
removed `xbmc.translatePath` with `xbmcvfs.translatePath`, and `LOGNOTICE` with
verified `LOGINFO`; do not invent numeric constants. Fix source/type errors before
claiming GUI behavior. Keep the public manifest's `xbmc.python=2.19.0` unchanged
in this safety PR; #2/#3 must set an appropriate Python 3 dependency and qualify it.

Shared target floor is Matrix API 3.0.0; Nexus/Omega provide 3.0.1; exact Piers
RC2 provides 3.1.1. `xbmc.translatePath` is removed in Nexus+, not merely deprecated;
modern InfoTag setters and `Addon.getSettings` are Nexus+, so prefer the oldest
verified common API or a measured guard. No version-specific source forks needed
yet. Tool Python 3.12.3 is not Kodi's embedded Python. Matrix 19.0.3 stubs use the
reviewed validator-only metadata annotation overlay; Piers 22.0.1rc1 is bounded
prerelease evidence, with retained stale checker dependency advice, not full RC2
API qualification. Each interpreter must precede its matching `--branch` choice.

#3 also needs review of legacy simplejson/requests/dateutil/PIL/bs4 declarations,
bundled old pytz/pyaes, undeclared optional add-ons, settings relative conditions,
types/defaults and persistence. No blanket dependency bump belongs in task 1.

Fixture proposal for #4/#6: tiny owner-authored XMLTV with stable IDs, timezone
offsets, Unicode titles and a few programs; local/generated media and M3U without
plugin actions, external scripts, provider credentials or network dependencies.
Include hostile delimiters, traversal-like titles and oversized gzip negatives
before trusting feed data. Keep clocks/expected programme times deterministic.
Later package only runtime files; exclude `.git`, docs, tests, evidence, caches and
agent configuration. Sequential native tests require independent safety approval,
actual exact version/profile/source identities and feature observations, not only
dispatch or static validation. Stop this task at draft PR review; do not merge.
