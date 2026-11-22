# TV Guide Fullscreen 0.1.1 Beta candidate

Prepared locally for Codex independent review, **NOT published**. Numeric manifest
version `0.1.1`; proposed tag `v0.1.1-beta` is not created. Historical public
[0.1.0 Beta](beta-0.1.0.md) and [Alpha 1](alpha-installation.md), installers,
tags and evidence are unchanged. No release, repository or Pages action follows
automatically from preparation.

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
reused; there is **no new 0.1.1 native, upgrade or repository UI acceptance**.

**Audio UNTESTED**. Optional timed notification and actual timer-fired AutoPlay
**UNOBSERVED**. Logs remain **non-clean**; fallback can retain the original failure
dialog. Inherited integrated static **FAIL** counts **605/605/605/578**
(Matrix/Nexus/Omega/Piers), and three locale errors per lane, remain historical.
All six integrated stages (syntax, manifest, paths, package, types, official
checker) are **NOT RERUN**. Focused metadata/license/asset/dependency/settings
checks and deterministic package audits are not that gate. Other beta lanes
remain deferred: Matrix native 19.4 crash unresolved (static 19.5 is distinct),
Omega 21.3 historical, Piers 22.0 RC2 historical preview with foreground/input
limits and plugin EOF uncertainty. No all-platform claim or new feature parity.

## Review and installation plan

The deterministic installer has **318 files**: published 322 minus four omitted
screenshots; four changed payloads (manifest, changelog, icon, fanart), 314 unchanged.
Docs/tests/generator/config/evidence are excluded. Two complete builds from exact
final committed Git blobs, per-file inventory, SHA256SUMS, source archive/bundle
and commit/tree are retained in private campaign evidence, not recursively in the
installer. No installer hash is inserted into its own payload.

See [README installation](../README.md#installation) for **both future routes**:
approved Nexus-only kcook-lab-repo publication, or direct GitHub Releases ZIP plus
`sha256sum --check --strict SHA256SUMS` once released. Neither is a live 0.1.1
download/catalog claim. Back up profile/settings/maps/rules. In-place update is
intended, but upgrade/migration/obsolete-file pruning (including old screenshots)
and automatic ZIP-origin updates are **unverified**. No Reset required.

This correction records specific redistribution bases, not automatic blanket
rights certification, provider/content permission, repository admission or a new
owner decision. Final release/repository publication requires separate owner approval.
