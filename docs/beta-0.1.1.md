# TV Guide Fullscreen 0.1.1 Beta

**Published prerelease:** [v0.1.1-beta](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.1.1-beta),
numeric manifest version `0.1.1`. Also live in **kcook-lab-repo's Nexus and Omega catalogs**.
Historical public [0.1.0 Beta](beta-0.1.0.md) and [Alpha 1](alpha-installation.md), installers,
tags and evidence are unchanged. Publication followed independent review and
explicit owner approval; preparation alone did not authorize it.

The annotated tag points to reviewed source
`f936c0a514e0de126e62e24fd3d24b66b0c74097`, tree
`c6d014c332f6d24b219f4976518dcf2221ae6a88`, also the source PR #75 merge tree.
This out-of-package documentation update does not rebuild the installer or retarget
the tag. All 318 packaged payloads, including all 45 Python files, remain unchanged.

## Artwork-only successor; runtime unchanged

- Replace root `icon.png` (512×512 opaque RGB PNG) and `fanart.jpg` (1920×1080
  RGB JPEG) with original geometric TV/guide artwork. Names/dimensions remain.
- Omit exactly `resources/screenshots/fullscreen-guide.png`,
  `resources/screenshots/programme-actions.png`, `resources/screenshots/on-now.png`
  and `resources/screenshots/search-results.png` from source, installer, manifest
  and the README current screenshot list. Native recapture would require
  unnecessary runtime setup for promotional material; omission is the selected
  fallback. No replacement/simulated Kodi captures are made.
- Retain `resources/screenshots/channel-management.png` exact bytes: owner-authored
  capture of ordinary labels/UI, with no separately identified artwork blocker
  in Codex's visual review. See [asset-by-asset basis and hashes](artwork-provenance.md).
- All 45 runtime Python files and every other resource are byte-identical to
  published source `c19f256333efbe7af12418312f17e00f99792dc2`. Channel mappings,
  scheduling and extension behavior are untouched. All six dependency imports,
  including pytz `2023.3.0+matrix.1`, Program/executable + service, platform and
  language declarations remain. GPL/credits, `LICENSE.txt`, complete OrderedDict
  MIT notice in `THIRD-PARTY-NOTICES.txt` and embedded pyaes MIT remain verbatim.

## Evidence scope (reused, not rerun)

Nexus **20.5** accepted functional code is
`cc411d933a269d4cba080a3bdf646b5eddc71e22`: bounded clean GUI ZIP/dependency
installation, direct/plugin moving frames, explicit alternative/automatic fallback,
Stop, Reminder/AutoPlay create/selective cancellation, reminder restart persistence,
service startup and graceful exit observations. This unchanged-code evidence is
reused; there is **no new 0.1.1 Nexus native, upgrade or repository UI acceptance**.

Codex's existing exact-package **Matrix 19.4 / Omega 21.3** core smoke is also
reused, not rerun for this documentation. The finite Linux Matrix scope includes
clean native GUI installation with official dependencies, populated guide/navigation,
moving owned local video, Stop/guide return, close/reopen, actual background update
and normal exit 0. It does not qualify audio, optional integrations, upgrades or
repository UI, nor replace the broader Nexus feature evidence. See the
[current scope and retained history](release-history.md#existing-current-package-matrixomega-smoke--reused).

**Audio UNTESTED**. Optional timed notification and actual timer-fired AutoPlay
**UNOBSERVED**. Logs remain **non-clean**; fallback can retain the original failure
dialog. Inherited integrated static **FAIL** counts **605/605/605/578**
(Matrix/Nexus/Omega/Piers), and three locale errors per lane, remain historical.
All six integrated stages (syntax, manifest, paths, package, types, official
checker) are **NOT RERUN**. Focused metadata/license/asset/dependency/settings
checks and deterministic package audits are not that gate. Matrix native 19.4 is
distinct from static 19.5. The owner reports repeated older-version crashes across
devices and accepts that historical risk. Codex's new reassessment corrects the
earlier current-blocker inference: history/shared runtime alone did not establish
a current 0.1.1 failure. No root cause or fix is claimed; old records remain intact.
See [historical crash context](release-history.md#historical-crashes-and-current-scope).
Piers 22.0 RC2 remains historical preview evidence with foreground/input limits
and plugin EOF uncertainty. No all-platform claim or new feature parity.

## Published installer and installation

The deterministic installer has **318 files**: 0.1.0's published 322 minus four omitted
screenshots; four changed payloads (manifest, changelog, icon, fanart), 314 unchanged.
Docs/tests/generator/config/evidence are excluded. Two complete builds from exact
final committed Git blobs, per-file inventory, SHA256SUMS, source archive/bundle
and commit/tree are retained in private campaign evidence, not recursively in the
installer. No installer hash is inserted into its own payload.

The public [installer ZIP](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.1.1-beta/script.tvguide.fullscreen-0.1.1.zip)
is **1,318,170 bytes**, SHA-256
`76533fcb570cd813e2deb885c919b59eea21171c6ce344d5a40ef5d8fba287b9`.
Its [SHA256SUMS](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.1.1-beta/SHA256SUMS)
passed GNU strict checksum verification after anonymous download. The published
Nexus and Omega catalogs list TV Guide Fullscreen `0.1.1`; both reference the
byte-identical GitHub installer, with valid catalog/package SHA-256 sidecars.
Codex's supplied publication verification records the promoted 46-file site and
anonymous HTTP checks; these were not rerun here. Matrix is being prepared/reviewed
but is **not published** and needs separate new-site approval; Piers is excluded.

See [README installation](../README.md#installation) for **both live routes**:
recommended Nexus 20.x / Omega 21.x installation through kcook-lab-repo, or direct GitHub
Releases ZIP plus `sha256sum --check --strict SHA256SUMS`, requiring
`script.tvguide.fullscreen-0.1.1.zip: OK` before Kodi's Install from zip file.
The repository source is `https://kcook98765.github.io/kcook-lab-repo/`;
its current `repository.ai.kodi-0.1.1.zip` installs the repository, not TV Guide.
Then choose **Install from repository → kcook-lab-repo → Program add-ons →
TV Guide Fullscreen 0.1.1**. Do not use source archive ZIPs as installers; follow
Kodi's standard Unknown sources consent and administrator policy.
Back up profile/settings/maps/rules. In-place update is
intended, but upgrade/migration/obsolete-file pruning (including old screenshots)
and automatic ZIP-origin updates are **unverified**. No Reset required.

Publication URL/metadata checks are not native installation, repository UI,
playback or audio acceptance. No new runtime testing was performed for this
documentation update; existing finite Linux Matrix 19.4/Omega 21.3 core smoke and
broader Nexus 20.5 evidence above are reused, not a fresh four-version qualification.

The [bundled-asset provenance](artwork-provenance.md) records specific
redistribution bases, not blanket rights certification or external provider/feed
permission. Historical preparation and package audits remain evidence of their
original scope, not broader beta qualification.
