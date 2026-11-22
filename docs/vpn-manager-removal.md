# Intentional legacy VPN Manager removal (unreleased, 2026-11-21)

This removes integration, not a network configuration: `vpnapi.py`, both imports,
the GUI constructor's manager detection/API/state/settings block, four guarded
GUI switching/default statements, the scheduled-play VPN-only block, and the
entire VPN settings category (only IDs `vpnmgr.connect` / `vpnmgr.default`).
No replacement dependency or dormant integration remains. Stale profile values
are neither read nor migrated/deleted. Manage connectivity independently through
Kodi, the OS or network tools; no VPN-security guarantee is implied.

## Preserved current behavior

Primary and selected alternate mappings, ordered fallback/retry/exhaustion,
stop/guide return, typed folder routing and malformed/action refusal remain.
Plugin, HTTP/HTTPS, local and special media remain Player data. GUI M3U/M3U8
selection retains its existing highest-BANDWIDTH parser, no-match and disabled
behavior. Scheduled playback deliberately retains the original URL verbatim:
there is no new GUI-style playlist expansion there. Preview, current Kodi Player,
PVR recording alternatives, callbacks/markers, reminders, AutoPlay producers,
scheduler ownership/cancellation and timer behavior are not redesigned.
The baseline has no named external-player branch; none is invented/restored.

## Focused evidence and limits

`tests/check_vpn_removal.py` runs actual GUI constructor/playback bodies with inert
boundaries and imports the real scheduled module against inert Kodi modules and
real in-memory SQLite. Manager installed/absent × both stale flag values covers
eight combinations. It asserts exact selected URLs, zero manager effects and
preserved retry/selection behavior. Existing typed-mapping/routing negatives and
the strict unrelated-settings/action contract remain. Private evidence includes
original-source failures, in-memory playback-loss mutants, the selected regression
batch, Python 3.8 grammar, exact source preservation audit and original Toolkit
`_types` before/after once per pinned Matrix/Nexus/Omega/Piers interpreter.

These are deterministic captures, not a full GUI import or native playback test.
No native operation, connection, manager installation, profile/settings/mapping
change or schedule creation is performed. The inherited six-stage full gate remains
**FAIL**; full validation/checker is not rerun. Matrix's validator overlay and Piers
RC2's bounded prerelease limits remain. Native acceptance awaits independent review
and a separate bounded **one Nexus OR Omega** handoff under actually available
authority; no launch workaround is authorized.

The complete manifest/version/dependencies/artwork, GPL/source notices, historical
documents/changelog and general Zomboided acknowledgments remain. Deleted vendored
code retains attribution/provenance in Git history. One common-source draft PR
targets main; after independent review, Codex normally merges then uses ordinary
nonforced fast-forwards for the four version branches, including the already
reviewed PR69/70 gap. No maintained remote branch is changed by this task.
