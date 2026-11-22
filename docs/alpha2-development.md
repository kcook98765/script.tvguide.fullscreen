# Continued practical TV Guide development

The **21 November 2026 continued-development campaign** (completed across the
22 November UTC boundary) remains development only, not a release or four-version
acceptance result. [Alpha 1 is already public](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.0.446-alpha1)
at `fc2f021ef6edc8c957e1ca91bfaa024d17c5f510`, with the later README download
correction merged as `439b8b7`. Its ZIP, SHA-256 and tag are unchanged; use the
[existing download instructions](../README.md#alpha-1-download-and-installation).
The manifest stays **`0.0.446~alpha1`**. No Alpha2 version, ZIP, release or
repository distribution is prepared.

## Once-cancellation follow-up

Source correction **`efac84a234c9ecbf90013dacd7eb6323b83cecf4`** is independently
accepted in [PR70](https://github.com/kcook98765/script.tvguide.fullscreen/pull/70).
Its [ownership contract](schedule-ownership.md#once-cancellation-follow-up-21-november-2026-campaign)
has retained source evidence: **10 scripts / 60 unittest methods + three assertion
scripts**, including 14 new methods, pinned-original 48 assertion failures and six
failing narrow mutations (no fixture errors). These are not native UI results;
the documentation follow-up reruns no product tests, types or full static gate.
Inherited static **FAIL**, warnings and historical scopes remain unchanged.

The subsequent single **Nexus20.5** attempt used one explicit Start request
(observation with the same UUID was not another Start). GEN11→**GEN12** capture,
structural validation and guarded deployment succeeded. Exact GEN12 target/workspace
script0 launch was then **refused before dispatch: `launch_not_deployed`**. Testing
stopped immediately: no menu fallback, redeployment or retry. File deployment
does **not** establish fresh-code execution. Codex independently checked 23 actual
MCP events and the **Home-only** PNG: no guide launch, no rules created, and all
native once transitions/callback behavior **UNOBSERVED**, not failed or accepted.
Viewer/browser closed and Stop was confirmed. Native authority has ended.

Codex's stopped-archive plus second-read audit verified protected table fields
**and rowids** exactly: 247 channels, 249 primary mappings, reminder/AutoPlay rules
**0/0**, other schedule/alternative mapping rows and the original one event JSON.
All **322 candidate + 595 retained vendor + 611 official pytz files** were exact;
other add-ons were unchanged. Only `last.background.update` preference changed;
programmes **2,209→2,090** through normal refresh, not a byte-identical Nexus profile.
The other three whole profiles were exact. All four original identities remain
**stopped**, original Current Nexus selection **46**, no pending work.

Current/old logs: **585/552 lines, 199/177 ERROR, 0/0 FATAL**; selected exception
and playback markers are zero. Logs remain **non-clean**, with **no guide UI
coverage**; reduced diagnostics are not a fix. No further native/tooling
investigation is authorized. Broader #21 remains open. The earlier campaign and
GEN11/GEN10 evidence below retain their own exact sources and historical limits.

## Four further corrections, two merged PRs

Both PRs were independently reviewed by Codex and normally merged:

| PR | Practical correction | Preserved boundary |
| --- | --- | --- |
| [#66](https://github.com/kcook98765/script.tvguide.fullscreen/pull/66) | Match the existing once/always/new/daily rules across all applicable rows, plus source-wide SQL LIKE reminders. Refresh popup scheduling labels after navigation; dispatch against the current selected programme's authoritative database state, so a listing's stale flags do not turn “Don't Remind/AutoPlay” into duplicate registration. Cancelled/empty wildcard input creates no rule/action on either route, retaining redraw and selected metadata. | Existing programme handlers are the selected small restoration. No recurrence, removal-policy, callback, provider or unsafe-execution expansion. |
| [#67](https://github.com/kcook98765/script.tvguide.fullscreen/pull/67) | Use the existing normalized channel ID only when XMLTV display-name is `None`, retaining the channel and valid trailing rows/later sources. | All-valid output, explicit empty/whitespace names, identities, programme links, offsets and logo precedence preserved. No feed repair, cache invalidation or settings refresh. |

Final functional source: **`ce8fe0fdf75a4622c767a95a1a322d626b3ae46f`**, tree
**`f7135e7f0df191b841f644320613b5a78b5ffacc`**. Its runtime freeze is **317 files /
4,096,555 bytes**. These are the tested source bytes, not a new installer. This
docs update preserves every functional/runtime file except a neutral changelog
prefix; that prefix changes the runtime byte total, not the tested Python.

## Final continued-development evidence — static failures retained

These are retained results, not tests rerun to author documentation. Codex
independently checked 378 source files, 317 runtime files and 64 raw-output hashes,
and replayed the semantic diagnostic comparison.

- **23 scripts PASS: 128 unittest methods plus three assertion scripts**; methods
  are not subcase/assertion counts. Affected files pass **Python 3.8 grammar**,
  a separate host check, not the full CLI syntax stage or embedded-Python proof.
- Per-PR original-failure and mutation negatives remain retained, as do earlier
  failed harness results; none is rewritten into a product PASS.
- Only the original Toolkit **private types stage** was freshly run per pinned
  interpreter, after its `stub-lanes` report. This was **not a full CLI gate**.

| Static target | Kodistubs | Type errors before → after | Semantic additions / removals | Inherited checker locale errors / warnings |
| --- | --- | --- | --- | --- |
| Matrix 19.5 | 19.0.3 | 606 → 608 | +2 / −0 | 3 / 6 |
| Nexus 20.5 | 20.0.1 | 606 → 608 | +2 / −0 | 3 / 7 |
| Omega 21.3 | 21.0.0 | 606 → 608 | +2 / −0 | 3 / 7 |
| Piers 22.0 RC2 | 22.0.1rc1 | 580 → 582 | +2 / −0 | 3 / 7 |

Both new `union-attr` errors are at the context-menu DB rechecks
(`gui.py:1961/1978`), exposing the existing optional database model. The unchanged
popup constructor already dereferences that database earlier; valid-DB fixtures
pass and no new `None` runtime path has been demonstrated. **Static uncertainty
remains**: these are genuine new diagnostics, not automatic false positives,
zero delta or typing cleanup. The inherited duplicate-`getControl` message's
embedded line **439 → 440** is relocation only; both method ASTs are unchanged.
Each collecting worker exited **0**, but returned mypy exit **1**: types **FAIL**.

The **full six-stage gate and official checker were NOT RERUN**. Inherited
syntax/manifest/paths/package PASS and types/checker FAIL retain their earlier
exact-source scope; no fresh CLI validation exit or static PASS is claimed.
All warnings and negative diagnostics remain retained, including the three locale
errors per lane and warnings **6/7/7/7**. Tool host CPython 3.12.3, mypy 2.4.0 and
checker 0.0.36 do not identify embedded Kodi Python; branch selection does not
switch stubs. Matrix static **19.5 ≠ native 19.4**; Piers remains bounded RC2-only.

## One bounded Nexus native round — not scheduler acceptance

Only **Nexus 20.5**, on the same source/workspace at **GEN11**, ran in this campaign.
Codex independently viewed meaningful pixels: populated guide/context, ordinary
Remind/AutoPlay labels, recurrence chooser, wildcard keyboard **Cancel** returning
to a populated guide/redraw, and ordinary close. The owned viewer/browser closed
and supported **Stop was confirmed**. No rule was created: saved reminders and
AutoPlay remained **0/0**, and the existing event JSON remained unchanged.

**Native UNOBSERVED:** listing once cancellation, new/daily matching and the second
key-input route. Selected query/handler behavior has focused actual-method/SQLite
evidence, not native acceptance. **Actual Kodi timer/callback delivery remains
unobserved and unqualified.** XMLTV fallback is deterministic parser
evidence only, with no native malformed-feed/settings switch. Matrix, Omega and
Piers were **UNRUN this campaign**; no Piers retry or Matrix crash work occurred.
Historical Alpha2 and Alpha 1 observations below do not fill these gaps.

### Independently verified stopped preservation and logs

Codex's fresh stopped-file audit matched all **317 candidate payloads/modes**,
**595 retained unused vendor files**, **611 official pytz payloads** and unchanged
other add-ons on Nexus. All **247 channel rowids/fields**, **249 primary mapping
values**, alternative mappings, schedule tables/associations and the one existing
event JSON were exact. Internal primary-mapping rowids changed through ordinary
refresh; not every database rowid was preserved. Integrity passed and FK checks
were clean. Normal programme refresh changed **2,037 → 1,760** rows. Only generated
`last.background.update` and core uptime preferences differed; **Nexus's whole
profile is not byte-identical**. No manual profile/cache/DB reset or restoration.

The untouched Matrix/Omega/Piers **whole profiles matched before/after exactly**.
All four original identities were retained and independently verified **stopped**,
with no pending operations. Original Current Nexus selection/binding stayed
unchanged; Nexus alone advanced from historical GEN10 to **GEN11**. No new runtime
authority follows from that final state.

Complete Nexus current/old logs contain **3,166 / 552 lines**, **1,927 / 177 ERROR**
and **0 / 0 FATAL**. Neither has the selected traceback, `PythonToCppException`,
import-failure or `UnboundLocalError` markers. Current has **7 caught optional-control
EXCEPTION entries**, old **0**: logs are **NON-CLEAN**. Prior triage classified
**22 of 23** entries as guarded optional static hooks and **one dynamic control
3019 unresolved**. The count drop is exercise coverage, not a fix. No controls,
skins, `Control.getPosition` or log-suppression changes were made.

## Next work: continue practical development

Broad trackers **#2/#4/#5/#8/#14/#21 remain OPEN** for their remaining scope.
No issue closure or automatic publication is recommended.

1. **Once-cancellation source follow-up:** the [narrow ownership contract](schedule-ownership.md#once-cancellation-follow-up-21-november-2026-campaign)
   now isolates exact once intent and explicitly selected recurring/LIKE rules,
   retains shared clicked-event actions beyond the normal reconstruction horizon,
   and uses a minimal rule chooser when several owners match. Actual-schema and
   inert producer/UI regressions are source evidence, **not native cancellation
   or callback acceptance**. Broad #21 and historical recovery/race limits remain.
2. Separately review a **preserving XMLTV settings-refresh design**: distinguish
   parse changes from channel replacement, retain rules/mappings/identities,
   account for source-less programme uniqueness and committed postprocessing,
   and test failure/rollback without destructive first-open snapshot handling.
3. Investigate **dynamic control 3019 only if reproduced with useful context** or
   a user symptom, not to suppress an isolated diagnostic.

Defer invasive/speculative legacy, VOD, dateless-OSD reachability, provider,
FFmpeg, complex-skin, Matrix crash and Piers input work. No source/test/settings/
manifest/version changes, new artifact or distribution are part of this docs PR.
Only focused documentation checks run here: no new product tests, types, full
gates or native stages. The original feature inventory and historical reports
remain [in the overview](modernization-status.md#feature-inventory).

## Historical Alpha2 checkpoint — superseded as current status

The following earlier record is retained with its failures and limits. Its
“final”, “current”, GEN10, zero-delta, Piers follow-up and future-Alpha2
recommendations refer **only to that older checkpoint**, not the continued
`ce8fe0f` campaign above. In particular, no new Piers attempt is recommended here.

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
