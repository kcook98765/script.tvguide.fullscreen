# TV Guide Fullscreen 0.1.0 Beta — release notes and preparation history

## Status and scope

**Available directly from GitHub as a prerelease; NOT listed or installable through
kcook-lab-repo.** Numeric Kodi manifest version: `0.1.0`. Open the
[v0.1.0-beta release](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.1.0-beta),
download the [installer ZIP](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.1.0-beta/script.tvguide.fullscreen-0.1.0.zip)
and [SHA256SUMS](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.1.0-beta/SHA256SUMS),
then follow [Installation](../README.md#installation): verify the checksum, back
up profile/settings/maps/rules, and use Kodi **Install from zip file**, without Reset.
Other versions remain in the [fork Releases index](https://github.com/kcook98765/script.tvguide.fullscreen/releases).

The existing [repository source page](https://kcook98765.github.io/kcook-lab-repo/)
offers [repository.ai.kodi-0.1.1.zip](https://kcook98765.github.io/kcook-lab-repo/repository.ai.kodi-0.1.1.zip),
which installs the **existing repository only**, not TV Guide beta.
**Install from repository → kcook-lab-repo → Program
add-ons → TV Guide Fullscreen** remains pending genuine admission and listing.
Existing repository controls require a verified redistribution basis for all
bundled material. The inherited artwork and screenshots remain **unverified**;
owner acknowledgement does not satisfy this requirement, so repository admission
remains blocked. The owner explicitly accepts this uncertainty for the one-time
source GitHub beta, not as third-party permission or legal clearance. The full
MIT notice gap is corrected, but broad artwork rights are not cleared. Repository
safeguards remain enforced; this source release supplies no repository admission
or Pages promotion.

The bounded beta recommendation is **Nexus 20.5**; Matrix/Omega/Piers beta acceptance
is deferred and their evidence is historical only. Neither functional evidence nor
source publication supplies provider/content rights.

The release uses the existing frozen reviewed ZIP, not an installer rebuild:
**2,137,274 bytes, 322 files**, SHA-256
`da5f38eed4707aa6de9ac7d9648008565ac332f51e93dc6cc5dab6f11f00f82e`.
Source/tag target: `c19f256333efbe7af12418312f17e00f99792dc2`, tree
`b51337779aa4a07dec43ac74530d95954ea5f16c`, also the tree of merged source main
`09eb7256a51b4baf1d07122dc96d21d85ad494cb` (PRs #72 and #73).
These later README/beta-document updates are outside the installer; they do not
retag or rebuild it. No exact-beta-ZIP native install or upgrade is newly claimed.

## Original preparation — 2026-11-21 history

The original preparation changed only version/summary/description/news/website, changelog,
release-facing documentation and necessary package-test assertions. No runtime
behavior edits, dependency changes, native runs, publication, tags or releases.
The original `primaeval` provider, contributors, GPL notices, `addon.py` Program
and `service.py` background entry points remain intact. All six required official
dependency declarations (including pytz `2023.3.0+matrix.1`), all five screenshot
PNGs and all 69 catalogs are preserved. No pytz vendor tree or VPN API is bundled.

## Notice-only successor

**2026-11-21 history:** this review followed the original private preparation and
preceded the separately authorized source prerelease described above.

The original **unpublished private** candidate from source
`42997e3c80784262be4e35c8d37e772c62bc5d6f`, tree
`d92962e7fbdc5475860976ab7dec64fc856d8f57`, is retained byte-for-byte:
`script.tvguide.fullscreen-0.1.0.zip`, 2,136,204 bytes, SHA-256
`0b25379c9eb71bd6e9014704114e5b3a7104c6fbbd9e209a97f5e189f7464492`.
Its 321 members lacked the Raymond Hettinger copyright and full MIT notice for
the OrderedDict backport attributed in `streaming.py` to ActiveState recipe 576693.

This owner-authorized successor superseded that candidate **for review**, adding
only the distributable root [THIRD-PARTY-NOTICES.txt](../THIRD-PARTY-NOTICES.txt)
to the installer (322 files). Its copyright **2011 Raymond Hettinger** and complete
MIT permission, condition and disclaimer were independently checked against the
pinned primary license URL and SHA-256 recorded in that notice. All 321 previous
payloads, including all 45 runtime Python files, manifest, dependencies, Program
and service entry points, resources, screenshots and catalogs, remain byte-identical.
GPLv2 / GPLv2-or-later notices and the separate Marti Raudsepp 2010 full MIT notice
in `pyaes.py` are unchanged. No changelog or manifest change is needed for this
notice correction. Same numeric `0.1.0` is explicitly authorized because the
original candidate is unpublished; no existing release is modified.

Measured successor `script.tvguide.fullscreen-0.1.0.zip`: **2,137,274 bytes**,
SHA-256 `da5f38eed4707aa6de9ac7d9648008565ac332f51e93dc6cc5dab6f11f00f82e`.
Two complete Git-blob builds are byte-identical. This subsequent documentation-only
hash disclosure does not change the payload; separate final source-binding evidence
verifies every one of the 322 ZIP members against the final source Git blobs.

At that checkpoint, only this disclosure, the README, the notice and a focused
preservation test were source changes. Original private preparation reports/artifacts
remain immutable;
separate successor command receipts, per-file inventory, deterministic Git-blob
builds and exact source binding are retained privately. The successor review ran only
the existing three focused checks plus license/payload preservation and negative
controls, using the recorded Omega tooling interpreter identity, not a native
Omega qualification or a full static gate. All runtime/evidence limits below
remain unchanged: audio **UNTESTED**, timed reminder delivery and actual AutoPlay
firing **UNOBSERVED**, non-clean logs, inherited integrated static **FAIL** and
historical Matrix/Omega/Piers RC2 lanes only. There is no new-beta native install
or upgrade claim. No rights approval was supplied; artwork/screenshots provenance,
repository admission and publication were pending at that review checkpoint.
Exact successor review was required before its push/PR. Subsequent source merges
and the direct prerelease do not clear rights or unblock repository admission;
no distribution repository change is made here.

## What's in this modernization Beta

This groups already merged work; none is newly implemented by preparation:

- Python 3 / modern Kodi API groundwork; safer command/data handling, preserved
  Program and background-service responsibilities and startup safety.
- Fullscreen/Quick guide navigation, programme details and search corrections;
  XMLTV offsets/logo handling, unusable programme-row handling and absent-only
  display-name fallback. Source-aware cache and additive M3U preservation remain.
- Punctuation-safe reminders and ordinary AutoPlay; event/source/channel identities,
  padding correction, authoritative current-popup dispatch, wildcard Cancel and
  selective once-rule cancellation. No new recurrence or timer-delivery guarantee.
- Existing safe JSON image matches, passive custom styling, action customization,
  typed playback mappings and optional TMDbHelper/PVR handoffs, with their own
  prerequisites and limits. See the [feature inventory](modernization-status.md#feature-inventory).
- Intentional [VPN Manager removal](vpn-manager-removal.md): connectivity must be
  managed independently; stale saved VPN values are ignored and not erased.
  Existing Kodi Player/PVR actions remain, not named external-player restoration.

## Accepted evidence reused, not rerun

The owner accepted an independently executed private disposable **Nexus 20.5**
campaign against exact source `cc411d933a269d4cba080a3bdf646b5eddc71e22`, tree
`36cfc23841bfc7fa671db31f480a9050c3003f3b`, and a **321-file** private ZIP with
SHA-256 `95995ad4706c4aa9a65c4fa93c39ec9bad3b82135778074cb41e11bf792b65db`.

Accepted core observations: clean GUI ZIP installation and official dependency
resolution; direct/plugin moving frames (including reused exact-source evidence);
explicit alternative and automatic fallback playback; Stop; Reminder/AutoPlay
create and selective cancel preserving unrelated rules; saved reminder persistence
across restart; actual service startup work; graceful exits status 0.

Only unchanged behavior reuses this evidence. The beta changes manifest and
changelog bytes and has a different artifact identity: **no exact 0.1.0 ZIP
native installation or Alpha-to-beta upgrade was performed**. Original profiles
are untouched by preparation. This is not a fresh four-version beta native PASS.
Unchanged-code functional evidence plus independent metadata/package-delta review
is legitimate scoped reuse; the absence of a new ZIP native run is disclosed,
not an automatic requirement to repeat the accepted campaign.

| Lane | Scope and unresolved limits |
| --- | --- |
| Nexus 20.5 | Current accepted bounded core source evidence above; not exhaustive feature, device or long-running-stream acceptance. |
| Matrix | Historical native **19.4**, distinct from static **19.5**. Historical crash unresolved; not rerun for beta. |
| Omega 21.3 | Historical bounded native evidence, not a new beta install or present full-stream/audio PASS. |
| Piers 22.0 RC2 | Historical exact preview, not final Kodi 22 support. Foreground/input limitations and plugin EOF uncertainty remain; not retried. |

No all-platform qualification follows from the manifest's inherited `all` value.
Audio is **UNTESTED**, an owner-accepted beta limitation: the campaign used
video-only clips. Optional timed reminder delivery is **UNOBSERVED**, and actual
AutoPlay firing was not observed. Prior callback evidence has only its historical
scope. Fallback retains the original Kodi failure dialog even when an alternative
plays. Logs are **non-clean**, including caught controls/audio warnings; errors
are not all declared harmless. Complex skins, old providers/catchup/recording,
external-player parity, scheduler collisions/horizons/in-flight cancellation and
settings-refresh design remain limited. No speculative fixes are included.

## Static/focused scope

**Preparation history, 2026-11-21; not rerun for these documentation updates.**

The inherited integrated gate remains **FAIL**. Latest saved types-only counts:
Matrix/Nexus/Omega **605 each**, Piers **578**. Three locale errors per lane remain;
translations are not removed or relabeled to suppress them. Earlier warnings,
negative-control diagnostics and dated failures remain historical evidence.
No full static gate or four-lane rerun is authorized in preparation; none is claimed.

Preparation ran only existing `check_package_metadata.py`,
`check_dependencies_settings.py` and `check_vpn_removal.py` using the installed
isolated Omega tooling interpreter, with `stub-lanes` recorded. Package tests
cover five methods including all 69 catalogs, original artwork semantics and
data-loss/escape controls; dependencies/settings includes baseline negative
diagnostics; VPN checks use inert I/O, not native Kodi. Their actual command/exit
receipts and outputs are retained privately, separately from historical results.
No fresh official-checker PASS is implied by focused metadata checks. All six
integrated stages are **NOT RERUN**: syntax, manifest, paths, package, types and
official checker. The separate deterministic ZIP audit is packaging-only.

Preparation's focused baseline and final checks both returned actual exit 0:

| Check | Result |
| --- | --- |
| Package metadata | 5 unittest methods PASS, all 69 catalogs and data-loss/escape controls retained |
| Dependencies/settings | Assertion script PASS, baseline default/routing and literal-index negative diagnostics plus existing invalid-escape SyntaxWarnings retained |
| VPN removal | 8 unittest methods PASS with inert I/O; existing invalid-escape SyntaxWarning/DeprecationWarning diagnostics retained |
| Tool identity | CPython 3.12.3/Linux, Kodistubs 21.0.0, mypy 2.4.0, checker 0.0.36; Omega tooling lane only |

Tool versions/readiness are not an executed gate or native qualification. No
checker branch was selected, no stubs switched and no dependencies installed.

## Update and release safeguards

`0.1.0` sorts above manifest `0.0.446~alpha1`. Back up the profile, settings,
mappings and rules before using Kodi's normal in-place ZIP update. No Kodi Reset
is required. Actual Alpha-to-beta upgrade, migration, obsolete-file pruning and
ZIP-installed automatic updates are unverified; no native upgrade test is claimed.
Repository admission remains blocked as described above, not supplied by a source PR.

The [published Alpha 1 instructions](alpha-installation.md) preserve its immutable
tag, installer, hash and dated qualification. Neither this beta nor these docs alter it.

**2026-11-21 packaging/review history:** private candidate packaging used exactly
one `script.tvguide.fullscreen/` root,
the reviewed 321-file original allowlist plus the successor's one root notice
(322 files), sorted fixed-1980 Unix regular-0644 entries and
deflate level 9. It excludes docs/tests/tools/configuration/Git/logs, VPN API and
bundled pytz. The two Git-blob builds were byte-identical, with commit/tree,
per-file hashes, source archive and installer SHA-256 retained privately.

Independent exact-candidate review was required next at that preparation
checkpoint. Installer upload, tags, releases (including drafts), repository/Pages
changes, merges and publication were outside that preparation campaign. The later
one-time direct source prerelease does not promote TV Guide into the repository;
these documentation-only updates do not modify its assets. Source attribution and
[GPL v2-or-later notices](../LICENSE.txt)
remain; see [README attribution](../README.md#feedback-attribution-and-license).
