# Current fork feature and qualification status

Settled runtime source: **`84b171b15562609d1af0db30c6059af21d71e763`**,
tree `0eda7048376fac5e5965fc5e62f26eb739f1ad2f`. The focused runtime work and
blank-logo repair are merged. **Source presence/review is not native acceptance
or full legacy parity.** Overall acceptance: [#1][overall]; preservation and original research:
[#14][preservation]; dependencies/settings: [#3][dependencies]. Older focused
docs retain review-time evidence; this table describes the current merged source.

## Feature inventory

| Feature | Current classification | Boundary / focused guide |
| --- | --- | --- |
| Fullscreen/quick EPG, XMLTV/offsets, channel/category/order/number navigation, lists/now/next, OSD/PiP/next-up, ordinary playback | **Retained, unverified natively** | [Local XMLTV/M3U/video fixtures](native-fixtures.md). Latent VOD callback is not working-VOD evidence ([GUI/API assessment][gui-audit]). |
| Internal title/synopsis/category/channel search, saved searches, favourites/library shortcuts | **Retained, unverified natively** | Internal search remains separate from external lookup; third-party favourites require compatible installed receivers. |
| Reminders / ordinary AutoPlay, recurrence, add/remove/clear, before/after, optional stop and reconstruction | **Retained through safe data replacements** | Punctuation/Unicode, five-minute/start reminder phases, 10000ms/sound-on semantics and scoped event identities retained. [Reminders](modernization-reminders.md), [AutoPlay](autoplay-data.md), [ownership/legacy limits](schedule-ownership.md): old collisions, recurrence horizons, claim/crash and in-flight cancellation limits remain. |
| Recording / legacy external AutoPlayWith | **Partially replaced**; other legacy modes **temporarily disabled** | [PVR recording/timers](recording-pvr.md) need an existing capable backend. Not arbitrary-M3U/plugin or FFmpeg capture, external AutoPlayWith, full old recurrence/padding/markers or legacy-row migration. |
| Optional external-player choice | **Temporarily disabled/provisional** | [External-player research][external-audit]: platform/configuration/receiver/stop qualification pending. Registered-player selection and JSON do not establish shell safety or playback. |
| Bundled Default/Dark/CatBar; local/profile appearance | Bundles **retained**; customization **partially replaced** | [Opt-in passive layout/PNG subset](custom-guide-skins.md), not arbitrary executable themes. Complex layouts/includes/resources and WMC/WhiteSnow compatibility remain unresolved. |
| ExtendedInfo / MySearch/iSearch cross-add-on lookup | **Partially replaced** | [Optional TMDbHelper movie/TV lookup](metadata-search.md), not all ExtendedInfo/search, arbitrary provider templates, year/episode/ID mapping or guide plot/art injection. Provider availability, quote normalization and native results/return remain limits. |
| Artwork, delete-image suppression, persistent image matches | Art paths **retained/unverified**; persistence **replaced, partial** | [Bounded JSON cache](image-match-cache.md): **no pickle migration**. Legacy lookup-service health and interprocess last-writer-wins behavior remain unresolved. |
| Media/plugin mappings, alternates, ini/M3U/TSV/subscriptions, catchup/play-beginning | Ordinary paths **retained**; stream/folder dispatch **partially replaced** | [Typed playback and safe video/Programs folders](typed-playback-mappings.md) are not RunPlugin-equivalent **`@` actions**, which remain temporarily blocked. Scheduled AutoPlay is media-only; receiver/catchup contracts still need native acceptance. |
| Key editor, bundled actions, custom action bar/MINE | Key editor **retained**; action customization **partially replaced** | [Closed action catalog](action-bar.md) supports hide/order/label/image choices, not arbitrary custom commands or MINE execution. |
| Providers, settings, logos/backgrounds, VPN, backup/import/export/reset | **Retained, unverified natively** | [Dependencies/defaults](dependencies-settings.md) are source/catalog evidence, not installation/provider/persistence acceptance. [Blank-logo PNG repair (#30)](https://github.com/kcook98765/script.tvguide.fullscreen/pull/30): four actual-Pillow cases pass; ordinary/white-background pixels unchanged. TLS verification remains; no secret logging or downloaded Python restoration. |
| Background updates, autostart, reminder/AutoPlay reconstruction | Both script/service declarations and functions **retained** | [Startup safety and saved scheduling](service-safety.md) repaired; stale-marker, database/recovery and race limits remain. Enabled state or startup markers alone do not prove background work. |
| Package metadata, artwork declarations, translations | **Retained with bounded modernization** | [Package/language notes](package-metadata.md): **69 catalogs / 2,492 entries** preserved; three legacy language identities/variants remain unresolved. Not distribution or checker acceptance. |
| Proposed permanent feature removals | **None** | Only downloaded-code/arbitrary-command mechanisms are approved removed. All other gaps above remain restoration/acceptance work or require an explicit owner decision. |

## Qualification

**Full validation: FAIL on all four lanes; source readiness: PARTIAL.** Task22
completed the gate on exact `84b171b`: **all 17 focused scripts exited 0**
(100 unittest cases plus 4 assertion scripts). Each lane **PASSED syntax,
manifest, paths and package**, but failed types and official checker.

| Intended native target | Types | Official checker | CLI / JSON exit | Native acceptance |
| --- | --- | --- | --- | --- |
| Matrix **19.4** ([#8][n8]) | **FAIL**, 643 errors | **FAIL**, 3 errors / 9 warnings | **1 / 1** | **BLOCKED/UNRUN** — deferred [Lab394][lab394] |
| Nexus **20.5** ([#9][n9]) | **FAIL**, 643 errors | **FAIL**, 3 errors / 10 warnings | **1 / 1** | **BLOCKED/UNRUN** — deferred [Lab394][lab394] |
| Omega **21.3** ([#10][n10]) | **FAIL**, 643 errors | **FAIL**, 3 errors / 10 warnings | **1 / 1** | **BLOCKED/UNRUN** — deferred [Lab394][lab394] |
| Piers **22 RC2** ([#11][n11]) | **FAIL**, 617 errors | **FAIL**, 3 errors / 10 warnings | **1 / 1** | **BLOCKED/UNRUN** — deferred [Lab394][lab394] |

The checker errors on every lane concern the retained `Georgian`, `Haitian
(Haitian Creole)` and `Vietnamese (Viet Nam)` locale directories; see
[language identity/variant limits](package-metadata.md#localization-evidence-and-unresolved-variants).
Typing remains unresolved, **not all false positives**. `gui.py`'s `playOrChoose`
optional-Database `getStreamUrl` access remains static uncertainty, not a proven
new runtime failure. Only the logo optional-index diagnostic was removed per lane;
no normalized type diagnostics were added and checker diagnostics are unchanged.
All warnings/negative controls remain preserved, including focused stderr; table
warning counts are the official checker's.
Matrix's static lane is **19.5**, not native19.4 proof; Piers remains bounded RC2
prerelease/static coverage, not all-platform or all-runtime correctness.

After the run, the supervisor independently verified **912 runtime files /
4,888,353 bytes**, exact Git blobs/modes and aggregate SHA-256
`4883108c5ffea0c1e9199088e86c1bd808e02de1f5ff1101262d29e61a429edd`.
Only `ResizeLogos.py` differs from the prior runtime; all modes and 911 other
files match. Task22's private receipt bundle is
`.git/modernization-evidence/task22-final-qualification/logo-followup-84b171b/`:
`gate-summary.json`, `comparison-to-5e83.json`, `bounded-classification.json`
and `receipt-index.json` locate results, limits and hashed raw evidence;
`runtime-inventory.json` defines the aggregate algorithm. Original gate receipts
remain historical. Applicability to later docs-only main requires **independent
payload-equality verification**; no validation was rerun for these docs.

[Toolkit31](https://github.com/kcook98765/kodi-agent-toolkit/issues/31)
(`start="login"` path classification) and
[Toolkit32](https://github.com/kcook98765/kodi-agent-toolkit/issues/32)
(Matrix `getPosition` stub false positive) are separate from Lab394; no source
workaround or blanket typing acceptance is implied.

Frozen Lab **generation 0** structural validation applies only to **`78bac49`**,
not this source, deployment or native behavior. Lab394 concerns qualified,
consented full-manifest cold activation, not proof Kodi cannot run script+service;
fixed-video smoke ineligibility is not whole-add-on failure. No native retry or
workaround is authorized while deferred.

After deferred Lab394 is resolved, resume acceptance sequentially **Matrix →
Nexus → Omega → Piers**: dependencies/install/consented full-manifest activation →
`development_launch` **ordinal 0** → independently verified background updates
and reminder/AutoPlay reconstruction and actual work → XMLTV/guide navigation,
playback/settings persistence → clean stop and bounded logs. Enabled state or
launch dispatch alone is not acceptance. Preserve both original `addon.py` and
`service.py` declarations/functions, GPL/upstream credits and history throughout.
No native, release or distribution qualification is claimed.

[overall]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/1
[preservation]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/14
[dependencies]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/3
[external-audit]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/14#issuecomment-7025774995
[gui-audit]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/14#issuecomment-7026036379
[lab394]: https://github.com/kcook98765/kodi-lab/issues/394
[n8]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/8
[n9]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/9
[n10]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/10
[n11]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/11
