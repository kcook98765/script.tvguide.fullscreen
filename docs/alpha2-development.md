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

## Native acceptance and preservation — PENDING

Affected-behavior native acceptance remains **PENDING** for **Matrix 19.4,
Nexus 20.5, Omega 21.3 and Piers 22 RC2**. No new per-version PASS, final stopped
state or completed preservation audit is claimed here. Actual outcomes must come
from supervisor-reviewed native observations and exact-byte/preservation facts.
Historical Alpha 1 bounded four-version results remain historical, not acceptance
of these changed behaviours. The historical Matrix crash remains unresolved.

README/docs do not change the runtime inventory; this update's neutral changelog
prefix is its sole runtime-byte difference from the source freeze. Independent
final reconciliation remains pending. No native actions, additional tests or
static gates were performed to prepare this documentation.

## Recommended next scope

Keep **#2/#4/#5/#8/#14/#21 OPEN**. Recommend these **six improvements only** as
the smallest future Alpha2 scope, pending the native/preservation review; add no
features or packaging yet. The [full original feature inventory and historical
qualification records](modernization-status.md#feature-inventory), attribution,
catalogs and entire previous changelog remain intact. No extra unsafe execution
restoration, functional source, tests, settings, dependency or manifest change is
part of this documentation update.
