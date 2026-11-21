# Alpha2 guide correctness — U1

This shared-source follow-up addresses bounded guide defects associated with
refs #2, #5 and #14; it does not close those broad feature issues or establish
new native/four-version acceptance.

## Source contracts

- `TVGuide.onActionQuickEPGMode`: PLAY resolves the attached Quick programme
  before hiding the guide, then passes that exact object to the unchanged
  `playOrChoose` router. A stale/initially absent OSD programme is not the
  selection. Without an associated programme it neither hides nor plays. Existing
  focus-repair behavior remains: a recovered focus requires another action.
  Channel placeholders remain playable, including those without date fields.
  Context, channel listing and Back retain their existing routes.
- `_quickUp` / `_quickMoveUp`: wrapping above the first channel selects the
  final three-channel page: six channels start at 3, nine at 6. Partial, single
  and empty pages retain valid starts. Arrow, page and wheel routes still use
  the existing focus geometry (`Control.getPosition`) and redraw callbacks.
  `Database._getQuickEPGView` is unchanged; tests exercise its actual normalization
  and slicing rather than substituting an imagined paging implementation.
- `setControlLabel`: explicit `''` clears an existing control; `None` and missing
  optional controls remain ignored. Actual `onFocus` transitions clear main
  subtitle/time/day and Quick time labels while preserving nonempty/Unicode text.
- `onFocus`: retain `focusedProgram` **after** resolving the Quick association.
  `lookupMetadata` consequently receives the selected Quick title, not a fallback
  to current playback. Its empty-title, cancellation and existing main-guide
  behavior are preserved; the metadata adapter itself is unchanged.

## Deferred candidate

`onClick(C_QUICK_EPG_BUTTON_LEFT)` uses a different edge/finder pair from the
keyboard `_quickLeft` boundary. However, none of the bundled Default, Dark or
CatBar `script-tvguide-main.xml` files declares that button (ID 17027).
No accessible bundled control was established, so that handler is deliberately
unchanged. Custom-skin accessibility and any later repair require separate
evidence; no skin redesign is included.

## Bounded verification

Run `python -B tests/check_quick_guide.py -v`. The fixture extracts only selected
actual GUI/DB AST methods, uses fresh control wrappers and inert native/RPC
adapters, and imports neither Kodi/stubs nor startup entry points. It covers
distinct stale/selected/absent programmes, absent focus/items, focus repair,
dateless placeholders, 0–9 channels, ordinary main focus, optional labels and
actual metadata adapter positive/empty/cancel decisions. Scoped in-memory
negative controls detect restoration of each defect and reject hiding before
selection or adding a date requirement. No entire unrelated file is frozen.

Focused GUI/control/empty-list/popup/metadata/safety regressions and Python 3.8
grammar/diff checks accompany this change. Existing invalid-escape diagnostics
remain. The full six-stage static gate, dependency installation, native startup,
deployment, playback/timer campaigns and packaging were **not performed** for
this source-only batch. Historical Alpha qualification and feature inventory
remain historical; no manifest/version/release change follows.
