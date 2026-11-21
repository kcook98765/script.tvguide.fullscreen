# TV Guide Fullscreen — Alpha development

A fullscreen XMLTV programme guide for Kodi: browse what's on, map channels to
streams, search listings, and set reminders or ordinary AutoPlay. This is an
**actively developed modernization fork**, not a qualified release or a promise
of full legacy feature parity.

Intended targets are **Matrix 19.4, Nexus 20.5, Omega 21.3 and Piers 22 RC2**.
Historical native checks have exercised core guide/playback and background/timer
paths, but with version-specific exceptions—including a deferred Matrix
native-exit investigation and an unexplained Piers modal problem. The new
consolidated native round and four-lane static gate are **PENDING**.
Earlier full static validation failed;
Piers is an exact Linux RC2 preview, not stable or all-platform qualification.
See the **[current feature and qualification overview](docs/modernization-status.md)**
for precise sources, results and remaining limits.

## What's been restored?

- Python 3 / modern Kodi API groundwork, safer command/data handling, and both
  the original Program and background-service responsibilities.
- Punctuation-safe reminders and AutoPlay, with channel/source-scoped event
  identities and bounded reconstruction/cancellation behavior.
- Additive M3U channel updates that preserve programmes and schedules;
  source-aware XMLTV caching; guide labels, native control actions and empty-list
  navigation repairs. Core paths have historical bounded native evidence—not
  acceptance of every feature or of the latest source batch.
- Reviewed Alpha source fixes for independent secondary/tertiary XMLTV offsets,
  XMLTV logo opt-in and explicit URL logos, title-search date windows, and
  source-scoped channel/catchup listings. Their focused regressions pass;
  consolidated native verification is still pending.

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
Neither optional integration is new to the five Alpha fixes, and those fixes do
not require installing another optional add-on.

Complex third-party skins, external players, legacy action/provider templates,
some catchup/provider behavior and old recording modes remain incomplete or
provisionally disabled. Old scheduler collisions, recurrence horizons and
in-flight cancellation have documented limits. Font glyph boxes, audio coverage
and partial timer evidence remain qualification limits. Translation identities
also need owner/translator decisions; no catalogs were discarded.

## Trying reviewed development source

There is **no qualified release ZIP or repository package offered by this work**.
A GitHub source snapshot is not a validated Kodi installer; inherited tags are
history, not Alpha release certification.

Obtain this fork and pin the reviewed implementation commit named in the
[status overview](docs/modernization-status.md), rather than testing an arbitrary
moving branch tip. For that reviewed source baseline:

```sh
git clone https://github.com/kcook98765/script.tvguide.fullscreen.git tvguide-fullscreen-development
git -C tvguide-fullscreen-development checkout --detach ca198d4ffc498f23ffdfae59d815d84177b10f1f
```

This is a source checkout, not an installation step or a final runtime-freeze
pin. Check the overview for a later reviewed frozen candidate before testing.

For development testing, use a reviewed commit in an isolated checkout and a
separate disposable Kodi development profile—not your everyday setup. Review
`addon.xml` and make its declared Kodi dependencies available through supported
Kodi installation paths. Keep **both** `addon.py` and `service.py`, with explicit
consent for background execution; do not strip the service to make a test pass.

Use the existing authorized Toolkit/Lab source validation and deployment workflow
for the exact target/profile; do not bypass missing permissions or enablement.
Start with the [deterministic local fixtures](docs/native-fixtures.md), then
observe guide navigation, settings persistence, actual playback progression/Stop
and background work separately. A successful copy, enabled flag or launch
acknowledgement is not functional acceptance. The current pending round has not
been performed by this documentation update.

## Feedback, history and license

Report reproducible problems to [this fork's issues](https://github.com/kcook98765/script.tvguide.fullscreen/issues),
including the reviewed source revision, Kodi build/platform and steps with safe
synthetic data. Do not post credentials, private feeds/stream URLs or raw private
logs. Track [overall acceptance (#1)](https://github.com/kcook98765/script.tvguide.fullscreen/issues/1),
[feature preservation (#14)](https://github.com/kcook98765/script.tvguide.fullscreen/issues/14)
and the [development changelog](changelog.txt).

Based on [primaeval's TV Guide Fullscreen](https://github.com/primaeval/script.tvguide.fullscreen),
Tommy Winther's (twinther) TV Guide, FTV Guide/Thomas Geppert (bluezed), and
Midraal's fork. Thanks to iainmacleod, im85288, RayW1986, andy, Zomboided, tycoo,
kjb86, Doctor-Eggs and the other credited contributors. Upstream history and
source notices are preserved. [LICENSE.txt](LICENSE.txt) contains GNU GPL v2;
source notices permit **GPL v2 or later**. No upstream endorsement is implied.
