# TV Guide Fullscreen — 0.1.0 Beta preparation

A fullscreen XMLTV programme guide for Kodi: browse what's on, map channels to
streams, search listings, and set reminders or ordinary AutoPlay. This is the
**maintained modernization fork** of primaeval's TV Guide Fullscreen, preserving
its Program add-on and background service. It supplies no TV subscriptions or feeds.

**Beta preparation only: 0.1.0 is NOT currently downloadable or in the repository.**
The owner approved preparation using independently accepted, bounded Nexus 20.5
core evidence for unchanged code. This is not stable/full legacy parity, a clean
static gate, or current four-version beta native qualification. See
[Beta scope, evidence and release notes](docs/beta-0.1.0.md).
The bounded beta recommendation is **Nexus 20.5**; current beta lane admission
for Matrix/Omega/Piers is unapproved, with historical evidence only, not fresh
beta PASS. This scope decision supplies neither content rights nor repository admission.

**Notice-only successor for review:** the original unpublished private 0.1.0 ZIP
is retained historically at SHA-256
`0b25379c9eb71bd6e9014704114e5b3a7104c6fbbd9e209a97f5e189f7464492`.
This successor supersedes it for review by adding the missing OrderedDict
backport MIT notice in [THIRD-PARTY-NOTICES.txt](THIRD-PARTY-NOTICES.txt).
Measured successor `script.tvguide.fullscreen-0.1.0.zip`: **2,137,274 bytes**,
SHA-256 `da5f38eed4707aa6de9ac7d9648008565ac332f51e93dc6cc5dab6f11f00f82e`.
All 321 original payloads, including all 45 runtime Python files, are unchanged;
the notice is the sole added installer member. The owner authorized the same
numeric `0.1.0` only because the retained original is unpublished. Runtime and
qualification limits below are unchanged; no rights approval is supplied,
artwork/screenshots provenance remains pending, and repository admission and
publication remain pending. See the [successor disclosure](docs/beta-0.1.0.md#notice-only-successor).

## Installation — two proposed methods after publication

Neither path below currently supplies TV Guide Fullscreen 0.1.0. Repository
availability and Kodi-lane admission remain pending. The existing
[fork Releases page](https://github.com/kcook98765/script.tvguide.fullscreen/releases)
is the place to check for an actual announcement; do not use source-snapshot ZIPs
as installers.

### Recommended, proposed: kcook-lab-repo

**After TV Guide is actually published and admitted to your Kodi lane:**

1. Add `https://kcook98765.github.io/kcook-lab-repo/` in Kodi **File manager → Add
   source**, naming it `kcook-lab-repo`.
2. Use **Add-ons → Install from zip file** to select the current `repository.ai.kodi`
   installer ZIP shown at that source. The [existing source page](https://kcook98765.github.io/kcook-lab-repo/)
   currently lists `repository.ai.kodi-0.1.1.zip`; use the current listing rather
   than assuming that filename will never change. If prompted, explicitly consent
   to Kodi's standard **Unknown sources** setting for this trusted ZIP source.
3. Open **Install from repository → kcook-lab-repo**.
4. Open **Program add-ons → TV Guide Fullscreen**, **only once it is listed and
   admitted for your Kodi lane**.
5. Install normally and receive future repository updates according to your
   **Kodi update and origin settings**. This does not establish auto-update or
   migration for a preexisting ZIP-installed Alpha 1; see the limitations below.

### Alternative, proposed: beta GitHub Release installer ZIP

After publication, use this fork's [Releases page](https://github.com/kcook98765/script.tvguide.fullscreen/releases)
to find the proposed **prerelease** tag `v0.1.0-beta`, installer
`script.tvguide.fullscreen-0.1.0.zip` and matching `SHA256SUMS`. These are proposed
names, not live beta download links. Save both assets together, keep the ZIP's
published filename, and run `sha256sum -c SHA256SUMS`; require
`script.tvguide.fullscreen-0.1.0.zip: OK`. Then use Kodi **Add-ons → Install from
zip file**. If verification fails, do not install. Ask your Kodi administrator
if supported source installation is unavailable; do not bypass policy. If
prompted, explicitly consent to Kodi's standard **Unknown sources** setting for
this trusted ZIP source.

### Updating and first use

Back up your **Kodi profile, TV Guide settings, channel/stream mappings and saved
reminder/AutoPlay rules** first; prefer a separate test profile. Numeric manifest
version **`0.1.0` sorts above `0.0.446~alpha1`**. A normal in-place update is the
intended route **after actual availability**; no Kodi profile Reset is required.
Alpha 1 automatic update, migration and obsolete-file pruning have **not** been
verified. No native upgrade test was performed for this beta; original profiles
were untouched by preparation. A repository install does not itself guarantee an
existing ZIP install will auto-update.

Keep the official Kodi repository enabled for required dependencies. Configure
a current **XMLTV file/URL** and matching **M3U stream mappings** in TV Guide's
settings; use only sources you are entitled to access. Allow the initial import
to finish. Launch through **My add-ons → Program add-ons → TV Guide Fullscreen →
Info → Run**. Keep the background service with explicit consent; do not execute
`service.py` manually. Ordinary **Stop** returns from playback to the guide.
Changing an XMLTV offset alone may reuse cached programmes: see the
[offset/refresh cautions](docs/xmltv-source-offsets.md) before forcing a refresh
that could affect channel-associated rules.

## Required dependencies

All six manifest declarations remain required, not bundled optional extras:

| Dependency | Minimum version |
| --- | --- |
| `xbmc.python` (provided by Kodi) | `3.0.0` |
| `script.module.requests` | `2.31.0` |
| `script.module.dateutil` | `2.8.2` |
| `script.module.pytz` | `2023.3.0+matrix.1` |
| `script.module.pil` | `5.1.0` |
| `script.module.beautifulsoup4` | `4.12.2` |

Kodi must install/enable suitable official modules; a listing in a catalog is not
installed-state proof. [Official pytz](docs/official-pytz.md) replaces the removed
vendor copy. **No bundled pytz or VPN Manager integration.** Manage VPN connectivity
independently through Kodi, the OS or your network; stale VPN settings are ignored
and untouched. This is not a VPN-security guarantee. See
[VPN removal scope](docs/vpn-manager-removal.md).

## Features and optional integrations

- Fullscreen/Quick guide, programme details, On Now, title/channel search and channel
  management; primary, alternative and automatic-fallback mapped playback.
- Reminders and ordinary AutoPlay, source/channel-scoped event identities and
  selective cancellation; additive M3U updates and source-aware XMLTV caching.
- XMLTV source offsets, optional XMLTV/URL logos, passive guide styling, safe JSON
  image matches, closed-catalog action customization and typed media/folder mappings.
  See the [feature inventory](docs/modernization-status.md#feature-inventory).
- Internal search requires no extra add-on. Optional [TMDbHelper lookup](docs/metadata-search.md)
  needs an installed/enabled compatible `plugin.video.themoviedb.helper` with its
  own dependencies/access/setup; it is not full ExtendedInfo or automatic plot/art replacement.
- Optional [Kodi PVR recording/timers](docs/recording-pvr.md) need a capable,
  configured recording backend and enabled PVR client; future scheduling also
  needs its EPG. XMLTV/M3U or IPTV Simple alone is not a recording backend.

## Current evidence and known limitations

The accepted private disposable **Nexus 20.5** campaign used exact `cc411d9` code:
clean GUI ZIP installation with official dependencies; direct/plugin moving
frames (including exact-source reused evidence); explicit alternative and
automatic fallback; Stop; reminder/AutoPlay creation and selective cancellation
preserving unrelated rules; saved reminder restart persistence; actual service
startup work; graceful exits status 0. This preparation changes metadata/docs,
not behavior, so that evidence is reused. **It is not native installation of the
new 0.1.0 ZIP.**

- **Audio UNTESTED**, accepted beta limitation: clips were video-only. Optional
  timed reminder delivery and actual AutoPlay firing were **not observed**.
- Automatic fallback can start the alternative while Kodi's original failure
  dialog remains visible. Logs are **non-clean**, including caught optional-control
  diagnostics and audio warnings; no blanket harmless-error claim.
- Matrix **19.4** native evidence is historical; static Matrix **19.5** is distinct.
  The historical Matrix crash is unresolved. Omega **21.3** native evidence is
  historical. Piers **22.0 RC2** is historical preview evidence, not final Kodi 22
  qualification; foreground/input limits and plugin EOF uncertainty remain.
  No all-platform testing claim is made.
- The inherited integrated static gate is **FAIL**: latest types-only counts are
  **605/605/605/578** (Matrix/Nexus/Omega/Piers); three locale errors per lane
  remain. No full gate rerun was performed for preparation. All 69 catalogs are retained.
- Third-party skins, external players, provider/catchup templates, legacy recording
  and FFmpeg/external AutoPlayWith parity remain incomplete or limited. Scheduler
  recurrence horizons, collisions and in-flight cancellation have limits. No new
  external-player branch, provider feature or settings-refresh redesign is implied.

## Screenshots

Existing actual Nexus 20.5 captures, Default TV Guide skin, no playback. They show
development UI, not proof of every beta feature or the published Alpha 1 UI.

![Fullscreen programme guide](resources/screenshots/fullscreen-guide.png)

![Programme actions](resources/screenshots/programme-actions.png)

![On Now](resources/screenshots/on-now.png)

![Title search results](resources/screenshots/search-results.png)

![Channel management](resources/screenshots/channel-management.png)

## Alpha 1 download and installation

The existing public prerelease remains [0.0.446 Alpha 1](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.0.446-alpha1):
[installer ZIP](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.0.446-alpha1/script.tvguide.fullscreen-0.0.446.alpha1.zip)
and [SHA256SUMS](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.0.446-alpha1/SHA256SUMS).
Its immutable tag `v0.0.446-alpha1` points to
`fc2f021ef6edc8c957e1ca91bfaa024d17c5f510`; manifest `0.0.446~alpha1` and asset
`script.tvguide.fullscreen-0.0.446.alpha1.zip` are unchanged. Installer SHA-256:
`dd10ec02c5a3e9c8f133c87c3cc0ac1806a650473cad7ef877554346daa903e7`.
See [historical Alpha installation and qualification](docs/alpha-installation.md).
Those results do not establish current beta acceptance or upgrade-file pruning.

## Feedback, attribution and license

Report problems to [this fork's issues](https://github.com/kcook98765/script.tvguide.fullscreen/issues)
with source/version, Kodi build/platform, expected/actual result and minimal
steps using safe synthetic data. Remove tokens, credentials, private feed/programme
details, endpoints and profile paths from excerpts; never upload raw settings,
databases, private screenshots or unredacted logs. See the [changelog](changelog.txt).

Based on [primaeval's TV Guide Fullscreen](https://github.com/primaeval/script.tvguide.fullscreen),
Tommy Winther's (twinther) TV Guide, FTV Guide/Thomas Geppert (bluezed), and
Midraal's fork. Thanks to iainmacleod, im85288, RayW1986, andy, Zomboided, tycoo,
kjb86, Doctor-Eggs and the other credited contributors. Original provider,
contributors, source notices and upstream history are preserved; no upstream
endorsement is implied. [LICENSE.txt](LICENSE.txt) contains GNU GPL v2; source
notices permit **GPL v2 or later**. This software comes without warranty.
The separate [third-party notice](THIRD-PARTY-NOTICES.txt) preserves Raymond
Hettinger's OrderedDict MIT terms; the distinct Marti Raudsepp 2010 MIT notice
remains embedded unchanged in `pyaes.py`.
