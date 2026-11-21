# TV Guide Fullscreen — Alpha development

A fullscreen XMLTV programme guide for Kodi: browse what's on, map channels to
streams, search listings, and set reminders or ordinary AutoPlay. This is an
**actively developed modernization fork**, not a qualified release or a promise
of full legacy feature parity.

The owner-decided **initial Alpha scope includes all four versions: Matrix 19.4,
Nexus 20.5, Omega 21.3 and Piers 22.0-RC2**. The former Nexus-first recommendation
is superseded. As of **21 November 2026 UTC**, the independently reviewed
**bounded aggregate native gate passed on all four; the final four-lane static
gate remains FAIL**. No Alpha release is published yet.

The native result combines fresh guide/import/service/preservation observations
with exact, reviewed historical component evidence. Nexus/Omega reuse historical
moving local clips and callbacks: **current LAN picture motion remains unverified**,
even though playback clocks advanced. This is not current full-stream/audio
acceptance or proof of whole historical GUI identity. Matrix's old crash is not
resolved. Piers is the exact tested RC2, not a future stable-support promise;
Matrix native **19.4** is distinct from static **19.5**. No all-platform, clean-log
or full-parity claim is made.
See the **[current feature and qualification overview](docs/modernization-status.md)**
for precise sources, results and remaining limits.

## What's been restored?

- Python 3 / modern Kodi API groundwork, safer command/data handling, and both
  the original Program and background-service responsibilities.
- Punctuation-safe reminders and AutoPlay, with channel/source-scoped event
  identities and bounded reconstruction/cancellation behavior.
- Additive M3U channel updates that preserve programmes and schedules;
  source-aware XMLTV caching; guide labels, native control actions and empty-list
  navigation repairs. Core paths have bounded native evidence, with distinct
  per-version and exact-source limits—not acceptance of every feature.
- Reviewed Alpha source fixes for independent secondary/tertiary XMLTV offsets,
  XMLTV logo opt-in and explicit URL logos, title-search date windows, and
  source-scoped channel/catchup listings, plus restored logo-setting visibility.
  The final focused core batch passed all 19 scripts; broader static typing and
  official-checker failures remain disclosed in the overview.

Other bounded restorations include JSON image matches, passive guide styling,
closed-catalog action customization and typed media/folder mappings. The
[overview](docs/modernization-status.md#feature-inventory) links their usage notes.

## Optional integrations and known gaps

Internal guide search does **not** require an extra add-on. The existing optional
[TMDbHelper lookup](docs/metadata-search.md) needs an already installed/enabled
official `plugin.video.themoviedb.helper`, compatible dependencies and its own
metadata access/setup. It is a movie/TV lookup handoff, not full ExtendedInfo,
automatic episode matching or guide plot/art replacement.

[Kodi PVR recording/timers](docs/recording-pvr.md) require a configured, capable
recording backend and enabled Kodi PVR client; future scheduling also needs its
EPG. An arbitrary XMLTV/M3U stream or IPTV Simple installation is not a recording
backend. This is a partial replacement, not old FFmpeg/external AutoPlayWith parity.
Neither optional integration is new to these focused fixes, and those fixes do
not require installing another optional add-on.

Complex third-party skins, external players, legacy action/provider templates,
some catchup/provider behavior and old recording modes remain incomplete or
provisionally disabled. Old scheduler collisions, recurrence horizons and
in-flight cancellation have documented limits. Font glyph boxes, audio coverage
and partial timer evidence remain qualification limits. Translation identities
also need owner/translator decisions; no catalogs were discarded.

## Planned Alpha installation — unpublished

There is **no published Alpha, release ZIP or repository package from this work**.
A GitHub source snapshot is not a validated Kodi installer; inherited tags are
history, not Alpha release certification.

The plan is **one common TV Guide ZIP for all four initial-scope versions**, with
dependencies obtained separately from the official Kodi repository. Required
`script.module.pytz >= 2023.3.0+matrix.1` replaces the old bundled copy; it is not
optional and must not be bundled in the TV Guide ZIP. The other declared module
dependencies remain required. Both the Program (`addon.py`) and background service
(`service.py`) are preserved, with explicit consent for background execution.

**Proposed only:** shared Kodi manifest version `0.0.446~alpha1` and separate Git
tag `v0.0.446-alpha1`; the current manifest remains **0.0.445, unchanged**. The
eventual common asset would be `script.tvguide.fullscreen-0.0.446~alpha1.zip`, with
one add-on root, SHA-256 and exact source/candidate build notes. Owner-approved
version metadata, a rebuild/new hash and explicit publication authorization are
required first. No release asset is available yet. Repository publication requires
separate explicit approval. See the [planned installation steps](docs/alpha-installation.md)
and [current status](docs/modernization-status.md) before any future installation.

The clean qualification export is **317 files / 4,093,191 bytes**, including the
329-byte changelog addition, with no `resources/lib/pytz`. A private **0.0.445**
qualification preview is not a release installer or native clean-install proof.
All native tests used retained installations containing **595 unchanged unused
old vendor files** as well as the reviewed source. No clean native installation
or official-repository intake readiness is claimed.

## Feedback, history and license

Report reproducible problems to [this fork's issues](https://github.com/kcook98765/script.tvguide.fullscreen/issues),
including the reviewed source revision, Kodi build/platform and steps with safe
synthetic data. Never publish credentials, private feed names/URLs, private logs
or settings. Track [overall acceptance (#1)](https://github.com/kcook98765/script.tvguide.fullscreen/issues/1),
[feature preservation (#14)](https://github.com/kcook98765/script.tvguide.fullscreen/issues/14)
and the [development changelog](changelog.txt).

Based on [primaeval's TV Guide Fullscreen](https://github.com/primaeval/script.tvguide.fullscreen),
Tommy Winther's (twinther) TV Guide, FTV Guide/Thomas Geppert (bluezed), and
Midraal's fork. Thanks to iainmacleod, im85288, RayW1986, andy, Zomboided, tycoo,
kjb86, Doctor-Eggs and the other credited contributors. Upstream history and
source notices are preserved. [LICENSE.txt](LICENSE.txt) contains GNU GPL v2;
source notices permit **GPL v2 or later**. No upstream endorsement is implied.
