# TV Guide Fullscreen — continued practical development

A fullscreen XMLTV programme guide for Kodi: browse what's on, map channels to
streams, search listings, and set reminders or ordinary AutoPlay. This is an
**actively developed modernization fork**, not a qualified release or a promise
of full legacy feature parity.

**Alpha 1 is published; later work is continued development only.** Two further
independently reviewed, normally merged PRs correct reminder/AutoPlay event
matching, current-popup cancellation dispatch, cancelled wildcard input, and an
absent XMLTV display-name. Earlier Alpha2 padding, Quick guide and programme-row
repairs remain in place. No new version, installer or distribution is prepared.

At functional freeze **`ce8fe0f`**, **23 focused scripts passed: 128 unittest
methods plus three assertion scripts**. Fresh types-only checks report **two new
unresolved errors per lane**; the inherited full static gate remains **FAIL** and
was not rerun. One bounded **Nexus 20.5** round observed guide/context, scheduling
labels and wildcard Cancel returning to the guide; **no rules were created or
actual timers exercised**. XMLTV fallback has deterministic evidence only; the
other three native versions were unrun this campaign. Codex independently
reviewed the evidence and preservation audits; all four profiles ended stopped.
This is not full four-version/native scheduler acceptance or a publication
recommendation. See [continued scope, evidence and next work](docs/alpha2-development.md).

The owner-decided **initial Alpha 1 scope includes all four versions: Matrix 19.4,
Nexus 20.5, Omega 21.3 and Piers 22.0-RC2**. The former Nexus-first recommendation
is superseded. As of **21 November 2026 UTC**, the independently reviewed
**historical Alpha 1 bounded aggregate native gate passed on all four; its final
four-lane static gate remained FAIL**. [Alpha 1 is published as a GitHub prerelease](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.0.446-alpha1),
not a Kodi repository release.

That prior retained-install result combines fresh guide/import/service/preservation
observations with exact, reviewed historical component evidence. Nexus/Omega reuse
historical moving local clips and callbacks: **current LAN picture motion remains
unverified**, even though playback clocks advanced. This is not current
full-stream/audio acceptance or proof of whole historical GUI identity. Matrix's
old crash is not resolved. Piers is the exact tested RC2, not a future stable-support promise;
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
  The historical Alpha 1 focused core batch passed all 19 scripts; the earlier
  Alpha2 batch passed 21. The continued-development batch passed 23 as summarized
  above; broader static typing and official-checker failures remain disclosed.
  Focused source results do not establish native acceptance.

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

Next work is event-scoped once cancellation and a separately reviewed,
preserving XMLTV settings-refresh design. Dynamic control 3019 needs a reproduced
symptom or useful context before a fix; fewer caught control diagnostics in the
latest round reflect coverage, not repair. Logs remain **non-clean**. Historical
Matrix crash and Piers input work remain deferred, not resolved or retried.

## Alpha 1 download and installation

The public GitHub prerelease is **TV Guide Fullscreen 0.0.446 Alpha 1**:
[download the installer ZIP](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.0.446-alpha1/script.tvguide.fullscreen-0.0.446.alpha1.zip)
and [SHA256SUMS](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.0.446-alpha1/SHA256SUMS).
There is **no Kodi repository publication**. A GitHub source snapshot is not the
installer; inherited tags are history, not Alpha release certification.

There is **one common TV Guide ZIP for all four initial-scope versions**, with
dependencies obtained separately from the official Kodi repository. Required
`script.module.pytz >= 2023.3.0+matrix.1` replaces the old bundled copy; it is not
optional and must not be bundled in the TV Guide ZIP. The other declared module
dependencies remain required. Both the Program (`addon.py`) and background service
(`service.py`) are preserved, with explicit consent for background execution.

The shared Kodi manifest version remains **`0.0.446~alpha1`**. The immutable
annotated Git tag **`v0.0.446-alpha1`** points to
`fc2f021ef6edc8c957e1ca91bfaa024d17c5f510`. The public installer filename is
**`script.tvguide.fullscreen-0.0.446.alpha1.zip`**, which differs from the Kodi
manifest spelling. Its SHA-256 is
`dd10ec02c5a3e9c8f133c87c3cc0ac1806a650473cad7ef877554346daa903e7`.
Download the ZIP and `SHA256SUMS` into the same directory, keep the ZIP's published
filename, and run `sha256sum -c SHA256SUMS`; require
`script.tvguide.fullscreen-0.0.446.alpha1.zip: OK` before installing.
Publication does not extend qualification; the separate clean-install observation
is bounded below. See the [installation steps](docs/alpha-installation.md)
and [current status](docs/modernization-status.md) before installation.

The prior clean qualification export was **317 files / 4,093,191 bytes**, including
the 329-byte changelog addition. The candidate keeps the same **317 runtime paths**,
with only manifest/changelog bytes changed and no `resources/lib/pytz`. A private
**0.0.445** qualification preview is not a release installer or native clean-install proof.
The prior all-four qualification used retained installations containing **595
unchanged unused old vendor files** as well as the reviewed source.

Separately, the **actual Alpha candidate ZIP** passed ordinary **Install from zip
file** in one new, clean, isolated **Nexus 20.5** environment, with official
dependency resolution. Ordinary **Program Info → Run** displayed a populated
synthetic guide with two visible fixture channels/two programmes, titles, times
and description, independently viewed by Codex. Actual background-service work
also independently passed after one ordinary restart of the same disposable instance, without
manual service execution. **The bounded clean-install smoke passed**, including
graceful final Stop and Codex's independent stopped-file/provenance/log audit.
All 317 installed payloads matched the tested ZIP; no old bundled pytz remained.
Logs were not clean, despite no import failures or Python tracebacks.
This is one representative clean installation, not four clean installs, proof
that an upgrade prunes old files, or official-repository intake readiness.

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
