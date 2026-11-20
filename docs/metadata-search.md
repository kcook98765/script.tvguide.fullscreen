# Optional metadata and named add-on search — partial source restoration

Refs #14, #7, #5, #1. One shared implementation for Matrix 19.4, Nexus 20.5,
Omega 21.3 and Piers 22 RC2, not four ports. **Native results/details, window
transitions and return-to-guide behavior remain untested on all four.**

## User path and prerequisites

- In Default/CatBar, the existing Extended Info button is now **TMDbHelper
  lookup…**, visible even when the optional provider is absent. The existing
  `EXTENDED_INFO` key-editor alias opens the same choices (no new default binding).
- Existing **iSearch/Search** menus keep Title, Synopsis, Category and Channel
  guide searches unchanged, then offer **TMDbHelper movie / TV lookup…**. This also
  supplies the path on Dark, which has no Extended Info control. No unrelated
  layout, recording control or skin-loading changes are included.
- Choose **Movie** or **TV show**, then accept/edit the original programme title.
  With no selected programme the keyboard accepts a new title. Choose the result
  in TMDbHelper's directory; use Kodi's **Information** on a result for details,
  or the provider's configured information/related UI. Ordinary select behavior is
  controlled by TMDbHelper: its default-select setting may play rather than open
  details. This guide neither configures nor invokes its custom player machinery.
  Use Back to leave the provider UI. This is a lookup handoff, not an automatic
  match or guide metadata replacement.
- Requires the user's **already installed and enabled**
  `plugin.video.themoviedb.helper`, its own compatible dependencies, and its online
  metadata access/setup. Official snapshots reviewed: **4.10.14** for Matrix
  (`xbmc.python` 3.0.0); **5.4.16** on newer Kodi (3.0.1). Availability is not native
  qualification. The adapter admits numeric 4.x >=4.10.14 and 5.x >=5.4.16 versions;
  later patches are not individually qualified. Unknown majors, older/unrecognized
  versions and suffixed forks explain the unsupported contract rather than guess.
  Kodi still determines whether the installed provider/dependencies are compatible.
  There is no hard dependency, installer, enabling action or API-key handling here.
- Missing/disabled/unverifiable providers and dispatch failures show useful
  explanations and leave internal guide search available. Selection cancellation
  or an empty keyboard result returns without opening the provider. An uncertain
  reply is **not retried**; window acknowledgement is not results/details success.
  Network/service errors after opening the directory belong to the provider UI;
  this adapter cannot observe or certify them.

## Exact data/dispatch contract

The new `metadata_search.py` is stdlib-only. GUI adapters supply only
`xbmc.executeJSONRPC`, `xbmcgui.Dialog` and the programme title. It reads
`Addons.GetAddonDetails` for the **fixed** ID with
`properties=["installed","enabled","version"]`, checks exact identity and literal
boolean installed/enabled state, and rechecks after keyboard interaction. It does
not treat an installable catalog entry as an installed provider.

The only dispatch is:

```json
{"jsonrpc":"2.0","id":3,"method":"GUI.ActivateWindow","params":{"window":"videos","parameters":["plugin://plugin.video.themoviedb.helper/?info=search&tmdb_type=movie&query=<percent-encoded-title>","return"]}}
```

`tmdb_type` is exactly `movie` or `tv`. Query construction uses Python
`urllib.parse.urlencode(..., quote_via=quote, safe='')`; quotes, apostrophes,
commas, parentheses, backslashes, Unicode, literal `+`, `%`, `#`, `&`, `=` and
`&&` are **encoded data**, never receiver parameters/actions. Tab, LF and CR from
valid XMLTV text are preserved as `%09`, `%0A`, `%0D`, not deleted/denied or silently
collapsed. Non-string, blank and >1024-character input is refused with an explicit
message (a bounded interactive search, not a bulk URI). XML-invalid C0 controls
other than tab/LF/CR and unpaired Unicode surrogates are refused; DEL is not denied.
There is no punctuation blacklist and no title/year/episode stripping in the guide.

No `Addons.ExecuteAddon`, raw-title builtin strings, arbitrary IDs/actions,
profile templates/Python/pickle, scraping, downloader or HTTP metadata framework
is added. Structured JSON by itself is **not** the safety argument: Matrix–Omega
`Addons.ExecuteAddon` object parameters enter un-Paramified `RunAddon` grammar.
This path instead sends the encoded fixed plugin URI through the GUI parameter
vector, with no addon command serialization. Previously removed arbitrary-command
and downloaded-code protections remain.

