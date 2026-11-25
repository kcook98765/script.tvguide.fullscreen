# Action-bar customization (Task17)

> Historical task record: old activation-blocker / whole-campaign UNRUN statements
> below are superseded by the [current overview](modernization-status.md).
> Original failures and feature-specific unverified limits remain; later core
> native evidence is not blanket acceptance of this feature.

The original interface is manual editing of
`userdata/addon_data/script.tvguide.fullscreen/actions.json` (see the original
Action Bar changelog entry). **Action Editor** in Settings is a separate keyboard
command/keymap editor; it is unchanged. No new editor UI is introduced.

Close the guide, back up your file, then edit its JSON array. Each row is
`["display label", "action-id", "image string"]`. Reorder rows to reorder buttons,
include only the actions you want, and omit rows to hide buttons. `[]` deliberately
hides all buttons. Labels support Unicode and punctuation; images retain Kodi's
existing image-string semantics (including empty strings, skin image names,
paths and URLs). Image strings and labels never become commands. Reopen the guide
to load changes. Example:

```json
[
  ["Now — TV!", "now", ""],
  ["Find", "search", "button_search.png"],
  ["Quit guide", "quit", ""]
]
```

## Closed catalog

These are the original bundled defaults, in the original order. The slightly
surprising Home/First labels and associated commands are preserved, not renamed.
`action_bar.py` supplies fixed catalog tokens; profile/bundled data is never executed.

The Favorites row remains **native Kodi Favorites**, not the optional provider
selection used by the main/context buttons. Its legacy token below is retained
for saved-row compatibility; the GUI dispatches the supported native window:
`10134` on Matrix/Nexus, named `favouritesbrowser` (`10060`) on Omega/Piers.
Loading does not rewrite saved rows. See [focused verification](favourites-navigation.md).

| ID | Original label | Exact accepted legacy command |
| --- | --- | --- |
| `num` | Num | `Action(MiddleClick)` |
| `stop` | Stop | `Action(Stop)` |
| `search` | Search | `Action(Number4)` |
| `title` | Title | `Action(Blue)` |
| `now` | Now | `Action(Number2)` |
| `next-program` | Next | `Action(Number3)` |
| `remind` | Remind | `Action(Number5)` |
| `autoplay` | Autoplay | `Action(Number6)` |
| `next-page` | Next | `Action(SkipNext)` |
| `previous-page` | Prev | `Action(skipprevious)` |
| `home` | Home | `Action(FirstPage)` |
| `first` | First | `Action(LastPage)` |
| `favourites` | Favs | `ActivateWindow(10134)` |
| `quit` | Quit | `Action(Close)` |

## Persistence and original differences

- Exact known legacy command rows load as closed IDs in memory, preserving row
  order, labels and images. No command parsing, interpolation or raw fallback.
- Unknown IDs/custom commands are **temporarily unsupported**, skipped with a
  Kodi WARNING diagnostic. The remaining known rows still work. An all-unknown
  file shows no buttons. Read never rewrites/migrates/deletes the original file.
  MINE/template commands, arbitrary builtins and downloaded-code paths stay blocked.
- Missing file uses code-owned defaults without creating a file. Malformed,
  unreadable or oversized input uses defaults and a warning without changing the
  original. Limits: 64 KiB UTF-8 JSON, 32 rows, three strings per row, at most
  1024 characters per string. Escaped unpaired surrogates are malformed; valid
  Unicode, punctuation and whitespace are retained verbatim. An empty file is
  malformed; an empty array is valid.
- Startup no longer unconditionally copies bundled defaults over user choices.
  `saveActions` persists normalized IDs; there is no new auto-save or editor.
- Existing **Appearance → Reset Action Bar** explicitly replaces the profile file
  with all code-owned default choices. Back up any unsupported rows first. Reset
  reports success only after the atomic local-file replacement succeeds; failed
  save/reset reports failure and leaves the previous file intact. Reopen the guide
  after reset. Persistence expects Kodi's translated local userdata path, not a
  remote VFS profile; filesystem failure is reported, not treated as success.

The script/service manifest entries, extension order, GPL/history and original
attribution are unchanged. Runtime code remains Python 3.8-compatible; no new Kodi
API is introduced beyond already-used `xbmcvfs.translatePath` (Matrix onward).
Intended targets remain Matrix 19.4, Nexus 20.5, Omega 21.3 and Piers 22 RC2;
the Toolkit's Matrix lane references 19.5 and is not exact 19.4 qualification.

## Focused evidence and limits

`tests/check_action_bar.py` executes the actual extracted GUI load/save/click and
display code and the actual Reset script with inert Kodi adapters and disposable
profiles. Covers legacy reorder/subset, labels/icons, explicit save/reload/reset,
malicious/unknown command rejection, missing/corrupt/bounded data, empty choices,
cancelled/stale indices and failure notifications/old-file preservation.
`tests/check_safety.py` retains the original unsafe-source negative controls.

Focused result: four action-bar checks pass, including an inert unsafe raw-resolver
negative control. Existing safety, command-data and Python3/old-API checks pass;
the existing metadata GUI/keymap adapter check also passes. Python 3.12 emits
existing invalid-escape SyntaxWarnings while parsing legacy GUI/source code;
these have not been suppressed or repaired in this slice.

The initial direct-worktree Nexus Toolkit report is **failed**, not a release
gate: syntax/manifest/paths pass; package/types/official-checker fail. The private
worktree basename `task17-action-bar` differs from the manifest ID; this is
input-layout evidence, **not a Toolkit/Lab defect** and not a reason to change the
product ID. The report also retains repository-wide typing diagnostics (including
initial test-harness diagnostics), metadata/assets/language errors and checker
warnings. No broad rerun or four-lane gate was performed after the focused harness
fixes. Final settled-candidate validation is deferred to a runtime-only export
rooted at `script.tvguide.fullscreen`, excluding Git/config/evidence/tests/tools/docs.

No native/Lab work: Lab394 remains DEFERRED. No deployment, launch, UI acceptance,
real profile access, runtime four-version claim, release or distribution.
