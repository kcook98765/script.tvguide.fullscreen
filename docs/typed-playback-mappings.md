# Task19 — typed playback / add-on-folder mappings (refs #14 / #6 / #7 / #1)

Source-only restoration from reviewed `6d1b9162289ccc20c3ba089302dc3a149150d0be`.
OpenCode owns the implementation; independent Codex review is still required.
No master-history rewrite, attribution/license change, manifest/entrypoint change,
release, distribution or merge. Both Program script and service remain. Task14's
canonical dirty checkout and all other task worktrees are untouched.

## Inventory before changes

Compared original `0e46733e9e5f7711f2381562cfbb98fd3b54b429`, the safety removal
`70ba1c9` and pinned reviewed main above, without importing those runtime files:

| Producer / storage | Original and reviewed-main semantics |
| --- | --- |
| `StreamSetupDialog.onClick`, `updateAddonInfo` | `addons.ini` plain URL is default Player playback; clicking a stream toggles an `@` prefix for RunPlugin-style action. OK/Alternative save the string to primary/alternative mappings. Green marking remains, not proof of execution. |
| `addBrowseFolder`, `ReloadAddonFolders.py` | `folders.list` plain or `@` directory entries drive Files.GetDirectory enumeration; **file** results are saved to addons.ini plain or `@` respectively. `@` here is not a folder-open type. |
| `StreamsService.loadFavourites` / `detectStream` | Reads Kodi favourites; previously sliced `PlayMedia(...)` text and retained other text, including full ActivateWindow favourites. Exact-title detection can save these directly; choice dialogs and Favourite OK/Alternative also save them. |
| `loadChannelMappings` | mapping.ini splits once at `=`; M3U URL entries (also channel creation) go to primary mappings. Percent/query data are not Kodi instructions. Existing import whitespace trimming is unchanged. |
| `source.Database`, `backup.py`, GUI close autosave | Primary `custom_stream_url` and alternative `alt_custom_stream_url` retain strings; primary INI and alternative TSV import/export preserve stored mapping forms. No schema/migration or rewrite in this task. |
| `TVGuide.playChannel`, `waitForPlayBackStopped` | Original `@` built RunPlugin, imported ActivateWindow executed raw; reviewed main silently returned success/no-op for both, after primary Player.stop/clear-catchup. Normal media/plugin playback uses Player, VPN selection, M3U-bandwidth selection and existing alternates. |
| Stream setup preview | Previously passed every mapping verbatim to Player, and stopped any existing player before reading the selection. |
| Scheduled `play.py` | Original formatted PlayMedia; reviewed main uses Player with a DB primary mapping verbatim. VPN and playing-channel/start bookkeeping precede playback. This is not the GUI RunPlugin/folder contract. |

Task17 owns action-bar commands, Task16 external players, Task14 settings/requires,
Task13 scheduler ownership, Task12 cache, Task15 metadata/languages. None are
reimplemented here. **PR20 is now merged on current main**: later supervised
integration must retain its reviewed `main(argv)` decoder/legacy-argument handling
and place this task's small mapping guard *before* bookkeeping/VPN/player inside
that callback. Do not copy this pinned base's older top-level `play.py` over main.
No current-main reconciliation or merge is attempted before draft review.

## Four exact-tag primary API / receiver research

Read upstream xbmc/xbmc, not moving-master documentation:

