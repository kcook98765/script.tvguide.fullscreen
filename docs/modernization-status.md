# Current fork feature and qualification status

This is the authoritative current overview. The reviewed Alpha source batch
([#44](https://github.com/kcook98765/script.tvguide.fullscreen/pull/44),
[#46](https://github.com/kcook98765/script.tvguide.fullscreen/pull/46),
[#48](https://github.com/kcook98765/script.tvguide.fullscreen/pull/48),
[#50](https://github.com/kcook98765/script.tvguide.fullscreen/pull/50),
[#52](https://github.com/kcook98765/script.tvguide.fullscreen/pull/52)) is merged.
Reviewed implementation checkout:
[`ca198d4ffc498f23ffdfae59d815d84177b10f1f`](https://github.com/kcook98765/script.tvguide.fullscreen/commit/ca198d4ffc498f23ffdfae59d815d84177b10f1f).
That is a reviewed source baseline, **not** a frozen or newly qualified payload.
This documentation/changelog update precedes runtime freeze; **no final frozen
payload identity or new consolidated qualification result is recorded yet**.
Overall acceptance: [#1][overall]; preservation: [#14][preservation];
dependencies/settings: [#3][dependencies]. No release or full legacy parity is claimed.

## Qualification

**New consolidated native round: PENDING. New four-lane static gate: PENDING.**
Focused source regressions pass, but do not substitute for these checks. Older
full-addon static failures remain unresolved evidence, not an assumed current pass.

Earlier blanket “all native BLOCKED/UNRUN” statements are superseded. The
[Lab394 activation blocker][lab394] is no longer the current blocker: deployed
Lab revision `3d1d459`, schema `0017`, was independently live-verified healthy.
That infrastructure observation does not qualify this add-on or authorize a new
runtime action. Mixed Program+service execution must still be observed, not
inferred from structural validation, enabled state or launch acknowledgement.

| Intended target | Historical native evidence and exceptions | New consolidated native | New full static gate |
| --- | --- | --- | --- |
| Matrix **19.4** ([#8][n8]) | Fixture XMLTV/guide, mapped playback/Stop and bounded background/timer evidence. Ordinary reopen had an unexplained native exit; separate historical SIGSEGV evidence is retained in **#8 (deferred)**, without a shared causal diagnosis. Recovery did not erase either observation. | **PENDING**; historical result remains partial | **PENDING**, using static **19.5**, not native 19.4 proof |
| Nexus **20.5** ([#9][n9]) | Core fixture/background/timer/player evidence plus later guide/control, M3U retention and empty-list corrections; exact source scopes below. | **PENDING** | **PENDING** |
| Omega **21.3** ([#10][n10]) | Core fixture/background/timer evidence; later optional-popup and source-aware XMLTV cache checks. Post-restart NOW reminder was **unobserved**, not diagnosed as failed. | **PENDING** | **PENDING** |
| Piers **22 RC2** ([#11][n11]) | Seven core fixture criteria passed on the exact Linux preview build below. Separate rapid-modal blank popup remains unexplained; no proven shared cause with Omega. | **PENDING**; bounded preview only | **PENDING**, bounded RC2 stub/checker limits |

### Historical native provenance and limits

These are supervisor-independently-reviewed historical observations, not a new
run or a result for the merged five-fix Alpha batch:

- Native source **`1e7e5a1`** has actual fixture XMLTV/guide/mapped playback/Stop
  and background/timer evidence across all four targets, with the table's
  exceptions. Nexus reuses **`465cc55`** timer/background/player evidence and
  **`21d01fd`** GUI correction/native evidence; its `1e7e5a1` follow-up establishes
  **M3U/rule retention only**, not a fresh repeat of all prior criteria.
- Piers was **22 RC2 / build 21.90.902 / Git 20261109-d686683a-dirty**, Linux.
  Seven fixture criteria passed there, not on every Piers build or platform.
- [PR32](https://github.com/kcook98765/script.tvguide.fullscreen/pull/32) repairs
  Nexus guide labels/details and programme actions using native control IDs;
  [PR34](https://github.com/kcook98765/script.tvguide.fullscreen/pull/34) preserves
  cached programmes/schedules during source-scoped additive M3U channel updates.
- [PR36](https://github.com/kcook98765/script.tvguide.fullscreen/pull/36) has
  original **Omega generation 4** optional-popup native evidence: two popups,
  Watch, an advancing fixture clip, Stop, populated saved-rule context and reopen.
  This does not establish the cause of Piers' separate blank modal.
  [PR38](https://github.com/kcook98765/script.tvguide.fullscreen/pull/38) has
  **Omega** source-aware XMLTV cache native evidence.
- [PR40](https://github.com/kcook98765/script.tvguide.fullscreen/pull/40) and
  [PR42](https://github.com/kcook98765/script.tvguide.fullscreen/pull/42) have exact
  combined **Nexus generation 6** no-match/empty-list arrow native evidence.
  At pre-Alpha source **`95c0310`**, **246/246 real-feed channel IDs mapped**;
  sampled guide/navigation/cache/settings and playback dispatch/Stop were checked.
  This is **not sustained playback progression or audio acceptance**. Private
  feed contents, endpoints, titles, settings, screenshots and raw logs are not
  redistributed here.

Reminder/AutoPlay timer/background observations are partial functional evidence,
not acceptance of all recurrence/restart/cancellation phases or proof of a PVR
backend recording. Japanese/emoji glyph boxes and environmental audio/control
log diagnostics remain recorded. There is no clean-log, complete audio,
all-platform or full four-version compatibility claim.

### Historical full static gate — exact Task22 source, not the current gate

Task22 validated **`84b171b15562609d1af0db30c6059af21d71e763`**,
tree `0eda7048376fac5e5965fc5e62f26eb739f1ad2f`. Its 17 focused scripts exited 0
(100 unittest cases plus four assertion scripts). On every lane syntax,
manifest, paths and package **passed**; types and official checker **failed**:

| Historical static lane | Type errors | Official checker errors / warnings | CLI / JSON exit |
| --- | --- | --- | --- |
| Matrix **19.5** | **643** | **3 / 9** | **1 / 1** |
| Nexus **20.5** | **643** | **3 / 10** | **1 / 1** |
| Omega **21.3** | **643** | **3 / 10** | **1 / 1** |
| Piers **22 RC2** | **617** | **3 / 10** | **1 / 1** |

The three checker errors concern retained `Georgian`, `Haitian (Haitian Creole)`
and `Vietnamese (Viet Nam)` directories. Preserve **69 catalogs / 2,492 entries**;
Georgian/Haitian identities and a conflicting Vietnamese variant need explicit
owner/translator decisions, not deletion or guessed mappings. See
[language limits](package-metadata.md#localization-evidence-and-unresolved-variants).
Typing is unresolved, **not all false positives**. The optional-Database
`playOrChoose` diagnostic is static uncertainty, not a proven new runtime defect.
Only the logo optional-index diagnostic changed in that historical comparison;
normalized checker diagnostics were unchanged. Warnings/negative controls remain.

Historical preservation proof covered **912 runtime files / 4,888,353 bytes**,
aggregate SHA-256 `4883108c5ffea0c1e9199088e86c1bd808e02de1f5ff1101262d29e61a429edd`.
The private Task22 `logo-followup-84b171b` receipts retain the six stages, hashes,
comparisons and limits. They do **not** validate later changed bytes. The old
generation-0 structural receipt for `78bac49` is likewise not current acceptance.
[Toolkit31](https://github.com/kcook98765/kodi-agent-toolkit/issues/31) and
[Toolkit32](https://github.com/kcook98765/kodi-agent-toolkit/issues/32) are historical
tooling context, not blanket explanations for typing failures. Piers remains an
exact-RC2 preview/static comparison, not complete API or platform qualification.

## Feature inventory

| Feature | Current state / evidence boundary | Focused guide |
| --- | --- | --- |
| Fullscreen/quick XMLTV EPG, mappings, lists/search, channel navigation and ordinary playback | Core paths have **bounded historical native evidence** above. Latest Alpha fixes need consolidated native checks. OSD/PiP/next-up and latent VOD are not fully accepted. | [Fixtures](native-fixtures.md); [GUI/API assessment][gui-audit] |
| XMLTV sources, offsets, logos and cache | Reviewed independent-offset, explicit bool opt-in and URL-logo restorations; source-aware cache repair has historical Omega evidence. URL construction is not image reachability/rendering proof. | [Offsets](xmltv-source-offsets.md); [settings/logo notes](dependencies-settings.md#alpha-a2-xmltv-logo-opt-in) |
| Internal title/synopsis/category/channel search and saved searches | Empty-result/list navigation has historical Nexus evidence. New title-only date window and source-scoped listing/catchup regressions pass; native pending. LIKE wildcards/cross-channel search remain intentional. | [Alpha repairs below](#reviewed-alpha-source-repairs); [fixtures](native-fixtures.md) |
| Reminders and ordinary AutoPlay | Safe text/data, source/channel event ownership and reconstruction retained; historical timer/background evidence is partial, not every phase. Old collisions, unclicked recurrence horizons and in-flight delivery/playback limits remain deferred. | [Reminders](modernization-reminders.md), [AutoPlay](autoplay-data.md), [ownership](schedule-ownership.md) |
| Recording / legacy external AutoPlayWith | **Partial PVR replacement**: existing capable backend/client required; no arbitrary-stream/FFmpeg capture, full old recurrence/padding/markers or legacy-row migration. | [PVR prerequisites/limits](recording-pvr.md) |
| External-player choice | **Provisionally disabled** pending platform/configuration/receiver/stop qualification; source presence/JSON is not safe execution proof. | [Research][external-audit] |
| Default/Dark/CatBar and custom appearance | Bundles retained; **partial passive layout/PNG customization**. Complex includes/resources and WMC/WhiteSnow compatibility unresolved. | [Passive skin subset](custom-guide-skins.md) |
| ExtendedInfo / MySearch / iSearch external lookup | **Optional TMDbHelper movie/TV handoff**, requiring an installed/enabled compatible official provider and its setup; not full legacy lookup, episode/ID matching or guide metadata injection. Provider results/return still need feature acceptance. | [Metadata lookup](metadata-search.md) |
| Artwork and image matches | Bounded JSON persistence replaces pickle, **without migration**. Last-writer-wins/interprocess and legacy lookup-service health limits remain; blank-logo PNG repair retained. | [Image cache](image-match-cache.md); [PR30](https://github.com/kcook98765/script.tvguide.fullscreen/pull/30) |
| Media/plugin mappings, alternates, ini/M3U/TSV/subscriptions and catchup | Ordinary paths retained; **partial typed stream/folder dispatch**. `@` RunPlugin-equivalent actions remain blocked; scheduled AutoPlay is media-only. Receiver/provider and catchup parity unqualified. | [Mapping contract](typed-playback-mappings.md) |
| Key editor and action bar/MINE | Key editor retained; **closed action catalog** supports hide/order/label/image, not arbitrary builtins, MINE templates or downloaded Python. | [Action bar](action-bar.md) |
| Settings, providers, logos/backgrounds, VPN and backup/import/export/reset | Source retained with bounded settings/cache repairs and sampled historical settings evidence; not universal provider health or persistence acceptance. TLS verification retained; no secret logging/downloaded-code restoration. | [Dependencies/settings](dependencies-settings.md) |
| Background updates/autostart | Both original script/service responsibilities retained; historical startup/background work exists with per-lane limits. Recovery/race/restart acceptance remains incomplete. | [Service safety](service-safety.md) |
| Package/artwork/translations | Manifest **0.0.445**, Program+service, GPL/upstream credits, assets and **69 catalogs / 2,492 entries** preserved. Three locale identity/variant problems unresolved. | [Package notes](package-metadata.md) |
| Permanent removals | Only downloaded-code/arbitrary-command mechanisms are approved removed. Other feature gaps remain restoration work or require an owner decision. | [Safety](modernization-safety.md); [preservation #14][preservation] |

### Reviewed Alpha source repairs

All five PRs were independently accepted and normally merged. These are focused
source results, **not new native results**; no new optional integration was needed
or installed for them:

- **#44:** secondary-only/tertiary-only XMLTV offsets; original 18 failing
  subtests → four methods / 128 scenarios pass (cache 13 and fixtures four pass).
- **#46:** `'false'` no longer enables XMLTV icons; seven original failing
  subtests → five parser methods pass.
- **#48:** explicit URL logo source now uses its already constructed URL;
  20 original failing subtests → six parser methods pass; title/path spelling,
  folder/XMLTV and TheLogoDB precedence retained.
- **#50:** title-only search uses the existing synopsis/title containment window;
  four original failures → seven tests pass, retaining wildcard/source/channel/
  metadata behavior.
- **#52:** channel/catchup listings filter by active source; four original
  failures → five tests pass, preserving their distinct strict-overlap predicates,
  independent windows, metadata and same-source result sequence.

The bounded adjacent review established no further small empty-selection or
scheduler #21 defect. Deferred scheduler limitations are not a request for a new
framework. The [changelog](../changelog.txt) includes the pre-freeze Alpha work;
later native/status follow-up is restricted to README/docs, not another changelog
or runtime change. Final qualification must identify the actual frozen payload
and separately establish GUI, playback/Stop, settings and functional service work.

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
