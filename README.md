# TV Guide Fullscreen — 0.1.2 Beta

## Introduction

TV Guide Fullscreen is a fullscreen XMLTV programme guide for Kodi: browse listings,
map channels to streams, search programmes, and set reminders or ordinary AutoPlay.
This maintained Python 3 modernization fork builds on **primaeval's TV Guide
Fullscreen**, retaining its Program add-on and background service.
**[0.1.2 Beta](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.1.2-beta)**
is a maintenance release. TV Guide Fullscreen supplies no subscriptions or feeds.

## What changed in 0.1.2

Stream Setup shows the selected tab's contents again in **Default, Dark and
CatBar**. To browse installed sources, open a channel's context menu and choose
**Stream Setup → Browse** or **Addons**. See the [0.1.2 release notes](docs/beta-0.1.2.md).

## Modernization highlights

- Python 3, current Kodi API usage and dependency handling replace older foundations;
  [official pytz](docs/official-pytz.md) replaces the vendored copy.
- XMLTV source offsets, source-aware caching, additive M3U updates, unusable programme
  rows and missing channel names have targeted corrections.
- Guide/Quick guide navigation, scheduling identities and selective cancellation,
  stream mapping, alternative playback and fallback handling have been modernized.
- Legacy custom commands and add-on action mappings are unsupported: use the
  [available actions](docs/action-bar.md) or [playable streams/supported folders](docs/typed-playback-mappings.md)
  instead. Saved data is kept; arbitrary command execution is not restored.
- VPN Manager integration is removed. Optional fixed TMDbHelper metadata lookup and
  Kodi PVR recording/timer handoffs have the prerequisites below.

## What is retained

