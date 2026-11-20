# Current fork feature and qualification status

Settled runtime source: **`5e83b888e3b82dd621da6b1576f6daea0d06747c`**,
tree `432a21d9f1ef4a99be782492880b678a5dbf8e55`. All focused runtime PRs through
#28 are merged. **Source presence/review is not native acceptance or full legacy
parity.** Overall acceptance: [#1][overall]; preservation and original research:
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
| Providers, settings, logos/backgrounds, VPN, backup/import/export/reset | **Retained, unverified natively** | [Dependencies/defaults](dependencies-settings.md) establish source/catalog availability, not installation, provider/network or settings persistence. TLS verification remains; no secret logging or downloaded Python restoration. |
| Background updates, autostart, reminder/AutoPlay reconstruction | Both script/service declarations and functions **retained** | [Startup safety and saved scheduling](service-safety.md) repaired; stale-marker, database/recovery and race limits remain. Enabled state or startup markers alone do not prove background work. |
| Package metadata, artwork declarations, translations | **Retained with bounded modernization** | [Package/language notes](package-metadata.md): **69 catalogs / 2,492 entries** preserved; three legacy language identities/variants remain unresolved. Not distribution or checker acceptance. |
| Proposed permanent feature removals | **None** | Only downloaded-code/arbitrary-command mechanisms are approved removed. All other gaps above remain restoration/acceptance work or require an explicit owner decision. |

## Qualification

**Task22's final non-native four-lane gate is IN PROGRESS** on exact runtime
baseline `5e83b888e3b82dd621da6b1576f6daea0d06747c`. Final receipts are pending;
no pass/failure cells or counts are inferred from earlier candidate reports.

| Intended native target | Final non-native gate (Task22) | Native acceptance |
| --- | --- | --- |
| Matrix **19.4** ([#8][n8]) | **IN PROGRESS**; static lane **19.5** is not native19.4 proof | **BLOCKED/UNRUN** — deferred [Lab394][lab394] |
| Nexus **20.5** ([#9][n9]) | **IN PROGRESS** | **BLOCKED/UNRUN** — deferred [Lab394][lab394] |
| Omega **21.3** ([#10][n10]) | **IN PROGRESS** | **BLOCKED/UNRUN** — deferred [Lab394][lab394] |
| Piers **22 RC2** ([#11][n11]) | **IN PROGRESS**; bounded prerelease/static coverage | **BLOCKED/UNRUN** — deferred [Lab394][lab394] |

Historical broad typing/checker failures, all six stages, warnings and negative
controls remain evidence for their exact inputs, not current-source success.
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

Future separately authorized acceptance remains sequential **Matrix → Nexus →
Omega → Piers**: dependencies/install/consented full-manifest activation →
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
