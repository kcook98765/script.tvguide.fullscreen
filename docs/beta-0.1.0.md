# TV Guide Fullscreen 0.1.0 Beta — preparation and release notes

## Status and scope

**Owner-approved release PREPARATION ONLY. Beta is not yet downloadable or in
kcook-lab-repo.** Numeric Kodi manifest version: `0.1.0`. Proposed GitHub tag:
`v0.1.0-beta`, to be marked **prerelease** only after separately authorized
publication. Proposed installer: `script.tvguide.fullscreen-0.1.0.zip` with
`SHA256SUMS`. These are proposed names, not live tag/download URLs.

Use the existing [fork Releases index](https://github.com/kcook98765/script.tvguide.fullscreen/releases)
for actual availability. The [README's two installation methods](../README.md#installation--two-proposed-methods-after-publication)
cover the proposed recommended repository route and alternative Release ZIP.
The repository source page currently offers `repository.ai.kodi-0.1.1.zip`;
the current installer should be selected from that page at installation time.
TV Guide's **Program add-ons** category follows its script/executable manifest,
not a tested repository listing. Admission/availability for each lane is unknown.
The bounded beta recommendation is **Nexus 20.5**; Matrix/Omega/Piers current beta
lane admission is unapproved and their evidence is historical only. Neither
functional evidence nor admission supplies provider/content rights.

This campaign changes only version/summary/description/news/website, changelog,
release-facing documentation and necessary package-test assertions. No runtime
behavior edits, dependency changes, native runs, publication, tags or releases.
The original `primaeval` provider, contributors, GPL notices, `addon.py` Program
and `service.py` background entry points remain intact. All six required official
dependency declarations (including pytz `2023.3.0+matrix.1`), all five screenshot
PNGs and all 69 catalogs are preserved. No pytz vendor tree or VPN API is bundled.

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

Only unchanged behavior reuses this evidence. The new beta changes manifest and
changelog bytes and has a new private artifact identity: **no exact 0.1.0 ZIP
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

The inherited integrated gate remains **FAIL**. Latest saved types-only counts:
Matrix/Nexus/Omega **605 each**, Piers **578**. Three locale errors per lane remain;
translations are not removed or relabeled to suppress them. Earlier warnings,
negative-control diagnostics and dated failures remain historical evidence.
No full static gate or four-lane rerun is authorized in preparation; none is claimed.

Preparation runs only existing `check_package_metadata.py`,
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
mappings and rules; use normal in-place update only after actual availability.
No Kodi Reset is required. Alpha 1 auto-update, migration and obsolete-file
pruning are unverified; no native upgrade test is claimed. Repository lane
admission remains a separate decision, not something a source PR supplies.

The [published Alpha 1 instructions](alpha-installation.md) preserve its immutable
tag, installer, hash and dated qualification. This preparation does not alter it.
Private candidate packaging uses exactly one `script.tvguide.fullscreen/` root,
the reviewed 321-file allowlist, sorted fixed-1980 Unix regular-0644 entries and
deflate level 9. It excludes docs/tests/tools/configuration/Git/logs, VPN API and
bundled pytz. Two Git-blob builds must be byte-identical, with commit/tree,
per-file hashes, source archive and installer SHA-256 retained privately.

Independent exact-candidate review is required next. No installer upload, tag,
release (including draft), repository/Pages change, merge or publication is part
of this campaign. Source attribution and [GPL v2-or-later notices](../LICENSE.txt)
remain; see [README attribution](../README.md#feedback-attribution-and-license).
