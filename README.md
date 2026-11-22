# TV Guide Fullscreen — 0.1.1 Beta candidate

A fullscreen XMLTV programme guide for Kodi: browse what's on, map channels to
streams, search listings, and set reminders or ordinary AutoPlay. This is the
**maintained modernization fork** of primaeval's TV Guide Fullscreen, preserving
its Program add-on and background service. It supplies no TV subscriptions or feeds.

**0.1.1 is prepared for independent review, NOT published.** Proposed tag:
`v0.1.1-beta` (not created). This is an **artwork-only successor; runtime unchanged**:
original geometric icon/fanart replace the Earth images, and four promotional
screenshots are omitted. The channel-management capture remains byte-identical.
See [0.1.1 scope](docs/beta-0.1.1.md) and [artwork provenance](docs/artwork-provenance.md).
The beta reuses
independently accepted, bounded Nexus 20.5 core evidence for unchanged code. This
is not stable/full legacy parity, a clean static gate, or current four-version
beta native qualification. See
[historical 0.1.0 Beta evidence and release notes](docs/beta-0.1.0.md).
The bounded beta recommendation is **Nexus 20.5**; Matrix/Omega/Piers beta acceptance
is deferred, with historical evidence only, not fresh beta PASS. This scope decision
supplies neither content rights nor repository admission.

**Repository publication remains pending separate review and approval.** This
candidate addresses the identified promotional-artwork blockers, not a blanket
rights certification or automatic repository admission. No live 0.1.1 download,
TV Guide catalog entry or Pages promotion is claimed. The public **0.1.0 Beta**
and **Alpha 1** releases, their assets and historical evidence remain unchanged.

<a id="installation--two-proposed-methods-after-publication"></a>

## Installation

### kcook-lab-repo — only after approved Nexus-only publication

This is a **future 0.1.1 route**, not a current TV Guide catalog claim. Once the
exact candidate is reviewed, admitted and published for Nexus:

1. In Kodi **File manager → Add source**, add
   `https://kcook98765.github.io/kcook-lab-repo/`, naming it `kcook-lab-repo`.
2. Use **Add-ons → Install from zip file** to select the current repository
   installer, `repository.ai.kodi-0.1.1.zip`, from that source. This installs the
   repository, not TV Guide itself. If prompted, explicitly consent to Kodi's
   standard **Unknown sources** setting for this trusted source; if unavailable,
   ask your Kodi administrator rather than bypassing policy.
3. After approved **Nexus-only** listing, use **Install from repository →
   kcook-lab-repo → Program add-ons → TV Guide Fullscreen 0.1.1**.

Repository updates follow Kodi's update/origin settings; no automatic migration
or updates of an existing ZIP installation are guaranteed.

### Direct GitHub Releases — only once 0.1.1 is released

1. Once published, open tag `v0.1.1-beta` in the
   [Releases index](https://github.com/kcook98765/script.tvguide.fullscreen/releases)
   and download **both** `script.tvguide.fullscreen-0.1.1.zip` and `SHA256SUMS`.
   Proposed release URL (not live):
   `https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.1.1-beta`.
   Do not use GitHub source-snapshot ZIPs as installers.
2. Save the two assets together without renaming the ZIP. Run
   `sha256sum --check --strict SHA256SUMS` in that directory and require
   `script.tvguide.fullscreen-0.1.1.zip: OK`. If verification fails, do not install.
3. Back up the profile/settings/mappings/rules as below; then use **Add-ons →
   Install from zip file** to select the verified ZIP. Give explicit consent to
   Kodi's standard Unknown sources prompt if needed; ask your administrator if
   supported installation is unavailable. **No Kodi Reset is required.**

### Historical 0.1.0 Beta — existing direct installer

The public [historical 0.1.0 Beta release](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.1.0-beta),
[installer ZIP](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.1.0-beta/script.tvguide.fullscreen-0.1.0.zip)
and [SHA256SUMS](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.1.0-beta/SHA256SUMS)
remain unchanged: **2,137,274 bytes, 322 files**, SHA-256
`da5f38eed4707aa6de9ac7d9648008565ac332f51e93dc6cc5dab6f11f00f82e`.
It is not listed in kcook-lab-repo; see the detailed
[historical installation, evidence and capture history](docs/beta-0.1.0.md).
Historical [Alpha 1 links and identity](#historical-alpha-1-download-and-installation)
are retained below. Neither historical release is rebuilt or retagged here.

### Updating and first use

Back up your **Kodi profile, TV Guide settings, channel/stream mappings and saved
reminder/AutoPlay rules** first; prefer a separate test profile. Numeric manifest
version **`0.1.1` sorts above `0.1.0` and `0.0.446~alpha1`**. A normal in-place update is the
intended route; no Kodi profile Reset is required. Actual Alpha-to-beta upgrade,
migration, obsolete-file pruning and ZIP-installed automatic updates have **not**
been verified, including removal of the four omitted screenshots from an existing
installation. No 0.1.1 native install, upgrade or repository UI test was performed; original
profiles were untouched by preparation. Installing the existing repository does
not itself make TV Guide available or guarantee an existing ZIP install will auto-update.

Keep the official Kodi repository enabled for required dependencies. Configure
a current **XMLTV file/URL** and matching **M3U stream mappings** in TV Guide's
settings; use only sources you are entitled to access. Allow the initial import
to finish. Launch through **My add-ons → Program add-ons → TV Guide Fullscreen →
Info → Run**. Keep the background service with explicit consent; do not execute
`service.py` manually. Ordinary **Stop** returns from playback to the guide.
Changing an XMLTV offset alone may reuse cached programmes: see the
[offset/refresh cautions](docs/xmltv-source-offsets.md) before forcing a refresh
that could affect channel-associated rules.

## Preparation history — 2026-11-21

The original unpublished private 0.1.0 ZIP remains historical, SHA-256
`0b25379c9eb71bd6e9014704114e5b3a7104c6fbbd9e209a97f5e189f7464492`.
Its notice-only successor added the missing OrderedDict backport MIT notice in
[THIRD-PARTY-NOTICES.txt](THIRD-PARTY-NOTICES.txt), superseding it for review and
subsequent publication. All 321 original payloads, including all 45 runtime Python
files, are unchanged; the notice is the sole added installer member. The owner
authorized the same numeric `0.1.0` because the original candidate was unpublished.
The preparation and successor reviews did not themselves publish a release or
grant rights/repository admission. See the [dated successor disclosure](docs/beta-0.1.0.md#notice-only-successor).

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
startup work; graceful exits status 0. Accepted source:
`cc411d933a269d4cba080a3bdf646b5eddc71e22`. This successor changes artwork and
metadata/docs, not runtime behavior, so that evidence is reused. **It is not new
0.1.1 native installation, upgrade or repository UI acceptance.**

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

## Current screenshot

Retained owner-authored actual Nexus 20.5 channel-management capture, Default TV
Guide skin, no playback; exact published 0.1.0 bytes. Ordinary channel labels/UI
have no separately identified artwork blocker in Codex's individual visual review.
Not a new capture or proof of every beta feature. Four other promotional captures
were omitted, not replaced or simulated; their capture history remains in the
[historical 0.1.0 notes](docs/beta-0.1.0.md) and immutable published source/release.
See [the per-image dispositions](docs/artwork-provenance.md).

![Channel management](resources/screenshots/channel-management.png)

## Historical Alpha 1 download and installation

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
