# Favorites navigation — #87

Later scoped native evidence and the independently passed exact-tag identifier
check are summarized in [0.1.3 qualification](beta-0.1.3.md#qualification).
The source handoff below remains historical, not a claim that every route or
provider was natively exercised; versioned-package acceptance is still pending.

## Compatibility correction

The campaign supplied official exact-tag `WindowIDs.h` / `WindowTranslator.cpp`
copies. Their native Favorites identifiers are:

| Kodi | Verified definitions/names | Selected route |
| --- | --- | --- |
| Matrix 19.4 (`e12e66e0`) | dialog `10134`, `favourites`; no browser | Existing `ActivateWindow(10134)` |
| Nexus 20.5 (`4b95737e`) | dialog `10134` and browser `10060`, both names | Existing `ActivateWindow(10134)` |
| Omega 21.3 (`a3a448d2`) | browser `10060`, `favouritesbrowser`; no old dialog/name | `ActivateWindow(favouritesbrowser)` |
| Piers 22 RC2 (`d686683a`) | browser `10060`, `favouritesbrowser`; no old dialog/name | `ActivateWindow(favouritesbrowser)` |

The supplied Nexus/Omega/Piers `GUIWindowFavourites.cpp` also derives the browser
from `CGUIMediaWindow`. This is not the same receiver as the old dialog. Source
identifier compatibility does **not** prove native focus, return or empty-list
behavior. There are no guide close/reopen, Home, sleep or modal-stack changes.

`favourites_navigation.py` supplies only closed code-owned routes. Main button
`4316` and context button `4012` share `TVGuide.openFavourites`; the context
popup's `doModal()` still returns before dispatch. Optional Simple/Video/Super
Favourites keep their exact plugin URI, window and `return` parameter. A read-only
installed/enabled pluginsource query prevents dispatch to an unavailable provider;
failure to confirm it produces an explanation, not silent success or fallback.
No provider is installed, enabled or configured.

The action-bar `favourites` ID **intentionally remains native-only**. The original
bundled `resources/actions.json` and closed catalog specify the native shortcut,
not a provider action. The catalog's exact `ActivateWindow(10134)` legacy token
is retained for saved-row recognition; only its GUI dispatch is version-aware.
Existing IDs, labels, order, icons and files are not migrated or rewritten.

## Settings and preserved workflows

`favourites` is legacy **select with `values`**, default `Favourites`, not an
integer enum or localized `lvalues` select. The reviewed exact-release loader
research in [dependencies/settings](dependencies-settings.md#legacy-settings-retained-intentionally)
distinguishes persisted string choices from enum indices. All four existing
provider names remain valid verbatim; empty/None uses the declared native default.
Numeric-looking, unknown and command-shaped values are not executed or guessed
into providers. The runtime does not write the setting. Actual native persisted
value/default/save/restart measurement remains in the isolated acceptance campaign.

Stream Setup's independent Favorites discovery, exact-title detection,
primary/alternative link/save, typed preview and Cancel paths are unchanged.
Default/CatBar expose direct Favorites controls; Dark does not have those baseline
main/context controls but retains Stream Setup Favorites. No skin redesign.

## Deterministic verification and native handoff

Run `python3 tests/check_favourites_navigation.py` for actual-caller regression
coverage without Kodi/stubs, providers, live profiles or network. Supply
`--kodi-source-dir ../github` in the campaign to additionally verify all four
official source-copy ID/name pairs. For portable runs that optional evidence test
is explicitly skipped, not silently passed.

`--source-ref 0c4a3c3f27f5980d616e5995f5a8b37512eace49` applies candidate
expectations to the exact old production source and **fails as expected** (modern
main/context/action-bar routing, unset values and unavailable providers). Add
`--baseline` to explicitly characterize the original behavior instead; its
unavailable-provider test is skipped because the baseline has no guard.
Helper-only tests always use the current pure helper; baseline replay is of the
actual old callers, not a claim that the old source included the new helper.

Additional checks: `tests/check_action_bar.py`, `check_dependencies_settings.py`,
`check_typed_mappings.py`, `check_stream_setup_visibility.py`, `check_safety.py`,
`check_command_data.py`, `check_python3.py`, `check_popup_optional_controls.py`,
`check_custom_skins.py`, `check_control_identity.py`. All pass; the new suite with
the supplied source copies passes 11 tests. Existing invalid-escape warnings and
negative controls remain. Host grammar/caller checks do not replace version-lane
Toolkit validation; previously blocked isolated-interpreter execution remains
incomplete. Matrix's static 19.5 mapping is not exact native 19.4; Piers is RC2.

Native acceptance is separately assigned to isolated **kodi-managed-lab**:
record exact installed revision, runtime, actual setting value, current underlying
window, top dialog and focus. Test empty/populated native Favorites through
Default/CatBar main/context and CatBar action bar, by pointer and keyboard/remote;
Back must preserve guide selection/focus and existing harmless local playback.
Then select/play/Stop the [local clip](native-fixtures.md) and verify return.
Exercise only already-authorized optional providers without configuration, plus
missing/disabled states. In all three skins verify Stream Setup Favorites
discovery, preview start/stop, primary/alternative save, Cancel, reopen and mapping
retention. Require Nexus 20.5/Omega 21.3, Matrix/Piers within assigned limits;
preserve Matrix #82 startup and Piers observation failures if encountered.
No native acceptance, clean logs, audio or full compatibility is claimed here.
