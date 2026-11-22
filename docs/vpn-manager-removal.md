# Intentional legacy VPN Manager removal (unreleased, 2026-11-21)

This removes integration, not a network configuration: `vpnapi.py`, both imports,
the GUI constructor's manager detection/API/state/settings block, four guarded
GUI switching/default statements, the scheduled-play VPN-only block, and the
entire VPN settings category (only IDs `vpnmgr.connect` / `vpnmgr.default`).
No replacement dependency or dormant integration remains. Stale profile values
are neither read nor migrated/deleted. Users requiring a VPN must manage it
independently through Kodi, the OS or network tools; no VPN-security guarantee is implied.

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

Final focused result: **18 scripts pass, 108 unittest methods plus four assertion
scripts; 17/17 negative controls detected**, zero negative harness errors. Initial
timeout/import-harness failures and their bounded corrections remain in private
evidence. Fresh type impact is **609→605** for Matrix/Nexus/Omega and **582→578** for
Piers, removing only four VPN findings per lane with no added normalized findings.
All mypy exits remain 1. The inherited six-stage full gate remains **FAIL**;
full validation/checker was not rerun. Matrix's validator overlay and Piers RC2's
bounded prerelease limits remain. This docs-only follow-up reruns no product checks.

## One bounded Nexus native round — ended before launch

The accepted implementation `d9c27c1` was captured as GEN13, structurally validated
and successfully deployed. The 322-file native payload comprises the prior 322
runtime paths minus `vpnapi.py`, plus this authorized developer note; all shared
hashes match Git. The unchanged viewer showed **Kodi Home only**, not the guide.
A prelaunch `tvguide_lab_log_scan` returned **`invalid_params`** without log evidence;
the no-refusal-retry rule was applied conservatively and testing stopped. No
manifest launch was submitted. This was neither `launch_not_deployed` nor an
add-on launch failure. Deployment is not evidence of fresh GUI execution.

Guide launch, playback/ordinary media Stop, plugin and alternative-player behavior
and fresh native manager non-action remain **unobserved**. Supported lifecycle Stop
completed; independent administrator status confirms all four originals stopped,
no pending requests/actions/operations, original Current Nexus selection46/binding
unchanged and viewer stopped. No settings/mappings/schedules or network/VPN changes
were requested. Stopped-profile archive comparison is still pending: no byte-exact
Nexus preservation claim is made, and destination-only files may remain after
deployment. Deterministic tests are not full GUI-import/native playback acceptance.
No second round or launch workaround is authorized by this documentation update.

The complete manifest/version/dependencies/artwork, GPL/source notices, historical
documents/changelog and general Zomboided acknowledgments remain. Deleted vendored
code retains attribution/provenance in Git history. Draft PR creation remains
blocked by two retained GitHub permission denials; no PR exists. The proposed
common-source PR targets main; after independent review, Codex normally merges then uses ordinary
nonforced fast-forwards for the four version branches, including the already
reviewed PR69/70 gap. Main and all four version branches remain unchanged; they
are not yet aligned. Issue21 remains open. No maintained remote branch is changed
by this task, and no release/version/licensing change is made.
