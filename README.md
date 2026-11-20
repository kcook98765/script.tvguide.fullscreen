# TV Guide Fullscreen — development fork

A fullscreen XMLTV programme guide for Kodi, with channel/stream mappings,
search, reminders, ordinary AutoPlay and optional integrations. This fork is a
**modernization source candidate**, not a qualified release or ready-to-install
distribution.

Intended targets: **Matrix 19.4, Nexus 20.5, Omega 21.3 and Piers 22 RC2**.
All four native acceptance lanes are **BLOCKED/UNRUN**; the
[Lab394 activation dependency](https://github.com/kcook98765/kodi-lab/issues/394)
is explicitly deferred. Current source has not been deployed or native-tested.
On runtime baseline `5e83b888`, Task22's 16 focused scripts pass, but full
validation **FAILS on all four static lanes** (typing and official checker).
Source readiness is **PARTIAL**, not clean qualification; see the
[measured results and limits](docs/modernization-status.md#qualification).

## What is being preserved?

The guide, ordinary playback, internal search and background service remain in
source. Merged restorations include punctuation-safe reminders/AutoPlay, scoped
event identities, backend-dependent PVR, passive styling, TMDbHelper lookup,
JSON image matches, closed-catalog action customization and typed stream/folder
mappings. These bounded replacements do not establish full legacy parity.

See the **[current feature inventory and qualification status](docs/modernization-status.md)**
for retained features, bounded replacements, remaining gaps and qualification.
Only downloaded-code/arbitrary-command mechanisms are approved removed; other
feature gaps remain provisional. Both the Program entry (`addon.py`) and service
entry (`service.py`), and their original responsibilities, are required.

Track overall acceptance in [issue #1](https://github.com/kcook98765/script.tvguide.fullscreen/issues/1)
and preservation/research in [issue #14](https://github.com/kcook98765/script.tvguide.fullscreen/issues/14).
The inventory links focused usage docs and [local acceptance fixtures](docs/native-fixtures.md).

## Upstream and license

Based on [primaeval's TV Guide Fullscreen](https://github.com/primaeval/script.tvguide.fullscreen),
the original TV Guide by Tommy Winther (twinther), FTV Guide/Thomas Geppert
(bluezed), and Midraal's fork. Thanks also to the credited contributors:
iainmacleod, im85288, RayW1986, andy, Zomboided, tycoo, kjb86 and Doctor-Eggs.
Original master, history, source notices and credits are preserved.

See [LICENSE.txt](LICENSE.txt) for GNU GPL version 2; source notices permit
version 2 or later. This work does not change those terms or imply upstream
endorsement.
