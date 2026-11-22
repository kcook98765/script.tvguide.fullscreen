# Current fork feature and qualification status

> Current notice (2026-11-21, unreleased): legacy Zomboided VPN Manager integration
> is intentionally removed. Historical VPN-preservation audit rows below remain
> verbatim, not current behavior claims. [Removal evidence/limits](vpn-manager-removal.md)
> are separate from earlier qualification. One Nexus GEN13 deployment succeeded;
> only Kodi Home was observed. A prelaunch log diagnostic returned `invalid_params`;
> testing stopped without guide launch or playback observation. Full gate remains FAIL.

## Current continued development — 21 November 2026 campaign

**Continue practical development, not automatic publication.** The existing
[Alpha 1 prerelease](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.0.446-alpha1),
tagged at `fc2f021ef6edc8c957e1ca91bfaa024d17c5f510`, public installer and checksum are
unchanged. Manifest **`0.0.446~alpha1`**, settings, GPL/upstream history and the
original feature inventory remain preserved. No new version, package or
distribution is prepared. The campaign finished across 22 November UTC.

Following the earlier six Alpha2 improvements in #62/#63/#64, independently
reviewed, normally merged [PR66](https://github.com/kcook98765/script.tvguide.fullscreen/pull/66)
and [PR67](https://github.com/kcook98765/script.tvguide.fullscreen/pull/67) add four
practical corrections: existing reminder/AutoPlay event matching across all
applicable once/always/new/daily rows and source-wide LIKE reminders; current-popup
state/authoritative DB dispatch instead of stale listing flags; wildcard Cancel
creating no rule/action on either route while retaining redraw/metadata; and
absent-only XMLTV display-name fallback to the existing normalized channel ID.
No scheduling removal-policy, provider or unsafe/parity expansion is included.
See [continued scope and evidence](alpha2-development.md) for exact boundaries.

Functional freeze **`ce8fe0fdf75a4622c767a95a1a322d626b3ae46f`**, tree
**`f7135e7f0df191b841f644320613b5a78b5ffacc`**: **317 runtime files / 4,096,555
bytes**. Codex independently audited source/runtime/raw-output hashes and replayed
the diagnostic comparison. **23 focused scripts PASS: 128 unittest methods plus
three assertion scripts**; affected Python 3.8 grammar PASS. Per-PR negative
proof and warnings remain retained. These are saved results, not new doc-authoring
tests. The neutral changelog prefix is this PR's only runtime-byte difference.

| Static lane | Fresh private types: before → after | Inherited locale errors / warnings |
| --- | --- | --- |
| Matrix 19.5 | 606 → 608 | 3 / 6 |
| Nexus 20.5 | 606 → 608 | 3 / 7 |
| Omega 21.3 | 606 → 608 | 3 / 7 |
| Piers 22.0 RC2 | 580 → 582 | 3 / 7 |

Only the original Toolkit private types stage ran freshly per pinned interpreter:
**two added / zero removed errors per lane**. The context DB rechecks expose the
existing Optional model; the constructor already dereferences DB earlier and
valid-DB fixtures pass, but no new `None` runtime path is demonstrated. These
remain **unresolved static failures**, not automatic false positives or zero
delta. Duplicate-`getControl` embedded line 439 → 440 is relocation only.
Worker exit **0** is collection success; returned mypy exit **1** is types FAIL.
**Full gate/checker NOT RERUN; inherited full gate FAIL** (syntax/manifest/paths/
package PASS, types/checker FAIL at its older source). Warnings/negative controls
remain; no static PASS or broad typing cleanup. Matrix static 19.5 differs from
native 19.4; Piers evidence remains bounded RC2-only.

One **Nexus 20.5 / GEN11** round has independently viewed populated guide/context,
Remind/AutoPlay labels, wildcard chooser/keyboard Cancel returning to guide/redraw,
ordinary close, closed owned viewer/browser and confirmed Stop. **No rules
created: 0/0 and one event JSON preserved.** Listing once cancellation, new/daily,
the second key route and actual timers remain **native UNOBSERVED**. XMLTV fallback
is deterministic only. Other three versions were **UNRUN** this campaign; no
Piers attempt or Matrix crash work. No full four-version/callback acceptance.

Codex's fresh stopped Nexus audit matched 317 candidate payloads/modes plus 595
retained unused vendor files, all 611 official pytz payloads and unchanged other
add-ons. All 247 channel rowids/fields, 249 mapping values, schedule associations
and event JSON were exact; internal mapping rowids changed. Only generated update
time/core uptime preferences differed, with normal programmes **2,037 → 1,760**;
Nexus is not whole-profile byte-identical. The other three **whole profiles are
exact before/after**. All four ended **STOPPED**, no pending operations; original
Current Nexus binding unchanged, same source/workspace now **GEN11**.

Nexus complete current/old logs: **3,166/552 lines, 1,927/177 ERROR, 0/0 FATAL**;
**7/0 caught optional-control EXCEPTIONs**, no selected traceback/PythonToCpp/
import/UnboundLocal markers. **NON-CLEAN logs**. Prior 23-entry triage classified
22 guarded optional static hooks and one unresolved dynamic **3019**. Fewer entries
mean different exercise coverage, not a fix. No control/skin/`getPosition` or
log-suppression changes. [Detailed preservation and log limits](alpha2-development.md#independently-verified-stopped-preservation-and-logs).

Broad trackers **#2/#4/#5/#8/#14/#21 remain OPEN** for their remaining scope.
Next: event-scoped once cancellation; separately reviewed preserving XMLTV
settings refresh; dynamic 3019 only if reproduced with useful context. Defer
invasive/speculative legacy/VOD/dateless-OSD/provider/FFmpeg/skin, Matrix crash and
Piers input work. This docs PR runs only focused doc checks, no product tests,
types, gates or native stages. Older Alpha2/GEN10 observations are
[historical](alpha2-development.md#historical-alpha2-checkpoint--superseded-as-current-status),
not current acceptance; the original feature inventory and reports below remain
intact under their historical scope notices.

## Historical Alpha2 U1 implementation checkpoint

[Guide correctness U1](quick-guide-correctness.md) records focused Quick selection,
page wrapping, label clearing and retained metadata-focus fixes. Deterministic
source fixtures are not new native acceptance; the initial Alpha results and
feature inventory below retain their original scope and provenance.

## Historical Alpha 1 qualification and prepublication record — 21 November 2026 UTC

**Historical scope notice:** everything from this heading through the next
historical-snapshots notice records the earlier Alpha 1 qualification and private
candidate preparation. Its “unpublished”, “not created”, “planned”, “current” and
candidate-filename statements describe that earlier checkpoint, not today's
publication state or Alpha2 acceptance. Alpha 1 was subsequently published as
linked above; use the [README download instructions](../README.md#alpha-1-download-and-installation)
for the actual public installer filename, checksum and immutable tag. Native and
static results below retain only their original exact-source scope.

**All four versions are owner-decided initial Alpha scope. Bounded aggregate
native gate: PASS on all four retained installations. Final four-lane static gate:
FAIL.** The former Nexus-first recommendation is obsolete. No Alpha release is
published, and no official-repository intake readiness or stable/all-platform
qualification follows.

Native inputs were executed in separately assigned OpenCode sessions; Codex
independently reviewed the functional observations, exact installed bytes,
receipts, logs and before/after stopped-profile archives. The aggregate result
uses explicit historical **component** reuse, not a claim that every criterion
was repeated from scratch on each build.

| Initial-scope native version | Independently reviewed bounded outcome and limits |
| --- | --- |
| Matrix **19.4** | **PASS**: fresh populated current guide, metadata, close/reopen, context, positive/empty search, logo settings, moving mapped local clip/Stop and service work; historical actual reconstructed AutoPlay/NOW reminder and same-profile restart evidence reused. Original nonempty rules, mappings and preferences restored/audited. Historical SIGSEGV/ordinary-reopen crash did not recur in this bounded pass; **not resolved**. Static 19.5 is not native 19.4. |
| Nexus **20.5** | **PASS aggregate with historical reuse**: fresh post-dependency-change guide/imports, mapped start/Stop, close/reopen, service and preservation; new navigation/context/positive search plus verified earlier empty-edge/logo observations and unchanged focused regressions. **Current LAN picture motion unverified**, despite advancing clock; that current playback round remains PARTIAL. Independently verified historical moving local mapped clip and actual callbacks supply only the unchanged critical component portion. |
| Omega **21.3** | **PASS aggregate with historical reuse**: fresh post-dependency-change guide/imports, mapped start/Stop, close/reopen, service and preservation; verified earlier navigation/search/context/logo observations and unchanged focused regressions. **Current LAN picture motion unverified**, despite advancing clock; that current playback round remains PARTIAL. Historical moving local mapped clip and reconstructed AutoPlay reused; historical post-restart NOW reminder remains unobserved. Earlier unrequested exit is not claimed resolved. |
| Piers **22.0-RC2** | **PASS on exact tested RC2**: fresh current populated guide, metadata, close/reopen, context, positive/empty search, logo settings, moving mapped local clip/Stop and service; historical actual reconstructed AutoPlay/NOW reminder reused. Original nonempty rules, mappings and preferences restored/audited. Exact build **21.90.902**, Git **20261109-d686683a-dirty**. Earlier occasional blank modal did not recur in tested menus; **not resolved**, and no future stable-Piers promise. |

### Eight-point acceptance and provenance

All four aggregate results cover the same eight criteria: (1) preserved
Program+service manifest, dependencies and actual imports; (2) ordinary populated
GUI Run/close/reopen; (3) usable XMLTV metadata, offsets/cache and logo behavior;
(4) M3U mapping, actual video progression and ordinary Stop; (5) navigation,
selection/context, positive/empty search and empty-programme safety; (6) guide,
preferences, mappings and original-rule persistence; (7) **fresh actual background
work** plus actual reminder **or** ordinary AutoPlay; (8) exact provenance,
screens/logs/receipts, supported terminal Stop and independent preservation audit.

- Native functional source:
  `4b2a83fbd98bc7aa7556bb19fa5f31401c32c0dc`, tree
  `61b859191c898c2ee07182d45ba7cec781677cb4`, workspace **GEN9**. Frozen static
  candidate `85b931bf2a351549b20271a3038877938fb7f83e`, tree
  `fb378fa5f9519cd9e832fc8e23bb44c5bed0973c`, differs in runtime only by **329
  neutral changelog bytes**. Python/manifest/resources are unchanged; later
  README/docs-only edits do not change the tested runtime.
- Historical moving clips/callbacks were independently observed and reused only
  after matching the critical playback/scheduler functions and original runtime
  identity. This does **not** prove whole historical GUI/importer identity or
  current LAN picture motion/audio/full-stream behavior. Fresh imports/guide and
  actual service work bridge the official dependency change on all four targets.
  No exhaustive recurrence/cancellation or every reminder-phase result is implied.
- Required official **`script.module.pytz >= 2023.3.0+matrix.1`** is separately
  installed/enabled and actually used on all four; each installed **611-file
  module payload** exactly matches its reviewed official package. Catalog checks
  alone were not used as installation proof. Both `addon.py` and `service.py`,
  all other dependencies and explicit background consent are preserved.
- The prior all-four native tests used retained installations: **317 reviewed
  files + 595 unchanged unused old vendor files**, not clean replacement/pruning.
  The clean static export is **317 files / 4,093,191 bytes**, with no
  `resources/lib/pytz` and the 329-byte changelog addition included. Neither the
  export nor a private unchanged
  **0.0.445** qualification preview establishes native clean-install success or
  provides a public release installer.
- Original saved rules/mappings and preference values were independently audited
  after restoration; ordinary service timestamps, caches/search history and guide
  refreshes can change. Whole profiles are **not byte-identical**. All four tests
  ended stopped with original identities preserved; no cleanup/Reset was used.
- Ordinary native **Program Info → Run** is distinct from the known Lab
  `launch_not_deployed` refusal. Fixed video-plugin smoke is ineligible for this
  Program+service manifest; workspace launch was unavailable under the testing
  client. Functional acceptance comes from observed ordinary GUI behavior, not
  from a refused tool, enabled flag, copy or launch acknowledgement.

### Final focused and static results — same frozen runtime

One final focused core batch passed **19 scripts: 97 unittest cases plus three
assertion scripts**, including real official-pytz imports/conversions and retained
negative controls. Existing invalid-escape `SyntaxWarning` diagnostics remain in
the raw evidence. No optional provider/recording/skin or Toolkit/Lab suite was
substituted for this bounded scope.

One integrated four-lane CLI gate completed on the clean 317-file export. In
**every lane**, all six stages are accounted for: **syntax PASS, manifest PASS,
paths PASS, package PASS, types FAIL, official checker FAIL**.

| Static lane | Kodistubs | Current type errors (GEN8 baseline) | Current checker errors / warnings (GEN8) | Process / JSON exit |
| --- | --- | --- | --- | --- |
| Matrix **19.5** | **19.0.3** | **606 (641)** | **3 / 6 (3 / 9)** | **1 / 1** |
| Nexus **20.5** | **20.0.1** | **606 (641)** | **3 / 7 (3 / 10)** | **1 / 1** |
| Omega **21.3** | **21.0.0** | **606 (641)** | **3 / 7 (3 / 10)** | **1 / 1** |
| Piers **22.0-RC2** | **22.0.1rc1** | **580 (615)** | **3 / 7 (3 / 10)** | **1 / 1** |

Each explicit lane interpreter ran `stub-lanes` then validation with its matching
branch and unchanged offline index cache; `--branch` did not select stubs. All
stub reports exited 0; host tooling was **CPython 3.12.3 / mypy 2.4.0 / checker 0.0.36**,
not proof of Kodi's embedded Python patch version. Matrix static 19.5 differs from
native 19.4. Piers retains exact-RC2/prerelease-stub coverage limits and checker
advice. Source/export/cache hashes were preserved through the one gate; warnings,
negative controls, full diagnostics and actual exits were retained, not suppressed.

Compared with GEN8/`965ee470`, each lane has **one new type error plus three notes**:
`source.py` imports official `pytz`, but `types-pytz` stubs are not installed in
the locked toolchain (`import-untyped`). This is a real **static typing coverage
gap**, not a native `ImportError`; real-module focused checks and native imports
passed. **36 errors and 22 notes disappeared solely with deleted vendor code**,
not 36 runtime fixes. The remaining **605/605/605/579 type errors are inherited**,
unresolved debt—not all false positives. No environment/config update was made.

After normalizing both validator and checker random temporary paths, all **three
checker errors are identical inherited locale-directory findings**: Georgian,
Haitian (Haitian Creole) and Vietnamese (Viet Nam). All **69 catalogs / 2,492
entries** remain intact pending owner/translator decisions. **No new checker
warning** was introduced; only three removed vendor `.tab` files account for the
warning reduction. This disclosed debt may inform an Alpha decision, but the
static gate stays **FAIL** and does not establish official-repository intake
readiness. No new functional regression was demonstrated by these deltas.

### Alpha release candidate preparation — still unpublished

The shared manifest version is now **`0.0.446~alpha1`**, prepared for independent
candidate review. Only version/news and changelog runtime metadata change;
Python logic, dependency floors, settings, artwork and catalogs are unchanged.
Metadata changes alone are not a runtime regression result. [Kodi Wiki ordering](https://kodi.wiki/view/Addon.xml#How_versioning_works)
documents `~alpha` before the corresponding unsuffixed version. The separate
proposed Git tag is **`v0.0.446-alpha1`**; Git tags cannot contain `~`.
The tag is **not created**. The private candidate build contains
**one common `script.tvguide.fullscreen-0.0.446~alpha1.zip`
with a single `script.tvguide.fullscreen/` root**, final SHA-256, exact
source/candidate build notes and actual per-version results and limitations.
A private qualification ZIP at unchanged **0.0.445** is not that release artifact.
The same **317 runtime paths** are retained, with new manifest/changelog hashes;
GPL and embedded notices remain, while official pytz and its notice stay in its
separate official module. Focused manifest/package/metadata checks do not replace
the recorded six-stage FAIL above; no full four-lane gate is rerun here.
Separately from the prior all-four retained-install gate, the **actual candidate
ZIP** passed ordinary Kodi **Install from zip file** in one new, genuinely clean,
isolated **Nexus 20.5** environment. Version **`0.0.446~alpha1`** was enabled;
required official requests **2.31.0**, dateutil **2.8.2**, pytz
**2023.3.0+matrix.1** and BeautifulSoup **4.12.2** were automatically installed,
with PIL **5.1.0** already bundled by that environment. Ordinary **Program Info →
Run** displayed **two visible synthetic fixture channels and two programmes**,
with titles, times and description, independently viewed by Codex. This tests the
private ZIP from source **`7e5e76518553ee42024549448e15eb996e4ebd0a`**, not a source-copy
substitute; its **317 files / 4,093,446 logical bytes** remain frozen.

**Actual background-service work independently passed** after one ordinary
restart of the same disposable instance, without manual service execution.
The update started and finished and its saved update timestamp advanced; this is
not inferred from enabled state or foreground parsing. Final Stop exited
gracefully with no forced kill. **The complete bounded clean-install smoke is
PASS**, accepted by Codex after independent stopped-file, provenance and log
audit. All **317 installed payloads and modes** matched the tested ZIP; all **69
catalogs** were preserved, no bundled `resources/lib/pytz` remained, and the only
extra runtime files were generated bytecode. Downloaded required modules were
enabled with official Kodi repository origin; the separate official pytz module
matched all **611 reviewed package files**. Complete current and previous logs
contained no `ImportError`, `ModuleNotFoundError` or Python traceback. **Logs were
not clean**: audio/environment errors and existing syntax warnings remained.

This is one representative clean Nexus installation, not four clean installs,
upgrade-pruning proof, new playback/timer qualification or
a new four-version runtime gate. The prior retained-install evidence, static
FAIL and limitations above remain unchanged.

The prerelease is **planned and unpublished**, without invented asset URLs;
tag/release creation, ZIP upload and repository publication need separate explicit
approval. See [planned user installation](alpha-installation.md).

No stable, future-stable Piers, all-platform, full-parity, clean-log or static-pass
claim is made. Font/glyph limitations, caught control diagnostics and environment/
audio errors remain; no prolonged-stream or broad stability campaign is implied.
Never publish private feed names/URLs, settings, credentials,
private logs or unsanitized screenshots. Historical upstream attribution, GPL,
translations, the full changelog tail and qualification receipts remain intact.

## Historical snapshots below — superseded as the current overview

Everything below this notice is retained verbatim from the documentation base.
Its “current”, “final”, “authoritative”, owner-pending and Nexus-first wording,
tables and source pins refer to those **older exact-source checkpoints**, not the
current campaign. In particular, issue54 is no longer future work and the former
912-file vendor-inclusive source is not today's clean source inventory. Historical
results, failures, receipts and limitations remain evidence for their stated
scope; none is silently promoted to a new four-version PASS. The current section
above governs current scope, outcomes and remaining limits.

## Dependency/package follow-up — issue #54

The [official pytz follow-up](official-pytz.md) replaces the bundled module and
changes the manifest/import/package bytes. It is **not** covered by the historical
912-file `965ee470` / GEN8 qualification below. Codex independently accepted the
source/dependency/package/license review and passed the four focused commands at
runtime freeze `023bf2670f0c6e910c49e5bd54e941fe8ee7d52a`. One ordinary native
**Nexus 20.5 guide/XMLTV startup passed**, with the official module installed and
all 611 module file payloads exact. This was a **retained-copy** deployment, not a
clean install or native vendor-removal proof; the MCP exact-launch path was
refused/unqualified, separate from successful ordinary GUI Run. See the focused
record for the corrected installer error, preservation and non-clean-log limits.
Four-catalog declarations are not four-native qualification. This docs-only
follow-up reruns no tests/native actions. Historical receipts/tables and
owner-pending Nexus-first release scope stand; no release decision is implied.

## Historical frozen Alpha qualification

This is the authoritative current overview. The reviewed Alpha source batch
([#44](https://github.com/kcook98765/script.tvguide.fullscreen/pull/44),
[#46](https://github.com/kcook98765/script.tvguide.fullscreen/pull/46),
[#48](https://github.com/kcook98765/script.tvguide.fullscreen/pull/48),
[#50](https://github.com/kcook98765/script.tvguide.fullscreen/pull/50),
[#52](https://github.com/kcook98765/script.tvguide.fullscreen/pull/52)) and Phase5
[#56](https://github.com/kcook98765/script.tvguide.fullscreen/pull/56) were
independently accepted and normally merged. Final frozen runtime:
[`965ee470e80abaaf13788ff921852ecdf6f0cfda`](https://github.com/kcook98765/script.tvguide.fullscreen/commit/965ee470e80abaaf13788ff921852ecdf6f0cfda),
Git tree `3c1f01374bbc452bf643b9ac1b623babb4f74b26`.
The reviewed runtime inventory is **912 files / 4,894,184 bytes**, aggregate
SHA-256 `64e7fd38f2069bf5d04c2500dabc9e47d7f506c23b034b30c01bab15d4e60376`.
Source/cache were unchanged by the final gate. A later README/docs-only merge
inherits qualification only after supervisor proof of protected runtime identity.
Overall acceptance: [#1][overall]; preservation: [#14][preservation];
dependencies/settings: [#3][dependencies]. No release or full legacy parity is claimed.

## Qualification

**Overall qualification: PARTIAL. Final four-lane static gate: FAIL.**
All final static/native facts below are supplied by **supervisor Codex's
independent review**, including pixels, operation receipts and complete stopped
archives; they are not this documentation author's native execution or owner
observation. No tests, gates or native calls were rerun for this docs update.

The broad primary native round applies to **GEN7 / `a92d17858b01dc6201a52ccfbd1f163f600acd78`**.
The final **GEN8 / `965ee470`** correction changes only two visibility attributes
in `resources/settings.xml`; Python, manifest, changelog and all other runtime
bytes are identical to GEN7. GEN8 has a focused **Omega settings-only retest**,
not a fresh full core cycle or four-version native pass on the final bytes.

Earlier blanket “all native BLOCKED/UNRUN” statements are superseded. The
[Lab394 activation blocker][lab394] is no longer the current blocker: deployed
Lab revision `3d1d459`, schema `0017`, was independently live-verified healthy.
That infrastructure observation does not qualify this add-on or authorize a new
runtime action. Mixed Program+service execution must still be observed, not
inferred from structural validation, enabled state or launch acknowledgement.

| Intended native target | Current bounded evidence / assessment for owner review |
| --- | --- |
| Matrix **19.4** ([#8][n8]) | Current candidate native **UNRUN**: no new Start/deploy. Experimental; historical SIGSEGV and ordinary-reopen exit remain deferred #8, not repaired by recovery. Static 19.5 is not native 19.4. |
| Nexus **20.5** ([#9][n9]) | GEN7 real guide/search/listing, LAN-video frame, ordinary Stop and close/reopen; strongest current core lane, not prolonged-stream/audio/timer acceptance. |
| Omega **21.3** ([#10][n10]) | GEN7 real guide/search/listing/background parse, with terminal unrequested exit and incomplete playback/reopen-after-pilot. GEN8 logo visibility retest passed with proper managed Stop. Bounded core/settings evidence, not resolution of the earlier exit. |
| Piers **22 RC2** ([#11][n11]) | GEN7 expired-fixture empty-state navigation and advancing local clip/Stop. Preview-bounded; no new populated programme/real-feed/timer acceptance. Earlier separate rapid-modal blank remains unproved and is not claimed fixed. |

These recommendations may support **core Alpha candidate owner review under a
limited scope**, not approved release support. The owner chooses support scope,
release version and publication separately. No target is silently removed.

### Primary native round — GEN7 applicability

- **Omega 21.3**, Debian `2:21.3+dfsg-1ubuntu1`: actual guide navigation,
  details/context, populated and empty title/channel search, populated
  selected-channel listing, safe Left/Back and ordinary guide close. Earlier
  supported same-profile Stop/Start rendered populated guide data. Fresh primary
  background update **01:01:17.733–01:01:18.526 UTC, 21 November 2026** mapped
  **246/246 feed IDs**: **244 XML channel icons / 0 database channel logos** with
  `xmltv.logos=false` and other logo sources off. The two missing Logos widgets
  were the visibility defect tracked in [#55](https://github.com/kcook98765/script.tvguide.fullscreen/issues/55)
  and corrected by [PR56](https://github.com/kcook98765/script.tvguide.fullscreen/pull/56),
  not a parser-false regression. Secondary VFS pilot
  was never saved or offset-parsed; the viewer disconnected during long text,
  followed by an unrequested native exit. No causal diagnosis, restart/crash
  investigation or final successful Stop is claimed for that terminal exit.
  Initial proper Stop and explicit resume have separate retained receipts.
  Primary playback and reopen-after-pilot remain incomplete; older evidence below
  remains historical. Full audit found critical config/core preferences unchanged,
  original **0 rules** retained, **247 channels / 2,180 programmes / 249 maps**;
  unsaved secondary/type/text did not persist.
- **Nexus 20.5**, Debian `2:20.5+dfsg-1ubuntu1`, `20240927-nogitfound`:
  populated real guide metadata/navigation/context/listing, positive/empty title
  search and safe Back, actual LAN-video frame followed by ordinary Stop to
  inactive playback/guide, and ordinary close/reopen. No audio, time-progression
  or prolonged-stream guarantee. Proper managed Stop confirmed. Fresh primary
  parse mapped **246/246 feed IDs**, **244 XML icons / 0 channel logos**;
  background update **02:16:02.245–02:16:02.753 UTC**. Original **0 rules**,
  config/core preferences preserved; **247 channels / 2,097 programmes / 249 maps**.
- **Piers 22 RC2**, build **21.90.902**, Git `20261109-d686683a-dirty`, Linux:
  retained fixture channels with expected empty current-date cells, usable empty
  programme context with intended disabled actions, empty channel listing/Back.
  One mapped local clip advanced **0s/frame 0 → 30s/frame 60**, then ordinary
  Stop to guide/inactive and proper managed Stop. Fixture was expired; no offset
  or cache reset/date hunt. All **3 fixture IDs** mapped; **4 channels / 24 fresh
  fixture programmes / 3 maps**. The original 27 → 24 cached programmes is a
  fresh fixture parse, not unchanged-cache evidence. Original **1 reminder +
  1 AutoPlay**, config/core preferences preserved; background update
  **02:31:25.034–02:31:25.255 UTC**. No new populated-programme, real-feed or timer
  qualification; separate earlier blank-modal behavior remains unresolved.
- **Matrix 19.4** was untouched: the independently final-archived **3,196-entry
  whole-profile inventory** exactly matches initial, retaining original
  **1 reminder + 1 AutoPlay** and source payload `1e7e5a16`. Historical guide,
  playback and timer observations are partial exact-source evidence, not a
  current-candidate native run. Only Matrix is current-native UNRUN, not all lanes.

For the three primary-tested versions, Codex independently matched **912 installed
runtime blobs and mode classes, no extras**, to GEN7 Git. Saved rules/config were
preserved, while search history and ordinary caches changed: no byte-identical
whole-profile claim applies to them. Complete current and old logs had no
`Traceback`, `PythonToCppException`, `UnboundLocalError` or fatal markers, but
caught missing-control/audio/environment errors remain. Current + old
**lines/errors**: Omega **23,930/15,739 + 732/304**; Nexus **5,022/3,142 +
731/297**; Piers **437/75 + 285/25**. No clean-log, blanket callback, audio or
all-recurrence acceptance follows. Nexus/Piers update times above are also
21 November UTC.

### Focused final settings retest — GEN8 Omega only

Phase5 [PR56](https://github.com/kcook98765/script.tvguide.fullscreen/pull/56)
fixes [NF1 #55](https://github.com/kcook98765/script.tvguide.fullscreen/issues/55).
The original XML had **14 assertion failures**; the corrected source passes
**4 methods / 24 widget-state expectations**. OpenCode's adjacent **39 methods plus
settings contract**, and Codex's independent **4 visibility + 6 parser methods plus
contract**, passed. Modeling documented C++ condition semantics is not native
execution.

The sole post-primary native correction round used Omega 21.3 and exact GEN8:
both XMLTV/add-on-folder Logos options appeared **OFF** with master **ON** and
External **None**; master **OFF** hid them; restoring **ON** showed both. Neither
option was touched; **Cancel** was clicked and the owned browser closed.
Structural validation passed. Capture `0bd46b4b-0dc9-446c-925c-a8cb1a762ffe`,
digest `9a59352ce91ae35cc7a8383131fd226ab3f55143be4190c10f1bf8e5e0b0f344`,
and managed Stop `1433b56a-8eb3-4523-87c1-c5432de47f08` were independently
audited; Stop confirmed and all four originals were stopped. Independent pixel
comparison and full stopped archive plus second read verified **912 runtime
blobs/modes exactly `965ee470`, no extras**; config/core preferences/rules exactly
match primary and initial, with only `last.background.update` changed.
Fresh data: **247 channels / 2,075 programmes / 249 maps**, **246/246 feed IDs**,
**0 logos / 244 XML icons** with the false flag. Actual background update:
**02:49:14.202–02:49:14.740 UTC, 21 November 2026**. Complete focused logs:
current **1,405 lines / 769 errors**, old **478 / 157**, no Python-exception/fatal
markers; not clean logs. The focused visibility defect in #55 is resolved with
Codex-accepted source and native audit evidence, not a new full core/native cycle.
Broader issues retain their exact scopes.

### Final static gate — exact frozen runtime

One final four-lane gate actually ran on `965ee470` and the runtime inventory
above. All six stages are accounted for: **syntax PASS, manifest PASS, paths
PASS, package PASS, types FAIL, official checker FAIL** in every lane.

| Final static lane | Kodistubs | Type errors | Checker errors / warnings | CLI / JSON exit |
| --- | --- | --- | --- | --- |
| Matrix **19.5** | **19.0.3** | **641** | **3 / 9** | **1 / 1** |
| Nexus **20.5** | **20.0.1** | **641** | **3 / 10** | **1 / 1** |
| Omega **21.3** | **21.0.0** | **641** | **3 / 10** | **1 / 1** |
| Piers **22 RC2** | **22.0.1rc1** | **615** | **3 / 10** | **1 / 1** |

Tool host: **CPython 3.12.3 / mypy 2.4.0 / addon-check 0.0.36**, not proof of
Kodi's embedded Python. Each intended lane used its explicit isolated interpreter;
`--branch` does not switch stubs. Matrix static **19.5 is not native 19.4**;
Piers is bounded exact RC2, not stable/full API qualification. Warnings and
negative-control diagnostics remain retained, not suppressed.

Against historical Task22 `84b171b` below, normalized typing comparison adds
**1 annotation diagnostic and removes 3 diagnostics (net −2)** per lane. The new
annotation diagnostic at `source.py:1054`, `programList`, belongs to
**`_channelSearch`**; that entire function's AST is identical to starting
`95c031`. No attributable runtime failure
or new code finding was established. Hundreds of unresolved diagnostics are
**not all false positives**; the typing debt remains unresolved.
Normalized checker errors/warnings are unchanged: Georgian, Haitian (Creole) and
Vietnamese variant identities still require owner/translator decisions. Preserve
**69 catalogs / 2,492 entries**, with no destructive locale guesses.

Two unnecessary NF1 source-worktree single-Omega validations also ran contrary
to scope. They failed packaging and inherited/test diagnostics and are retained
separately as a **workflow deviation**, not this runtime gate or qualification.
No new runs were made to prepare this documentation.

### Historical native provenance and limits

These are supervisor-independently-reviewed historical observations, not a new
run or a result for the merged five-fix Alpha batch:

- Native source **`1e7e5a1`** has actual fixture XMLTV/guide/mapped playback/Stop
  and background/timer evidence across all four targets, with the table's
  exceptions. Nexus reuses **`465cc55`** timer/background/player evidence and
  **`21d01fd`** GUI correction/native evidence; its `1e7e5a1` follow-up establishes
  **M3U/rule retention only**, not a fresh repeat of all prior criteria.
- Matrix's historical ordinary-reopen native exit and separate SIGSEGV evidence
  remain deferred in #8, without a shared causal diagnosis; recovery did not erase
  either observation.
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
backend recording. Omega's historical post-restart NOW reminder was **unobserved**,
not diagnosed as failed. Japanese/emoji glyph boxes and environmental audio/control
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
| Fullscreen/quick XMLTV EPG, mappings, lists/search, channel navigation and ordinary playback | Bounded GEN7 core evidence per lane above; only Omega settings retested on GEN8. OSD/PiP/next-up and latent VOD are not fully accepted; Matrix current-native unrun. | [Fixtures](native-fixtures.md); [GUI/API assessment][gui-audit] |
| XMLTV sources, offsets, logos and cache | Independent-offset, bool opt-in and URL-logo source regressions pass; fresh GEN7 Omega/Nexus parse confirms false means no database logos. GEN8 Omega accepts visibility of both options. Secondary offset pilot was unsaved/unparsed; URL construction is not image reachability/rendering proof. Cache-setting invalidation tied to destructive channel refresh remains preservation-sensitive and deferred. | [Offsets](xmltv-source-offsets.md); [settings/logo notes](dependencies-settings.md#alpha-a2-xmltv-logo-opt-in) |
| Internal title/synopsis/category/channel search and saved searches | GEN7 Omega/Nexus populated/empty search and listing observations above, plus focused window/source regressions; not every search mode or catchup provider accepted. LIKE wildcards/cross-channel search remain intentional. | [Alpha repairs below](#reviewed-alpha-source-repairs); [fixtures](native-fixtures.md) |
| Reminders and ordinary AutoPlay | Safe text/data, source/channel event ownership and reconstruction retained; historical timer/background evidence is partial, not every phase. Old collisions, unclicked recurrence horizons and in-flight delivery/playback limits remain deferred. | [Reminders](modernization-reminders.md), [AutoPlay](autoplay-data.md), [ownership](schedule-ownership.md) |
| Recording / legacy external AutoPlayWith | **Partial PVR replacement**: existing capable backend/client required; no arbitrary-stream/FFmpeg capture, full old recurrence/padding/markers or legacy-row migration. | [PVR prerequisites/limits](recording-pvr.md) |
| External-player choice | **Provisionally disabled** pending platform/configuration/receiver/stop qualification; source presence/JSON is not safe execution proof. | [Research][external-audit] |
| Default/Dark/CatBar and custom appearance | Bundles retained; **partial passive layout/PNG customization**. Complex includes/resources and WMC/WhiteSnow compatibility unresolved. | [Passive skin subset](custom-guide-skins.md) |
| ExtendedInfo / MySearch / iSearch external lookup | **Optional TMDbHelper movie/TV handoff**, requiring an installed/enabled compatible official provider and its setup; not full legacy lookup, episode/ID matching or guide metadata injection. Provider results/return still need feature acceptance. | [Metadata lookup](metadata-search.md) |
| Artwork and image matches | Bounded JSON persistence replaces pickle, **without migration**. Last-writer-wins/interprocess and legacy lookup-service health limits remain; blank-logo PNG repair retained. | [Image cache](image-match-cache.md); [PR30](https://github.com/kcook98765/script.tvguide.fullscreen/pull/30) |
| Media/plugin mappings, alternates, ini/M3U/TSV/subscriptions and catchup | Ordinary paths retained; **partial typed stream/folder dispatch**. `@` RunPlugin-equivalent actions remain blocked; scheduled AutoPlay is media-only. Receiver/provider and catchup parity unqualified. | [Mapping contract](typed-playback-mappings.md) |
| Key editor and action bar/MINE | Key editor retained; **closed action catalog** supports hide/order/label/image, not arbitrary builtins, MINE templates or downloaded Python. | [Action bar](action-bar.md) |
| Settings, providers, logos/backgrounds, VPN and backup/import/export/reset | GEN7 preservation audits plus GEN8 Omega Cancel/visibility retest; not universal provider health, migrations or all settings persistence acceptance. TLS verification retained; no secret logging/downloaded-code restoration. | [Dependencies/settings](dependencies-settings.md) |
| Background updates/autostart | Both original script/service responsibilities and background consent retained; actual fresh GEN7 Omega/Nexus/Piers and focused GEN8 Omega updates audited above. Recovery/race/restart acceptance remains incomplete. | [Service safety](service-safety.md) |
| Package/artwork/translations | Manifest **0.0.445**, Program+service, GPL/upstream credits, assets and **69 catalogs / 2,492 entries** preserved. Three locale identity/variant problems unresolved. | [Package notes](package-metadata.md) |
| Permanent removals | Only downloaded-code/arbitrary-command mechanisms are approved removed. Other feature gaps remain restoration work or require an owner decision. | [Safety](modernization-safety.md); [preservation #14][preservation] |

### Reviewed Alpha source repairs

All five PRs were independently accepted and normally merged. These are focused
source results, distinct from the exact-source native observations above; no new
official add-on or integration was installed. Core guide/search requires none;
existing optional TMDbHelper lookup and backend-dependent PVR remain partial
replacements, not mandatory new optional dependencies:

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

The integrated primary GEN7 regression result was **19 scripts, 94 unittest
methods + 4 assertion scripts ALL PASS**. The original failure proofs above and
Phase5's separate XML visibility proof remain distinct from that integrated run.

The bounded adjacent review established no further small empty-selection or
scheduler [#21](https://github.com/kcook98765/script.tvguide.fullscreen/issues/21)
defect. The documented scheduler limitations remain unresolved.
[Owner #54](https://github.com/kcook98765/script.tvguide.fullscreen/issues/54) is
**owner-approved small cleanup for the next batch**, explicitly deferred by the
freeze rule—not a blocker or a new integration. No work on pytz is included.
Large gaps remain: FFmpeg/arbitrary capture, external AutoPlayWith/player,
complex skins/providers/migrations, old scheduler collision/horizon/in-flight
behavior and preservation-sensitive cache invalidation. There is no full-parity
claim, unsafe downloaded code/raw-command restoration or permanent additional
feature deletion.

[Initial docs PR53](https://github.com/kcook98765/script.tvguide.fullscreen/pull/53)
already finalized the [changelog](../changelog.txt): its **26,296 historical bytes
plus 3,252-byte Unreleased prefix** remain untouched. This final qualification update
is README/docs only; no runtime/test/manifest/GPL/translation/asset/dependency or
version changes, release ZIP, repository package, tag or publication. Older
exact-source reports, their failed results and historical header notices are
retained rather than rewritten as passes.

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
