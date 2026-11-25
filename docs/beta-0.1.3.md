# TV Guide Fullscreen 0.1.3 Beta — prepared release notes

**Pending owner review, versioned-package qualification and publication.** These
notes can also serve as prerelease notes. They do not announce a published 0.1.3
installer. Use the [README installation routes](../README.md#installation) for
published **0.1.2 Beta** until the owner publishes an approved successor.
Planned distribution is **Nexus 20.x / Omega 21.x**. Matrix keeps its **0.1.1**
catalog; Piers preview is outside publication. No 0.1.3 asset links are advertised.

## Expected improvements

1. **Reliable same-path XMLTV refresh.** Reopening the guide or its supported
   background update detects changed local content even with unchanged or older
   timestamps. This is not a filesystem watcher or navigation-time provider poll.
   Rejected replacements retain last-good data within the
   [documented cache/import limits](xmltv-local-refresh.md).
2. **Retained guide configuration.** Supported refreshes preserve settings,
   saved channel weights/order and visibility, categories, manual/alternative
   stream mappings and reminder/AutoPlay rules. No guide reset is required.
3. **Subtitle search.** Programme search includes XMLTV subtitles as well as
   titles; optional plot search remains controlled by its existing setting.
4. **Strict category-scoped search.** Programme search respects the active
   category, channel visibility and configured listing window. An empty category
   does not silently broaden the search to every channel.
5. **Kodi native Favorites and return.** Version-aware native Favorites routing
   restores navigation and return to the guide. Optional third-party Favorites
   providers still need their own compatible installation/setup; none is added.
6. **Category mouse interaction and membership order.** Category controls accept
   mouse interaction again; membership changes and startup preserve member order.

On genuinely fresh profiles, channels follow **XMLTV declaration order unless
explicit M3U ordering is enabled**, when playlist order wins. Existing profiles'
saved weights and visibility are preserved, not retroactively reordered. See
[initial ordering](xmltv-initial-order.md). The 0.1.2 Stream Setup tab fixes remain.

## Same-ID backup and upgrade

Back up the **Kodi profile, TV Guide settings, channel/stream mappings and saved
reminder/AutoPlay rules** before updating; prefer a separate test profile. Keep
`script.tvguide.fullscreen` and use the normal in-place upgrade. Do not uninstall
with data removal, delete the guide database or use Reset Database as an upgrade
step. Keep Kodi's official repository enabled and let Kodi resolve the unchanged
[six mandatory dependency floors](../README.md#required-dependencies); no modules
are bundled and dependency failures should not be bypassed. Other fork IDs and
older migrations need separate checks.

Wait for owner publication and its verified installer/checksum or catalog update.
The current README repository/direct ZIP links intentionally remain **0.1.2**.
Actual versioned **0.1.3 ZIP install/upgrade has not yet been qualified**; a
separate authorized native step must supply that evidence.

## Qualification

The following is supplied premerge evidence for the **integrated private package
still numbered 0.1.2**, not a native run performed for these notes. This release
preparation changes only manifest version/news, changelog and documentation;
the exact integrated runtime is unchanged.

| Kodi | Bounded integrated-runtime evidence |
| --- | --- |
| Nexus 20.5 | Passed native in-place upgrade from the actual published Beta and same-path nanosecond-mtime refresh. All **1,888** real programmes and **246** matched channels were retained, as were configured data/order/visibility/maps and preexisting category order; **36** additional normal generated aliases only. The integrated candidate stopped cleanly. The published Beta had one preexisting shutdown hang on this runtime, recovered without profile/data loss. |
| Omega 21.3 | Passed actual integrated-package installation and rendered guide. Startup service refreshed changed content at unchanged filename/mtime **before any foreground launch**; all **1,888** raw rows and **246** mapped IDs were checked. Settings were unchanged except the expected last-background-update timestamp. |
| Piers 22.0 RC2 preview | Exact integrated runtime installed with **ten verified dependencies**; guide started and live view was available. All **1,888** raw rows and **246** mappings/cache were checked. The targeted new GUI probe stayed at placeholder focus. Earlier scoped rendered-guide/Favorites evidence remains separate. This is **forward smoke only**, not publication qualification. |
| Matrix 19.4 | **Blocked** by the prior native startup signal, tracked in [#82](https://github.com/kcook98765/script.tvguide.fullscreen/issues/82). No Matrix launch in this campaign. Matrix is not a Nexus/Omega release gate; its catalog stays on 0.1.1. |

Separate clean isolated Omega actual tests with captured full data confirmed
historical XMLTV order with explicit M3U ordering **off** for both published and
candidate builds, playlist order **on**, repeated opens preserving state, and
graceful Stop/release. Earlier exact feature-path evidence includes modern
Favorites/Back, Stream Setup Browse/Addons/Favorites, owned/authorized
preview/playback/Stop and mappings. These are not claims that every action was
repeated in the latest integration run or that all settings combinations passed.

The final premerge suite reported **331 tests, one existing conditional skip**.
The skipped upstream Favorites identifiers test passed independently using exact
native-tag source copies. [#93](https://github.com/kcook98765/script.tvguide.fullscreen/issues/93)
is resolved by focused test-only [PR #94](https://github.com/kcook98765/script.tvguide.fullscreen/pull/94).
Inherited static typing/locale issues remain, with structural checks passing and
no new diagnoses in the supplied comparison; this is not a clean full static gate.
Audio quality and actual timer firing remain outside measurement.

## Open reports and limits

[#86](https://github.com/kcook98765/script.tvguide.fullscreen/issues/86) **stays
open for the reporter's ordinary title misses**. Subtitle/category regressions
do not prove those misses fixed, and earlier reports are not all resolved.
For follow-up, provide minimal **redacted XMLTV channel/programme rows**, the
**exact query**, active **category**, listing **window**, channel **visibility**,
relevant search/source **settings** and **Kodi version**. Preserve the
query-to-row relationship while redacting. Do not upload raw settings/databases,
credentials, endpoints, private stream links, unredacted logs or private captures.

Other inherited Beta limits remain: non-clean logs, optional integrations,
third-party skins/players, provider/catchup and legacy recording parity, scheduler
edge cases, and the possible original playback-error dialog during fallback.
No broad all-platform, audio, scheduler-firing or full legacy-parity claim follows.

The same add-on ID, all six mandatory dependency floors, Program and background
service entry points, maintained metadata, exact artwork, original GPL notices
and author/upstream credit remain. See [technical release history](release-history.md),
[artwork provenance](artwork-provenance.md) and the [changelog](../changelog.txt).
