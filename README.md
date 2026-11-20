# TV Guide Fullscreen — development fork

A fullscreen XMLTV programme guide for Kodi, with channel/stream mappings,
search, reminders, ordinary AutoPlay and optional integrations. This fork is a
**modernization source candidate**, not a qualified release or ready-to-install
distribution. Source review does not establish working playback or native feature
parity.

Intended targets: **Matrix 19.4, Nexus 20.5, Omega 21.3 and Piers 22 RC2**.
All four native acceptance lanes are **BLOCKED/UNRUN**; the
[Lab394 activation dependency](https://github.com/kcook98765/kodi-lab/issues/394)
is explicitly deferred. Current main has not been deployed or native-tested.

## What is being preserved?

The fullscreen/quick guide, XMLTV, navigation, ordinary playback, internal search,
reminders and background service remain in source. Focused restorations cover
punctuation-safe reminders/AutoPlay, scoped event identities, optional PVR timers,
passive guide styling, TMDbHelper lookup and a persistent JSON image-match cache.
These are not blanket replacements for every legacy integration. Action-bar,
service-safety, package/translation and typed-mapping work is still under draft
review at this snapshot.

See the **[current feature inventory and qualification status](docs/modernization-status.md)**
for merged versus draft work, practical limits and the four-version native gate.
Only downloaded-code/arbitrary-command mechanisms are approved removed; other
feature gaps remain provisional. Both the Program entry (`addon.py`) and service
entry (`service.py`), and their original responsibilities, are required.

Useful focused guides:

- [Local XMLTV/M3U/video fixtures](docs/native-fixtures.md) — future acceptance inputs, not a native pass.
- [Dependencies and settings](docs/dependencies-settings.md).
- [Reminders](docs/modernization-reminders.md), [ordinary AutoPlay](docs/autoplay-data.md)
  and [event ownership/legacy limits](docs/schedule-ownership.md).
- [PVR recording](docs/recording-pvr.md), [passive styling](docs/custom-guide-skins.md),
  [metadata/search](docs/metadata-search.md) and [image-match cache](docs/image-match-cache.md).

Track overall acceptance in [issue #1](https://github.com/kcook98765/script.tvguide.fullscreen/issues/1)
and preservation/research in [issue #14](https://github.com/kcook98765/script.tvguide.fullscreen/issues/14).
Older focused notes retain their original review-time wording; the inventory
distinguishes their current GitHub merge state from functional acceptance.

## Upstream and license

Based on [primaeval's TV Guide Fullscreen](https://github.com/primaeval/script.tvguide.fullscreen),
the original TV Guide by Tommy Winther (twinther), FTV Guide/Thomas Geppert
(bluezed), and Midraal's fork. Thanks also to the credited contributors:
iainmacleod, im85288, RayW1986, andy, Zomboided, tycoo, kjb86 and Doctor-Eggs.
Original master, history, source notices and credits are preserved.

See [LICENSE.txt](LICENSE.txt) for GNU GPL version 2; source notices permit
version 2 or later. This work does not change those terms or imply upstream
endorsement.
