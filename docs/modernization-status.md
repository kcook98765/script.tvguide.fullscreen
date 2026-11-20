# Current fork feature and qualification status

Source snapshot: reviewed main **`891151d2318f3178df61c77fa1da6482eaade2eb`**
(PR24 merge). This inventory consolidates [#1](https://github.com/kcook98765/script.tvguide.fullscreen/issues/1),
[#14's original audit and focused follow-ups](https://github.com/kcook98765/script.tvguide.fullscreen/issues/14)
and [#3](https://github.com/kcook98765/script.tvguide.fullscreen/issues/3).
**Retained means source presence, not native acceptance.** Replaced/partial means
a bounded alternative, not legacy parity; temporarily disabled means unresolved,
not owner-approved deletion. No additional permanent feature removal is approved
or proposed here. Only downloaded-code/arbitrary-command mechanisms are approved removed.

## Current feature inventory

| User-facing feature | Current classification / merged source | Remaining difference or candidate |
| --- | --- | --- |
| Fullscreen/quick EPG, XMLTV/offsets, channel/category/order/number navigation, lists/now/next, OSD/PiP/next-up, ordinary playback | **Retained, unverified**; Python3/API port [#13][p13], deterministic fixtures [#16][p16] | [Fixture guide](native-fixtures.md); rendering/navigation/playback still need native proof. Existing latent VOD `programList` callback is not evidence of working VOD or a new port regression ([Task20][gui-audit]). |
| Internal title/synopsis/category/channel search, saved searches, favourites/library shortcuts | **Retained, unverified** | Third-party favourites depend on installed receivers; internal search is distinct from external lookup. |
| Reminders and ordinary AutoPlay: rules, add/remove/clear, before/after, optional stop, service reconstruction | **Retained through replaced safe data handoffs**, merged [#15][p15], [#20][p20], [#23][p23] | Original punctuation/Unicode, reminder five-minute/start phases, 10000ms/sound-on semantics and scoped source/channel/event identities preserved in source. [Reminder](modernization-reminders.md), [AutoPlay](autoplay-data.md), [ownership](schedule-ownership.md) notes explain legacy collisions, recurrence horizons, in-flight cancellation and crash/marker limits; no native timing/sound/race guarantee. |
| Recording / legacy external AutoPlayWith | **Partially replaced** by optional backend PVR choices, [#17][p17]; remaining legacy modes **temporarily disabled** | [Real PVR channel record-now, selected broadcast once, timers/exact-ID cancel](recording-pvr.md) require an existing capable backend. Not arbitrary-M3U/plugin or FFmpeg capture, external AutoPlayWith, old recurrence/padding/markers or row migration. |
| Optional external-player choice and scheduled external AutoPlayWith | **Temporarily disabled/provisional**; [Task16 research][external-audit], source unchanged | Registered-player/JSON selection alone is not shell-safety or playback proof. POSIX `system()`, Windows configuration/argument parsing and Android receiver/return/stop qualification remain pending. No platform candidate is implemented/accepted. |
| Bundled Default/Dark/CatBar and custom guide appearance | Bundles **retained**; local/profile customization **partially replaced**, [#18][p18] | [Explicit opt-in passive layout/PNG subset](custom-guide-skins.md), not arbitrary executable themes. Complex legacy layouts/includes, hooks, resources and WMC/WhiteSnow compatibility remain unresolved, not permanently rejected. |
| ExtendedInfo details / MySearch/iSearch cross-add-on lookup | **Partially replaced**, optional TMDbHelper movie/TV lookup, [#19][p19] | [Provider-owned search/details](metadata-search.md), not full ExtendedInfo, arbitrary cross-add-on templates, year/episode/ID mapping or guide plot/art injection. Requires compatible installed/enabled provider; provider boundary-quote normalization and native return/results remain limits. |
| Programme artwork, delete-image suppression, persistent image matches | Existing XMLTV/artwork paths **retained/unverified**; persistence **replaced, partial**, [#22][p22] | [Bounded JSON cache](image-match-cache.md) restores learned/empty matches and reset. **No pickle migration**; old learned data remains untouched. Legacy remote lookup services and interprocess last-writer-wins behavior are not repaired by persistence. |
| Media/plugin mappings, alternates, ini/M3U/TSV/subscriptions, catchup/play-beginning | Ordinary paths **retained/unverified**; execution/folder forms **temporarily disabled or partial** | Draft [#28][p28] adds typed playback and safe video/Programs folder mappings; **not merged**. Safe folder navigation is not RunPlugin-equivalent `@` actions; these remain blocked. Integration must preserve the current data decoder and place the candidate's media-only guard before playback effects. |
| Key editor, bundled actions, custom action bar/MINE | Key editor/bundled actions **retained**; profile customization **temporarily constrained** | Draft [#25][p25] restores hide/order/label/image choices via a closed action catalog; **not merged**, not arbitrary custom commands/MINE execution. No new editor or raw fallback. |
| Providers, logos/backgrounds, VPN, backup/import/export/reset, settings | **Retained, unverified**; common dependency floors/legacy defaults merged [#24][p24] | [Dependency/settings evidence](dependencies-settings.md) is availability/source evidence, not provider/network/credential, binary installation or persistence acceptance. TLS verification is retained; no secret logging or downloaded Python restoration. |
| Background updates, autostart, reminder/AutoPlay reconstruction | Script **and service declarations/functions retained**, unverified | Draft [#26][p26] removes unsafe startup journal/lock deletion and repairs saved scheduling/abort handling; **not merged**. Source safety changes are not proof of actual background work. |
| Package metadata, artwork declarations, translations | Existing source retained at this pinned base; readiness **partial** | [#27][p27] preserves **69 catalogs / 2,492 entries** while improving metadata/resource IDs/icon; now merged on newer main (below), not included in this base. Earlier candidate checker result **73 → 3 errors**, warnings retained, is **not final merged-source or clean qualification**. |
| Proposed permanent feature removals | **None** | Only downloaded-code/arbitrary-command mechanisms are approved removed ([#12][p12]); all other differences above remain restoration/acceptance work or require an explicit owner decision. |

Included merges at this source snapshot: **#12, #13, #15, #16, #17, #18, #19,
#20, #22, #23, #24**. **Live-state update:** PR27 subsequently merged as
`0843fe00af052d20612d6c20d17f1d7a1963e8b2` (reviewed head `dd8a78e`);
**#25, #26 and #28 remain draft/unmerged**. This documentation branch keeps its
authorized `891151d` source base; newer main has not been reconciled or qualified
here. Draft descriptions contain focused usage/evidence links, not integrated
features. Reconcile this provisional inventory after the remaining integrations.
Task16 and Task20 are source-unchanged findings, not extra implementation PRs.

## Qualification, not a release claim

| Intended native target | Native acceptance | Current-source static qualification |
| --- | --- | --- |
| Matrix **19.4** | **BLOCKED/UNRUN** — deferred [Lab394][lab394]; [#8][n8] | Final settled gate unrun; available Matrix static lane is **19.5**, not native19.4 proof. |
| Nexus **20.5** | **BLOCKED/UNRUN** — deferred [Lab394][lab394]; [#9][n9] | Final settled gate unrun; historical broad type/checker failures remain. |
| Omega **21.3** | **BLOCKED/UNRUN** — deferred [Lab394][lab394]; [#10][n10] | Final settled gate unrun; PR27's focused checker comparison is candidate-only. |
| Piers **22 RC2** | **BLOCKED/UNRUN** — deferred [Lab394][lab394]; [#11][n11] | Final settled gate unrun; bounded prerelease/static coverage limits remain. |

Frozen workspace **generation 0** structural validation passed only for
**`78bac49be6359f4d37ab36ed45880d0d6be712dc`**. It does not qualify subsequent
main, deployment, activation or native behavior. The focused blocker is a
qualified, consented **full-manifest cold activation** path, not proof that Kodi
cannot run both extensions or that every byte-copy path fails. Historical
[Lab112](https://github.com/kcook98765/kodi-lab/issues/112#issuecomment-7023719173)
is context, not the current blocker. Fixed-video smoke ineligibility is not
whole-add-on failure. Neither service enabled state nor script dispatch alone
proves service work.

When separately resumed, test **Matrix → Nexus → Omega → Piers sequentially**:
dependencies/install and consented full-manifest activation → exact deployed
script `development_launch` **ordinal 0** → actual background updates and reminder
and AutoPlay reconstruction/delivery/work → XMLTV/guide navigation/playback/settings
persistence → clean stop and bounded logs. Preserve both `addon.py` and `service.py`
and their responsibilities throughout. This is a future acceptance sequence,
not a request to retry Lab394 now; all native stages are unperformed.

Focused source checks do not supersede the historical six-stage receipts:
syntax, manifest, paths and package passed in recorded runtime-only snapshots;
full-addon typing and official checker failed, with warnings/negative-control
diagnostics retained. Counts belong to their exact inputs, not current main.
[Python3 notes](modernization-python3.md), [fixture receipts](native-fixtures.md)
and [ownership comparison](schedule-ownership.md) retain that scope. Separate
[Toolkit31](https://github.com/kcook98765/kodi-agent-toolkit/issues/31) concerns
`start="login"` path classification;
[Toolkit32](https://github.com/kcook98765/kodi-agent-toolkit/issues/32) concerns a
Matrix `getPosition` stub false positive, not a TVGuide source defect or Lab394.
The **final settled four-lane gate is a later separate task**; no new broad
validation, native run, source freeze, release or distribution is claimed here.

[p12]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/12
[p13]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/13
[p15]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/15
[p16]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/16
[p17]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/17
[p18]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/18
[p19]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/19
[p20]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/20
[p22]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/22
[p23]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/23
[p24]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/24
[p25]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/25
[p26]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/26
[p27]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/27
[p28]: https://github.com/kcook98765/script.tvguide.fullscreen/pull/28
[external-audit]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/14#issuecomment-7025774995
[gui-audit]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/14#issuecomment-7026036379
[lab394]: https://github.com/kcook98765/kodi-lab/issues/394
[n8]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/8
[n9]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/9
[n10]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/10
[n11]: https://github.com/kcook98765/script.tvguide.fullscreen/issues/11
