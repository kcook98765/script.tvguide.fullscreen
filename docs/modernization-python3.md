# Shared Python 3 / Kodi API port — task03

Refs #2, parent #1; dependency/settings follow-up #3. Source-only, **PARTIAL**:
not native acceptance or permission to launch. OpenCode implemented this port;
Codex supervises and independently reviews, without editing source.

## Integration and scope

PR #12's accepted head `898aa6e6e18028d336a07c6c196d37dd441292d3` was
normally merged as `4617e9fd47b4424daed1b704cd99b3df4df45f93`. The merge tree
equals the reviewed tree (`b347ffe93f4ecedc76b04fb919dd41373a01e622`), preserving
all three commits. Original master remains `0e46733`. #7 and #1 stay open.

One shared branch targets owner-approved Matrix **19.4**, Nexus **20.5**,
Omega **21.3**, Piers **22 RC2**. No fork code was imported, version split made,
or GPL/upstream attribution removed. Tooling CPython 3.12 is not Kodi's embedded
interpreter; a separate AST check uses conservative Python 3.6 grammar.

- Port exception/print syntax, urllib/html/configparser/thread/itertools imports,
  RPC metaclass, iterator advancement, materialized SD batches, and removed
  ElementTree iteration. Repair vendored pytz's removed Mapping import and alias;
  do not replace its timezone data or pretend it is current.
- Keep settings/sqlite/mapping/UI values as text; retain bytes for AES/base64,
  hashing, gzip and XML parsing. XMLTV reads bytes with actual byte progress;
  optional XML repair decodes/re-encodes its declaration. INI parsing retains
  case, duplicate-key tolerance and literal URL percent escapes. Keep integer
  alarm minutes, pixel positions and logo dimensions; use comparable tuple
  keys at all five category-order sites.
- Replace path translation with xbmcvfs, notice logging with symbolic LOGINFO,
  old abort flag with Monitor, removed ListItem image arguments/setters with
  setArt, removed dialog lines with newline-joined message text, and erroneous
  getFocusId arguments. Background progress APIs already match; retain them.
  Pillow LANCZOS replaces removed ANTIALIAS (the installed typing still omits
  this documented alias). ResetDatabase/backup now explicitly import sys.
- Preserve safety digests, delimiter rejection, encoded catchup components and
  Player data APIs. Adapt only Python3 spellings/service log syntax in the safety
  checks; retain every original negative control and safety assertion.
- Set xbmc.python minimum **3.0.0**, not an embedded CPython version. Remove only
  obsolete service timing `start="login"`; retain the service extension/library.
  This is justified by current service semantics, **not a fix for Toolkit #31**
  (misclassifying timing as a filename). Its original repro remains in evidence;
  no fake login file, Toolkit patch or product extension removal was used.

## API basis (read 2026-11-19)

- Official tagged [Matrix 19.4 ListItem.h](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/interfaces/legacy/ListItem.h):
  v19 removes iconImage/thumbnailImage constructor arguments; use setArt.
  setInfo remains available; no migration to Nexus-only InfoTag setters.
- [Matrix Dialog.h](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/interfaces/legacy/Dialog.h):
  ok/yesno/progress remove line2/line3 in v19; BG update retains heading/message.
- [Nexus ModuleXbmc.h](https://github.com/xbmc/xbmc/blob/20.5-Nexus/xbmc/interfaces/legacy/ModuleXbmc.h):
  v19 removes LOGNOTICE (use LOGINFO) / LOGSEVERE (use LOGFATAL); no numeric guesses.
  No LOGSEVERE usage was found in this tree.
- [Matrix File.cpp](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/interfaces/legacy/File.cpp)
  implements binary readBytes; [Matrix Python manifest](https://github.com/xbmc/xbmc/blob/19.4-Matrix/addons/xbmc.python/addon.xml)
  provides API 3.0.0. xbmcvfs.translatePath and Monitor are common 19–22 APIs;
  later-lane stubs are checked separately, not inferred from Matrix alone.
- Official [Service add-ons](https://kodi.wiki/view/Service_add-ons) revision
  234134: service declaration has no timing attribute; pre-Leia startup timing
  was removed. It also documents Monitor instead of the old abort flag.
  Tagged [Matrix Service.cpp](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/addons/Service.cpp)
  starts enabled services without consulting timing.
- [Pillow 10 removal notes](https://pillow.readthedocs.io/en/stable/releasenotes/10.0.0.html#constants)
  explicitly recommend Image.LANCZOS or Image.Resampling.LANCZOS.

## Checks and remaining gates

Private raw JSON, stdout/stderr, negative controls and source exports are under
`.git/modernization-evidence/task03-*`, never distributable runtime packages.
The first focused export's wrong basename/package failure is preserved, not
attributed to addon.xml. Subsequent exports use `script.tvguide.fullscreen`
and contain only explicitly staged tracked source, not local configuration or
Git/evidence. The initial root scan was unsuitable because it traverses local
non-payload files; do not reuse that layout. No configuration contents were
inspected by the implementer. Final check identities/results accompany the PR.

All three focused scripts run independently in a minimal environment. They
import no legacy module or Kodi stub: safety controls use baseline source as
inert data; the Python3 check executes only extracted pure entity/date/sqlite
converters plus stdlib in-memory controls. It does not test AES, providers or UI.

The four lanes retain all six stages. Syntax/manifest/paths/package can pass
while mypy and official checker fail: no clean validation is claimed. Missing
bs4 and dateutil/pytz typing, legacy variable-reuse/nullable/dynamic XML-control
typing and inherited WindowXML allocation signatures are not addressed by a
whole-provider typing rewrite. The pre-existing inactive VOD callback references
an undefined programList; its dialog never assigns a selection. This remains a
documented non-port feature defect, not a proven working path.

Smallest next task (#3/task04): verify Python3 dependency IDs/versions on all
four releases (especially PIL/Pillow and bs4), fix legacy settings persistence
against modern profile XML without direct competing writes, and prepare one
credential-free local XMLTV/mapping fixture. Repository-compliance work remains
for empty news metadata, explicit assets/icon transparency and 69 legacy language
directories. Retain checker dependency advice/warnings; Piers's 3.0.1 advice is
stale and does not establish full RC2 API coverage. Matrix static qualification
is the documented 19.5 lane/major evidence, not a native 19.4 test.

No Lab/native calls, lifecycle, inventory, workspace import/validation/deployment,
launch/smoke, UI/logs/screenshots, production access, releases/tags or distribution
publication occurred. Mixed Program+service remains intact: managed owned-project
import's mixed-service limitation must be resolved by a supported future workflow,
not by deleting the service to manufacture a receipt. Future native work requires
separate authorization and enabled inventory (disabled means administrator source
enablement), exact identities/generations, validation and supported launch access.