Fullscreen and Quick guide, programme details, On Now, search/navigation, channel
management, primary/alternative/fallback stream mappings, reminders and ordinary
AutoPlay remain. Existing settings are retained within the supported scope, not
as a promise that every legacy integration works. See the detailed
[feature inventory](docs/modernization-status.md#feature-inventory).

## Important differences

- **VPN:** manage connectivity independently through Kodi, your OS or network.
  Stale VPN flags are ignored, not migrated or deleted; see [removal scope](docs/vpn-manager-removal.md).
- **Metadata:** internal guide search needs no extra add-on. Optional
  [TMDbHelper lookup](docs/metadata-search.md) requires an installed/enabled compatible
  `plugin.video.themoviedb.helper`, its dependencies and online setup. It is not
  full ExtendedInfo or automatic guide plot/art replacement.
- **Recording:** [Kodi PVR timers](docs/recording-pvr.md) require a configured,
  recording-capable backend and enabled PVR client; future scheduling needs its EPG.
  XMLTV, M3U or IPTV Simple alone is **not a recorder**.
- Third-party skins, external players, old providers/catchup, legacy recording,
  FFmpeg and external AutoPlayWith remain incomplete or limited; no full parity is claimed.

<a id="installation--two-proposed-methods-after-publication"></a>

## Installation

### Recommended: kcook-lab-repo

1. In Kodi **File manager → Add source**, add
   `https://kcook98765.github.io/kcook-lab-repo/`.
2. Choose **Add-ons → Install from zip file** and select
   [repository.ai.kodi-0.1.1.zip](https://kcook98765.github.io/kcook-lab-repo/repository.ai.kodi-0.1.1.zip)
   from that source. This installs the repository, not TV Guide.
3. Choose **Install from repository → kcook-lab-repo → Program add-ons →
   TV Guide Fullscreen**.

The [Nexus 20.x](https://kcook98765.github.io/kcook-lab-repo/catalogs/nexus/addons.xml)
and [Omega 21.x](https://kcook98765.github.io/kcook-lab-repo/catalogs/omega/addons.xml)
catalogs offer **0.1.2 Beta**. The
[Matrix 19.x catalog](https://kcook98765.github.io/kcook-lab-repo/catalogs/matrix/addons.xml)
stays on **0.1.1 Beta** pending investigation of the
[Matrix startup fault](https://github.com/kcook98765/script.tvguide.fullscreen/issues/82).
Piers 22.x is a development preview and is outside TV Guide repository publication.

### Direct GitHub Beta ZIP

Download the [installer ZIP](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.1.2-beta/script.tvguide.fullscreen-0.1.2.zip)
and [SHA256SUMS](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.1.2-beta/SHA256SUMS)
together without renaming. Run `sha256sum --check --strict SHA256SUMS` there;
require `script.tvguide.fullscreen-0.1.2.zip: OK` before **Install from zip file**.
Do not install after a verification failure or use source-snapshot ZIPs as installers.
Both routes require ordinary **Unknown sources** consent when prompted; ask your
administrator if policy prevents installation, rather than bypassing it. No Reset is required.

<a id="required-dependencies"></a>

Keep Kodi's official repository enabled. All six minimum declarations are required;
external modules are official Kodi dependencies, **not bundled**:

| Dependency | Minimum |
| --- | --- |
| `xbmc.python` (Kodi-provided) | `3.0.0` |
| `script.module.requests` | `2.31.0` |
| `script.module.dateutil` | `2.8.2` |
| `script.module.pytz` | `2023.3.0+matrix.1` |
| `script.module.pil` | `5.1.0` |
| `script.module.beautifulsoup4` | `4.12.2` |

Configure a current **XMLTV file/URL** and matching **M3U stream mappings** in settings;
allow the initial import to finish. Use **My add-ons → Program add-ons → TV Guide
Fullscreen → Info → Run**. Enable background service work only with explicit consent;
never run `service.py` manually. Ordinary **Stop** returns playback to the guide.
You need your own sources and stream/content entitlements.

<a id="updating-and-first-use"></a>

## Updating older TV Guide

Back up your **Kodi profile, TV Guide settings, channel/stream mappings and saved
reminder/AutoPlay rules** first; a separate test profile is preferable. The same
add-on ID supports the normal in-place update path. A native 0.1.1 to 0.1.2
upgrade using the exact ZIPs on disposable Omega 21.3 preserved user settings,
channels and saved stream mappings. The ZIP upgrade ran through a private test
feed. Public catalog availability was verified separately. Updates from older builds
or different fork IDs can require separate migration checks.
Changing source offsets may reuse cached programmes; read the
[refresh and rule-preservation cautions](docs/xmltv-source-offsets.md) before forcing refreshes.

<a id="current-evidence-and-known-limitations"></a>

## Known Beta limits

**Audio UNTESTED**; optional notification delivery and actual timer-fired AutoPlay
**UNOBSERVED**. An original playback-error dialog can remain while fallback plays.
Logs are non-clean and inherited static findings remain; optional features,
scheduler horizons/collisions/in-flight cancellation, upgrades and parity have limits.
See the [0.1.2 qualification and limitations](docs/beta-0.1.2.md#qualification)
and [technical release history](docs/release-history.md). Matrix 19.4 qualification
is blocked before Stream Setup by an unclassified native startup fault.

<a id="feedback-attribution-and-license"></a>

## Credits, license and issues

Based on [primaeval's TV Guide Fullscreen](https://github.com/primaeval/script.tvguide.fullscreen),
Tommy Winther (twinther), FTV Guide/Thomas Geppert (bluezed), and Midraal's fork.
Thanks to iainmacleod, im85288, RayW1986, andy, Zomboided, tycoo, kjb86, Doctor-Eggs
and all other credited contributors. No upstream endorsement is implied.
[GPL v2 or later](LICENSE.txt) source notices and warranty disclaimer remain;
[OrderedDict MIT terms](THIRD-PARTY-NOTICES.txt) and Marti Raudsepp's 2010 pyaes MIT
notice in `pyaes.py` are preserved.

Report [issues](https://github.com/kcook98765/script.tvguide.fullscreen/issues) with
version, Kodi/platform, expected/actual behavior and minimal synthetic reproduction.
Redact credentials, tokens, private feeds/programmes, endpoints and profile paths;
never upload raw settings, databases, private screenshots or unredacted logs.
See the [changelog](changelog.txt) and [release history](docs/release-history.md).

<a id="historical-alpha-1-download-and-installation"></a><a id="alpha-1-download-and-installation"></a>
<a id="historical-010-beta--existing-direct-installer"></a><a id="preparation-history--2026-11-21"></a>
<a id="features-and-optional-integrations"></a><a id="current-screenshot"></a><a id="kcook-lab-repo--recommended-for-nexus-205"></a><a id="direct-github-releases"></a>

Historical downloads, preparation, technical detail and screenshot provenance have
moved to [release history](docs/release-history.md); installation is [above](#installation).
