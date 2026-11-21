# Alpha2 development: practical improvements

As of 21 November 2026, **Alpha2 is development only**, not a release or a
four-version acceptance result. [Alpha 1 is already public](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.0.446-alpha1)
at `fc2f021ef6edc8c957e1ca91bfaa024d17c5f510`, with the later README download
correction merged as `439b8b7`. Its ZIP, SHA-256 and tag are unchanged; use the
[existing download instructions](../README.md#alpha-1-download-and-installation).
The manifest stays **`0.0.446~alpha1`**. No Alpha2 version, ZIP, release or
repository distribution is prepared.

## Six improvements, three merged PRs

Seven confirmed user-visible defect groups were investigated. Six were improved
in three coherent, independently reviewed and normally merged PRs:

| PR | Practical correction | Preserved boundary |
| --- | --- | --- |
| [#62](https://github.com/kcook98765/script.tvguide.fullscreen/pull/62) | AutoPlay before/after saved enum index **6** means the displayed **10 minutes** at both runtime consumers. | All saved choices, indices, order and defaults unchanged; no settings migration or scheduling redesign. [Padding contract](alpha2-autoplay-padding.md). |
| [#63](https://github.com/kcook98765/script.tvguide.fullscreen/pull/63) | Four groups: Quick Select uses the focused programme, not stale/`None` OSD state; Up wraps correctly on an exact full final page; explicit empty labels clear; Quick `focusedProgram` restores the metadata-lookup adapter's selection. | Existing focus repair, placeholders, main-guide routes and optional-provider boundaries retained. `Control.getPosition` unchanged. [Guide contracts](quick-guide-correctness.md). |
| [#64](https://github.com/kcook98765/script.tvguide.fullscreen/pull/64) | Skip rows with unusable programme channel identity/start/stop, continuing through good tails and all three XMLTV sources. | Good metadata, ordering and offsets unchanged; no stop inference, XML syntax repair, broad catch or new title/duration policy. [Programme-row contract](XMLTV-PROGRAMME-ROWS.md). |

The separate Quick left-button discrepancy remains latent/unqualified and was
**not selected**: no bundled Default/Dark/CatBar control **17027** establishes
reachability. No button or skin redesign was added to manufacture it.

The [primary XMLTV DTD](https://github.com/XMLTV/xmltv/blob/master/xmltv.dtd)
requires programme `start` and `channel` attributes, while `stop` is optional.
A missing stop can therefore be valid XMLTV yet unrepresentable by this add-on's
timed grid. The row guard skips it without inventing an end time. Existing
source/fixtures prove the three-slot guard; no native bad-feed switch or setup
was needed, and arbitrary malformed XML is not repaired.

## Why automatic cache invalidation is deferred

The seventh group is real but not a safe small patch. Eleven parse-affecting
settings are omitted from the legacy change detector. Real-schema probes showed:

- Simply adding those keys can treat the first open with an old saved snapshot
  as channel replacement and lose saved rules.
- A parse-expiry flag alone retains the original global programme deletion,
  deleting other-source programmes.
- A source-scoped deletion prototype still collides with programme `UNIQUE`
  identity lacking a source field; later cross-source postprocessing hits a
  foreign-key failure after earlier commits. Rollback does not undo those commits.

These reproduce a persistence boundary, **not a successful preserving refresh**.
No migration/reset framework, database rewrite or data-loss workaround is
included. Existing FileFetcher source-aware caching and additive M3U preservation
remain in place, not reimplemented. A separately scoped preservation design and
independent evidence are needed before this group can be fixed safely.

## Final frozen-source evidence — static gate FAIL

Source: **`be9c64141161e671604a4876404e6aaf64778ccb`**, tree
**`a339971aa620f667eec988173b31d751be303add`**. Runtime freeze:
**317 files / 4,094,697 bytes**. The following results are existing receipts,
independently verified by Codex, not tests rerun for this documentation:

- **21 focused scripts exited 0**, reporting **114 unittest methods plus three
  assertion scripts**, including real official-pytz imports/conversions. Method
  counts are not subtest/assertion counts or native execution proof.
- One four-lane gate: all six stages completed in each lane. **Syntax, manifest,
  paths and package PASS; types and official checker FAIL**. Every process and
  JSON exit is **1**.

| Static target | Kodistubs | Type errors | Locale errors / warnings | Process / JSON exit |
| --- | --- | --- | --- | --- |
| Matrix 19.5 | 19.0.3 | 606 | 3 / 6 | 1 / 1 |
| Nexus 20.5 | 20.0.1 | 606 | 3 / 7 | 1 / 1 |
| Omega 21.3 | 21.0.0 | 606 | 3 / 7 | 1 / 1 |
| Piers 22.0 RC2 | 22.0.1rc1 | 580 | 3 / 7 | 1 / 1 |

Each explicit isolated interpreter ran `stub-lanes` before its matching checker
branch; the branch did not switch stubs. Tool host: CPython 3.12.3, mypy 2.4.0,
checker 0.0.36, unchanged offline index cache. Normalized semantic diagnostics
show **zero additions and zero removals versus Alpha 1**; unchanged failures are
not a static PASS or proof that all diagnostics are false positives.

Warnings and negative-control diagnostics remain retained, including legacy
invalid escapes, offline URL-check limits, entry-point complexity, fixture-file
advice and checker API-version advice. The three inherited locale findings need
owner/translator decisions; **all 69 catalogs / 2,492 entries are preserved**.
No broad typing cleanup, warning suppression or locale guessing was performed.
Matrix static **19.5 is not native 19.4**; Piers is bounded **RC2-only** evidence.

## Final bounded native observations

The following bounded observations and all-four preservation audits are actual
results independently reviewed by Codex, supplied for this documentation. They
are **not full four-version qualification or a release-ready guarantee**.
**Piers Run/guide/playback/Quick remain UNOBSERVED**; the foreground attempt is
not an add-on failure. All original targets are retained and independently
verified stopped; original Current Nexus selection is restored as detailed below.
Historical Alpha 1 aggregate passes remain historical, not substitute acceptance
for changed behaviour.

| Native build | Observed affected behaviour | Explicit limits / UNOBSERVED |
| --- | --- | --- |
| **Nexus 20.5**, Debian `2:20.5+dfsg-1ubuntu1`, code `20.5.0`, Git `20240927-nogitfound` | Padding **10/10 Save/reopen**; original **1/1** restored and saved. Current populated guide; Quick first → last page. While A played, selected B; Select requested B with its named loading overlay and a different frame; ordinary Stop/close. **Exact-multiple Up wrap PASS** independently established from stopped DB/pixels: 246 visible XMLTV channels, no category/sort filter, first/last three title boundaries match, last page starts at **243**. | OpenCode's original channel count was unobserved; Codex's archive/pixel consolidation establishes the wrap result. Numeric saved **6** was **not directly read**: official tagged enum contract plus unchanged XML establish index semantics; 49 actual consumer pairs are deterministic source evidence. Empty-detail clearing and metadata prefill **UNOBSERVED**. No motion/audio/timer qualification. |
| **Omega 21.3**, Debian `2:21.3+dfsg-1ubuntu1`, code `21.3.0`, Git `20260315-nogitfound` | Current populated guide/Quick; selected B while A played, Select showed B's matching loading overlay; ordinary Stop/close. | Up-wrap input **refused before dispatch** because viewer control expired: **UNOBSERVED**, not a failed wrap or a retried test. One supported viewer renewal served selection; no infrastructure changes. No padding writes/repeated Save cycle, new provider, empty-detail or native callback acceptance. |
| **Matrix 19.4**, Debian `2:19.4+dfsg1-2`, code `19.4.0`, Git `20220409-nogitfound` | Three-channel **dateless** guide with old fixture dates unchanged; brief existing mapped clip; Quick highlighted-cell selection returned playback; ordinary Stop/close. | Shared fixture media does **not** independently prove distinct B-channel identity: **UNOBSERVED**. Historical crash/SIGSEGV did not recur here but remains **UNRESOLVED**; no debugger/reopen/crash campaign. No new padding UI/timer/provider qualification. |
| **Piers 22.0-RC2 (21.90.902)**, Git `20261109-d686683a-dirty`, reported compile date `2011-11-11`, Linux x86_64 | Native Add-ons root independently viewed; background updater started/finished. Final stopped preservation audit completed. | Initial attempt and **one supervisor-authorized bounded supplement** retained separately. Supplement reached **Add-ons only**: Program-add-ons input refused before dispatch, one supported viewer renewal, then a second pre-input refusal. Optional checks stopped permanently. **Run/guide/playback/Quick UNOBSERVED**, not an add-on failure; no further runtime attempts or infrastructure work. |

Empty-detail label clearing and metadata prefill have no new native acceptance;
their deterministic source evidence remains separate. These rounds did not
repeat ten-minute waits, recurrence/reconstruction, sound/races, the old
eight-point acceptance gate or full skin/provider work. No new official add-on
was installed.

### Four completed stopped-profile preservation audits

All four retained exact **GEN10**, the frozen `be9c641` runtime: **317 files /
4,094,697 bytes**, payloads/modes checked by Codex against stopped after-archives
and a second live read. All **595 original unused vendor files** were exact and
retained; all **611 official pytz payloads** were exact, and other add-on payloads
were unchanged.

| Protected data / ordinary guide refresh | Nexus | Omega | Matrix | Piers |
| --- | --- | --- | --- | --- |
| Channel rowids/all fields exact | 247 | 247 | 4 | 4 |
| Primary mapping values exact; alternatives also exact | 249 | 249 | 3 | 3 |
| Reminder + AutoPlay rules: all fields/associations exact | 0 + 0 | 0 + 0 | 1 + 1 | 1 + 1 |
| Programmes before → after | 2,266 → 2,037 | 2,234 → 2,000 | 24 → 24 | 24 → 24 |

Database integrity passed and foreign-key checks were clean. Nexus/Omega
programme counts changed through ordinary refresh/aging, not preservation loss
of protected channel identifiers, schedule rows/associations or mapping values.
Channel-table and all three schedule-table rowids/all fields were identical in
all four profiles. Primary mapping **values (`channel`, `stream_url`)** and
alternatives were exact; internal `custom_stream_url` rowids changed on
Matrix/Nexus/Omega, consistent with existing delete+insert mapping refresh paths
(`_setCustomStreamUrl` / `_setCustomStreamUrls`). Piers mapping rowids were also
exact. These internal mapping rowids are not mapping/channel/schedule identities;
**not every database rowid was preserved**. Existing JSON event-file hashes were
retained (Nexus **1**, others **0**); no event JSON was added or deleted.

Original preferences, including padding
**1/1** and `channelIdx` **0**, were restored unchanged. Generated `last.channel`
history, the existing version marker **0.0.445 → 0.0.446~alpha1**,
`last.background.update` and core uptime changed in the first three rounds.
Piers changed only its version marker, background-update time and core uptime.
**Do not infer byte-identical whole profiles or all settings bytes.**
No profile/cache/database reset or manual
deletion/restoration was used.

All four original profiles/identities are independently verified **STOPPED**,
with **no pending operations** and owned browsers closed. Original **Current
Nexus selection 46** is restored with the same source/workspace **GEN10**;
the browser is closed and **Nexus was not started** for restoration.

Codex checked complete stopped current/old logs: no selected Python traceback,
`PythonToCppException` or import-failure markers in these rounds. Piers current
log: **293 lines / 29 ERROR / 0 FATAL**; old: **290 / 27 / 0**, with zero selected
Python exception markers and inherited `SyntaxWarning`s. Caught
missing-control diagnostics and many environment/audio errors persist:
Nexus retains **23 caught missing-control EXCEPTION entries**, not zero exceptions.
**logs are not clean**. Limited-tail and invalid-scan receipts remain retained,
not substitutes for the full-log audit or evidence of clean logs.

README/docs do not change the runtime inventory; this update's neutral changelog
prefix is its sole runtime-byte difference from the source freeze. The independent
final original-profile preservation and Current-selection audits are complete;
they do not establish foreground behaviour or native scheduler acceptance.
No native actions, additional tests or static gates were performed to prepare
this documentation update.

## Recommended next scope

Keep **#2/#4/#5/#8/#14/#21 OPEN**. Recommend these **six improvements only** as
the smallest future Alpha2 scope. **Targeted Piers UI verification remains
outstanding before a confidence claim**, with no further attempt authorized in
this task. No native scheduler acceptance, features or packaging are added.
Any future release/version/package needs separate authorization. The
[full original feature inventory and historical
qualification records](modernization-status.md#feature-inventory), attribution,
catalogs and entire previous changelog remain intact. No extra unsafe execution
restoration, functional source, tests, settings, dependency or manifest change is
part of this documentation update.