| Intended release | Structured entry / schema | RunAddon receiver | Folder receiver |
| --- | --- | --- | --- |
| Matrix **19.4** | [GUIOperations](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/interfaces/json-rpc/GUIOperations.cpp), [AddonsOperations](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/interfaces/json-rpc/AddonsOperations.cpp), [methods](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/interfaces/json-rpc/schema/methods.json) | [AddonBuiltins](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/interfaces/builtins/AddonBuiltins.cpp) | [window manager](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/guilib/GUIWindowManager.cpp), [media window](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/windows/GUIMediaWindow.cpp) |
| Nexus **20.5** | [GUIOperations](https://github.com/xbmc/xbmc/blob/20.5-Nexus/xbmc/interfaces/json-rpc/GUIOperations.cpp), [AddonsOperations](https://github.com/xbmc/xbmc/blob/20.5-Nexus/xbmc/interfaces/json-rpc/AddonsOperations.cpp), [methods](https://github.com/xbmc/xbmc/blob/20.5-Nexus/xbmc/interfaces/json-rpc/schema/methods.json) | [AddonBuiltins](https://github.com/xbmc/xbmc/blob/20.5-Nexus/xbmc/interfaces/builtins/AddonBuiltins.cpp) | [window manager](https://github.com/xbmc/xbmc/blob/20.5-Nexus/xbmc/guilib/GUIWindowManager.cpp), [media window](https://github.com/xbmc/xbmc/blob/20.5-Nexus/xbmc/windows/GUIMediaWindow.cpp) |
| Omega **21.3** | [GUIOperations](https://github.com/xbmc/xbmc/blob/21.3-Omega/xbmc/interfaces/json-rpc/GUIOperations.cpp), [AddonsOperations](https://github.com/xbmc/xbmc/blob/21.3-Omega/xbmc/interfaces/json-rpc/AddonsOperations.cpp), [methods](https://github.com/xbmc/xbmc/blob/21.3-Omega/xbmc/interfaces/json-rpc/schema/methods.json) | [AddonBuiltins](https://github.com/xbmc/xbmc/blob/21.3-Omega/xbmc/interfaces/builtins/AddonBuiltins.cpp) | [window manager](https://github.com/xbmc/xbmc/blob/21.3-Omega/xbmc/guilib/GUIWindowManager.cpp), [media window](https://github.com/xbmc/xbmc/blob/21.3-Omega/xbmc/windows/GUIMediaWindow.cpp) |
| Piers **22.0 RC2** | [GUIOperations](https://github.com/xbmc/xbmc/blob/22.0rc2-Piers/xbmc/interfaces/json-rpc/GUIOperations.cpp), [AddonsOperations](https://github.com/xbmc/xbmc/blob/22.0rc2-Piers/xbmc/interfaces/json-rpc/AddonsOperations.cpp), [methods](https://github.com/xbmc/xbmc/blob/22.0rc2-Piers/xbmc/interfaces/json-rpc/schema/methods.json) | [AddonBuiltins](https://github.com/xbmc/xbmc/blob/22.0rc2-Piers/xbmc/interfaces/builtins/AddonBuiltins.cpp), [parameter builder](https://github.com/xbmc/xbmc/blob/22.0rc2-Piers/xbmc/interfaces/json-rpc/AddonsExecuteAddon.cpp) | [window manager](https://github.com/xbmc/xbmc/blob/22.0rc2-Piers/xbmc/guilib/GUIWindowManager.cpp), [media window](https://github.com/xbmc/xbmc/blob/22.0rc2-Piers/xbmc/windows/GUIMediaWindow.cpp) |

All four GUI.ActivateWindow implementations copy string array elements to a
vector in TMSG_GUI_ACTIVATE_WINDOW. GUIWindowManager::OnApplicationMessage forwards
that vector to ActivateWindow, then GUI_MSG_WINDOW_INIT.SetStringParams.
CGUIMediaWindow reads element 0 as directory and element 1 as `return` (history / Back
behavior), **not** command text. Also traced each tag's
`video/windows/GUIWindowVideoNav.cpp::GetStartFolder` →
`GUIWindowVideoBase.cpp::GetStartFolder` → `CGUIMediaWindow::GetStartFolder`:
plugin:// URIs are returned unchanged. Quotes/commas/parentheses in the **data
vector** do not create extra arguments. Provider URL interpretation remains an
installed add-on trust boundary; opening a directory can execute provider Python
and use its existing network access. No provider is configured/installed/enabled.

The same exact four tags' `programs/GUIWindowPrograms.cpp::OnMessage` forwards
GUI_MSG_WINDOW_INIT to CGUIMediaWindow; `GetStartFolder` resolves optional source
names/locks, otherwise passes plugin paths to the base unchanged.
`input/WindowTranslator.cpp` maps fixed `programs` and `videos` names on all four.
Thus the only second pair admitted here is **programs + executable content**;
it is plugin directory navigation, not arbitrary Program script execution.

### Favourite escaping preservation (interim supervisor correction)

Read each of the four tags' `favourites/FavouritesService.cpp`,
`utils/StringUtils.cpp::Paramify` and `Util.cpp::SplitParams`; additionally read
`utils/ExecString.cpp` on Nexus/Omega/RC2 (Matrix produces the string directly in
CFavouritesService::GetExecutePath). Exact primary examples:
[Matrix producer](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/favourites/FavouritesService.cpp),
[Nexus producer](https://github.com/xbmc/xbmc/blob/20.5-Nexus/xbmc/utils/ExecString.cpp),
[Omega producer](https://github.com/xbmc/xbmc/blob/21.3-Omega/xbmc/utils/ExecString.cpp),
[RC2 producer](https://github.com/xbmc/xbmc/blob/22.0rc2-Piers/xbmc/utils/ExecString.cpp).
All four Paramify implementations **double backslashes, backslash-escape double
quotes, then enclose in double quotes**. All four receiver grammars invert those
escapes (Nexus/Omega also have the copied SplitParams implementation in ExecString;
RC2 calls CUtil::SplitParams). The adapter accepts exactly that quoted argument
representation and inverts **only** `\\` and `\"` once into Player/vector **data**.
No percent/Unicode escape decoding, command parsing or command reserialization.
This preserves generated Windows/local/UNC favourites and escaped-quote query
data. For example saved `PlayMedia("C:\\Media\\Film.mp4")` plays data
`C:\Media\Film.mp4`; a trailing original backslash must also have been doubled.
Hand-authored quoted wrappers with **single, non-Paramified** backslashes (e.g.
`PlayMedia("C:\Media\Film.mp4")`) remain temporarily unsupported, because treating
all such strings as literal paths would disagree with the receiver's handling of
`\\`/`\"`. A raw `C:\Media\Film.mp4` mapping is supported unchanged. This is not
a blanket Windows-playback restriction. Optional newer playlist_type_hint and
other extra PlayMedia arguments remain outside this one-argument subset.

RunPlugin instead calls CPluginDirectory::RunScriptWithParams on the original full
URI. ExecuteAddon calls **RunAddon**, not RunPlugin: a single argument starting
`/` or `?` is used as URL suffix; multiple arguments are joined with `&` after `?`.
Passing `[original_uri]` therefore does **not** preserve that URI contract. For
content plugins RunAddon constructs another ActivateWindow builtin string;
non-content plugins take a different RunPlugin path using joined parameters.
Matrix–Omega's ExecuteAddon **object** arguments concatenate un-Paramified keys
and values (Task04 finding); array/string Paramify protects only the first parse,
not RunAddon's later content-plugin string reconstruction or semantic mismatch.
RC2 Paramifies object entries and routes script vectors directly, but retains
the plugin command reconstruction. Neither branch justifies generic `@` actions.
No ExecuteAddon call, generic builtin interpreter, bridge or executable download
is introduced here.

## Implemented minimal subset and explicit temporary differences

`playback_mapping.py` is a small stdlib-only Python 3.8 adapter: typed **PLAY**,
**OPEN_FOLDER**, **RUN_ADDON**; invalid input fails with a fixed explanation.

* Raw media and plugin URI defaults remain Player data, with punctuation, Unicode,
  percent escapes and query values unchanged. Existing media VPN/M3U/alternate
  behavior remains in the callers. Simple one-argument `PlayMedia(uri)` and
  `PlayMedia("uri")` favourites are recognized without executing their wrapper.
* Interactive folder opens recognize only the complete legacy forms
  `ActivateWindow(10025,uri,return)` / `ActivateWindow(Videos,uri,return)` and
  `ActivateWindow(10001,uri,return)` / `ActivateWindow(Programs,uri,return)` (case
  insensitive command/window), also with a Paramify double-quoted URI. The internal type
  does **not** store an executable command. The destination is always fixed
  `videos` or `programs`, parameters `[original_uri, 'return']`. Addons.GetAddons filters
  installed+enabled **xbmc.python.pluginsource** with manifest **video** content;
  for Programs it requires manifest **executable** content instead. The matching
  ID/type must be present. No ID-prefix inference or auto-enable.
* Quoted legacy arguments use only the two producer escapes described above;
  unescaped embedded quotes, non-Paramified backslashes, and unquoted arguments
  containing commas/parentheses/quotes/backslashes remain temporarily rejected.
  Valid quoted arguments retain commas, parentheses, apostrophes, Unicode,
  escaped quotes and doubled backslashes as their original data. Plain URI/path
  playback retains punctuation unchanged. Refusal requires actual command shape
  (`name(`, including incomplete or unknown commands), not a name prefix:
  `PlayMediaConcert.mp4`, `RunPlugin Demo.mp4` and `RunAddon.mp4` remain media data.
  A relative filename with one parenthesized portion followed directly by a
  filename-extension suffix, such as `Movie (2026).mp4` or `Concert(HD).mkv`, is
  also unchanged Player data, not a full command expression. This tiny recognizer
  does not admit compound command expressions followed by a filename suffix.
  Malformed known ActivateWindow/PlayMedia/RunPlugin/RunAddon/RunScript wrappers
  remain rejected even with such a suffix. Unknown full command expressions and
  extra-argument controls remain rejected. No generic parser or command execution.
* `@plugin://` is typed RUN_ADDON but **temporarily blocked** with explanation;
  original strings, producers and toggles remain for later safe receiver work.
  It is never coerced into Player.play or folder navigation. Other windows,
  RunPlugin/RunAddon/RunScript command text, optional PlayMedia flags, additional
  commands, unknown/malformed or non-Paramified legacy forms remain unsupported. These
  are explicit compatibility gaps for #14, **not permanent feature dispositions**.
* Primary routing is before Player.stop, catchup clearing, playing-channel state,
  PiP and guide hiding. Selection cancellation/rejection returns False; only
  **None (missing mapping)** triggers playOrChoose auto-detection. Folder success
  means RPC dispatch acknowledged, not playback; it does not change current media
  channel, stop an existing player, switch VPN or hide the guide. Preview routes
  before its stop toggle; with a media selection the existing play/stop behavior
  is retained. A folder preview is navigation, not a stoppable playback preview.
* Fallback uses the same boundary. Folder/action results end that playback retry
  chain; rejection reports failure and redraws the guide, never silently succeeds.
  Response loss/malformed response/RPC error/denial is **unconfirmed**, no automatic
  retry (the window could already have opened). No URI/response is echoed in errors.
* Scheduled `play.py` permits PLAY only; folder UI and actions are rejected/logged
  before channel/start bookkeeping, VPN or Player, with unsuccessful exit. This
  corrects reviewed-main's verbatim command-as-media behavior; it does not redesign
  scheduling. Original code never implemented GUI-style scheduled folder actions.

Native UI/Back behavior, modal-preview window interaction, provider results,
playback and fallback acceptance are **not tested**. An RPC ACK is not completion.

## Bounded local evidence / deferred stages

Focused `tests/check_typed_mappings.py` loads only the new pure adapter and extracts
actual GUI/favourite/scheduled bodies into inert mocks; no legacy module/service,
Kodi stubs, user profile, provider or network is executed. Tests include benign
punctuation/Unicode, Windows/UNC and escaped-quote Paramify roundtrips, ordinary
command-prefix filenames, both fixed video/Programs pairs, old formats, PLAY vs
folder vs action, incompatible manifest
type/filtered inventory absence, malformed/unknown commands, response failure/loss,
no-retry/no-secret-echo, primary/fallback/preview, selection cancel/invalid index,
scheduled guard and Python 3.8 grammar. Initial regression failed on the pinned
silent-success branch before implementation. A subsequent fixture-development
failure (missing mock VISIBLE_ADDONS) is retained in private evidence, not hidden.

Final focused suite: **12 tests PASS**; existing command-data and source-only
safety checks also pass, retaining their baseline negative-control diagnostics.
Final test environment is `env -i PATH=/usr/bin:/bin LANG=C.UTF-8` only; no HOME,
home or CODEX_HOME is repurposed. Earlier pre-review test invocations used an
empty credential-free environment with HOME=/tmp/opencode; that is no longer used.

Interpreter: `/home/kyle/kodi-development/toolkit/.local/matrix/bin/python`;
stub-lanes reports CPython 3.12.3/Linux, Kodistubs 19.0.3, mypy 2.4.0, checker
0.0.36. Its Matrix catalog labels **19.5**, not requested 19.4: API evidence here
uses exact **19.4** sources, not a 19.5 native claim. Stubs are not imported or
executed by these tests. Existing 11 gui invalid-escape warnings remain, including
DeprecationWarnings from the 3.8 grammar pass. Piers retains prerelease/stale-checker
limits from the original compatibility skill.

No broad six-stage/four-lane rerun or new framework/dependency. Historical syntax,
manifest, paths, package, types and official-checker records/warnings/negative
controls in existing modernization docs/evidence remain unchanged; **none** is
claimed freshly passed by this focused test. No new Python Kodi signature is
introduced beyond existing executeJSONRPC; structured schema and receiver evidence
above is separate from static signatures. Toolkit/config/cache are untouched.

**Lab394 DEFERRED:** no Lab calls, catalog/native probes, Start/Stop/Reset,
workspaces, deployments, executions, UI/screenshots/logs, workarounds or production
access. No runtime identity/generation/receipt exists for this task. Stop at draft
PR for independent review; later current-main integration is coordinated separately.