## Receiver and tagged Kodi evidence (2026-11-19)

Task04 research in [#14](https://github.com/kcook98765/script.tvguide.fullscreen/issues/14)
is reused; only this route, its parsers and inventory/window contracts were checked.
Official provider ZIPs were inspected in memory, never installed/executed:

| Official ZIP | SHA-256 |
| --- | --- |
| [TMDbHelper 4.10.14][tm4] | `5d20a98dfc14e7eda94c5ad71a997d68ab767d577479bf95bc679af7ccd5f706` |
| [TMDbHelper 5.4.16][tm5] | `3e79b35ff103bf86cb99747dd092e22565af269d571beadab7ab40f86e9238dc` |
| [jurialmunkey 0.2.2][jm2] (5.4.16 minimum dependency) | `103d5ac324b26de1827f3ec2e9db9d3e6f9a76444a452f6ada2a97497b943fba` |
| [jurialmunkey 0.2.28][jm28] (published newer dependency) | `99bbad7b9eefc587042d6b605a55f3a20dfbc78fef1d7bd79507f9c8d9dd7172` |

- 4.10.14 `plugin.py` → `resources/lib/items/router.py`: removes the leading `?`,
  parses with `addon/parser.py::parse_paramstring`, reconfigures legacy names,
  routes `search` through `items/routes.py` to `api/tmdb/search.py::ListSearch`.
  Its parser replaces literal `&amp;`, splits on `&`, then `=`, then
  `unquote_plus` on keys/values. Every query `&`/`=` is encoded before splitting.
  `reconfigure_legacy_params` does not alter this fixed movie/TV query.
- 5.4.16 `resources/plugin.py` → `resources/tmdbhelper/lib/items/router.py`: splits
  secondary paths at **literal** `&&` before calling `jurialmunkey.parser`.
  Encoded query `&&` cannot make secondary paths. Both inspected jurialmunkey
  parsers split/decode similarly but then apply **`v.strip("'").strip('"')`**.
  **This can strip boundary apostrophes/quotes; it is a known provider-side
  difference**, not exact-title preservation or a reason to reject punctuation.
  Interior quotes/apostrophes, whitespace and Unicode are not normalized there.
  Future dependency versions remain subject to provider changes.
- Both `ListSearch.get_items` pass the decoded query to `get_search_list`, which
  applies `quote_plus` for the metadata HTTP search request. 5.x implements that
  in `api/tmdb/methods/lists.py`. No guide-injected alternate action is derived
  from the query. Search matches/ranking and any downstream service normalization
  remain provider behavior. A nonempty supplied query avoids provider prompting
  and its empty-query container rewrite. This adapter does not request search
  history persistence; provider-owned API caches/settings remain its concern.
- Result info comes from provider `items/listitem.py`/container building;
  `_set_params_reroute_default` confirms select may route to `play` or `related`.
  Do not interpret successful directory opening as a guaranteed details dialog.

For **each** official tag [19.4-Matrix][k19], [20.5-Nexus][k20],
[21.3-Omega][k21], [22.0rc2-Piers][k22], inspected
`xbmc/interfaces/json-rpc/schema/{methods,types}.json`,
`AddonsOperations.cpp::{GetAddonDetails,FillDetails}` and
`GUIOperations.cpp::ActivateWindow`:

- `Addon.Fields` permits **installed**, **enabled**, **version**; `Addon.Details`
  types them boolean, boolean, string and requires addonid/type. GetAddonDetails
  returns `result.addon`, including disabled installed add-ons; a missing add-on
  fails. FillDetails reads installed/enabled from the add-on manager, not XML.
- GUI.ActivateWindow accepts the string parameter array, translates `videos`,
  and queues `TMSG_GUI_ACTIVATE_WINDOW` with that vector. These parameters are
  not concatenated into a builtin command. This is API/source evidence only.

## Focused checks and retained limits

`tests/check_metadata_search.py`: **11 pure/AST checks**, exact movie/TV payloads,
original default title, punctuation/Unicode/command-looking text, literal query
delimiters and benign multiline/tab/CR titles, actual receiver boundary/known
quote difference, unsupported/uninstalled/disabled/stale provider, cancellation,
RPC errors/lost/malformed replies, GUI menu/adapters and key alias. Four in-memory
negative controls detect unsafe ExecuteAddon dispatch, comma loss, disabled
provider bypass and cancelled-choice dispatch. No Kodi/stub/legacy host imports.

Existing safety/command-data, six reminder, twelve PVR and four fixture/loader
checks pass. The PVR test changes only its old assertion that the unrelated
metadata alias is forcibly empty; recording code/docs/payloads are untouched.
Changed-source Python 3.8 AST and narrow Matrix-stub typing/signatures pass.
The deliberate bad-signature probe exits **1**, retaining four expected errors.
Runtime stdlib additions (`json`, `re.fullmatch`, `urllib.parse.urlencode`,
`quote_via`) exist in Python 3.8; this does **not** run embedded Matrix Python.

Tool interpreter: `/home/kyle/kodi-development/toolkit/.local/matrix/bin/python`,
CPython 3.12.3/Linux; observed Kodistubs19.0.3, mypy2.4.0, checker0.0.36.
Matrix stub qualification is 19.5, not requested native19.4. Piers retains bounded
RC2 qualification. Existing GUI invalid-escape SyntaxWarnings remain visible.

No new full validator/four-lane suite was run: the CLI has no stage selector;
this scope uses narrow checks rather than requalifying legacy source. All six
task03 receipt stages/hashes are retained privately: syntax/manifest/paths/package
passed **then**, types/official_checker **failed** on all four. Latest PR16 Nexus
651 type diagnostics / 73 checker errors / 11 warnings also remain unresolved.
Neither historical passes nor a summary-reader exit0 qualify these new bytes.
Private `task10-*` evidence under `.git/modernization-evidence/` records actual
child `subprocess.returncode`, full stdout/stderr, source hashes and tagged-source
receipts; it is not runtime/export/package content. Two early one-line research
commands had syntax errors (no provider code ran); successful bounded research
and focused checks are recorded separately, not substituted for those failures.

All native stages #8–#11 remain **BLOCKED/UNRUN** under the existing complete
Program+service [Lab112 limitation][lab112]. Installed provider availability,
metadata network responses, result Information UI and guide return remain untested.

## Explicit #14 differences / subsequent slices

This is real **named cross-add-on search**, distinct from internal guide search,
but only for TMDbHelper. It partially replaces old ExtendedInfo/MySearch/iSearch
surfaces, not every provider/template. No new ExtendedInfo/GlobalSearch action is
needed: ExtendedInfo title normalization/ID discovery would add another contract;
Global Search is local-library search, not universal cross-add-on search.

No automatic title/year split, year filter, season/episode mapping or ID lookup
is supplied. A year embedded in the title stays query text and may need editing;
TV search is show-level, not an exact episode lookup. No plot/artwork is written
back to the guide; XMLTV details/artwork, original program model and current cache
paths are untouched. Persistent JSON match cache, arbitrary user/provider
templates, typed playback mappings/actions and external players remain separate
provisional follow-ups. There is no permanent removal decision or parity claim.
Guide sources/settings/defaults, fixtures, playback, reminders, PVR, full
Program+service manifest, GPL/attribution and original history are preserved.

[tm4]: https://mirrors.kodi.tv/addons/matrix/plugin.video.themoviedb.helper/plugin.video.themoviedb.helper-4.10.14.zip
[tm5]: https://mirrors.kodi.tv/addons/omega/plugin.video.themoviedb.helper/plugin.video.themoviedb.helper-5.4.16.zip
[jm2]: https://mirrors.kodi.tv/addons/omega/script.module.jurialmunkey/script.module.jurialmunkey-0.2.2.zip
[jm28]: https://mirrors.kodi.tv/addons/omega/script.module.jurialmunkey/script.module.jurialmunkey-0.2.28.zip
[k19]: https://github.com/xbmc/xbmc/tree/19.4-Matrix/xbmc/interfaces/json-rpc
[k20]: https://github.com/xbmc/xbmc/tree/20.5-Nexus/xbmc/interfaces/json-rpc
[k21]: https://github.com/xbmc/xbmc/tree/21.3-Omega/xbmc/interfaces/json-rpc
[k22]: https://github.com/xbmc/xbmc/tree/22.0rc2-Piers/xbmc/interfaces/json-rpc
[lab112]: https://github.com/kcook98765/kodi-lab/issues/112#issuecomment-7023719173
