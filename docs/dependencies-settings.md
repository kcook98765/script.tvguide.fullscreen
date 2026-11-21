# Dependencies and retained legacy settings (Task14)

## Current dependency follow-up — issue #54

The bundled pytz has now been replaced by the official Kodi module. See the
[focused dependency/package record](official-pytz.md) for exact four-catalog
versions, package hashes, licensing, checks and native-smoke limits. The Task14
table and vendor statements below are historical, not qualification of this
follow-up. Dateutil/tzlocal, provider and scheduler logic are unchanged.

> Historical task record: old activation-blocker / whole-campaign UNRUN statements
> below are superseded by the [current overview](modernization-status.md).
> Original failures and feature-specific unverified limits remain; later core
> native evidence is not blanket acceptance of this feature.

Scope: source review for the shared Matrix **19.4**, Nexus **20.5**, Omega
**21.3**, and Piers **22.0 RC2** implementation. This is **not** native dependency
installation, settings persistence, provider or GUI acceptance. Refs #1, #3, #14.
No packages were installed/enabled, and no profiles or Lab tools were accessed.

## Official dependency availability

The following are versions **observed in the official branch catalogs** during
Task14, not the oldest versions ever supported and not an assertion that an
arbitrary user's Kodi already has them installed:

| Dependency | Matrix | Nexus | Omega | Piers | Decision |
| --- | --- | --- | --- | --- | --- |
| `script.module.simplejson` | 3.19.1+matrix.1 | 3.19.1+matrix.1 | 3.19.1+matrix.1 | 3.19.1+matrix.1 | Remove unused direct requirement only |
| `script.module.requests` | 2.31.0 | 2.31.0 | 2.31.0 | 2.31.0 | Common practical floor 2.31.0 |
| `script.module.dateutil` | 2.8.2 | 2.8.2 | 2.8.2 | 2.8.2 | Common practical floor 2.8.2 |
| `script.module.beautifulsoup4` | 4.12.2 | 4.12.2 | 4.12.2 | 4.12.2 | Common practical floor 4.12.2 |
| `script.module.pil` | 5.1.0 bundled | 5.1.0 bundled | 5.1.0 bundled | 5.1.0 bundled | Explicit wrapper floor 5.1.0 |

Catalog sources: [Matrix][matrix-index], [Nexus][nexus-index],
[Omega][omega-index], [Piers][piers-index]. PIL is **absent from these catalogs**;
its evidence is instead each tagged Kodi tree's
`addons/script.module.pil/addon.xml`: [19.4][matrix-pil], [20.5][nexus-pil],
[21.3][omega-pil], [22RC2][piers-pil]. All five module manifests declare
`xbmc.python` 3.0.0. PIL's **add-on wrapper version is not the installed Pillow
engine version**, which depends on the Kodi/platform build. Binary installation
and image decoding on those builds remain untested.

The retained modules' current [official source manifests][module-source] match
the catalogs. Their requests transitive requirements are certifi 2023.5.7,
chardet 5.1.0, idna 3.4.0 and urllib3 1.26.16+matrix.1; dateutil requires six
1.15.0+matrix.1; BeautifulSoup requires soupsieve 2.4.1. These remain the modules'
own requirements, not new direct dependencies or optional provider requirements
of TVGuide.

### Why these floors, rather than the old numbers or release-specific forks?

Requests 2.9.1 and dateutil 2.4.2 predate the Python-3 Kodi packaging transition;
BeautifulSoup and PIL previously had no explicit floors. The old version numbers
were permissive lower bounds, **not proof of incompatibility** with current Kodi.
The new floors select the smallest versions in the **current observed common
official set**, avoiding demands for packages available only on newer branches.
They are not claims that TVGuide needs a newly introduced API, that these are
security-patched forever, or that all earlier Python-3 packages are broken.

For historical context, the official Python-3 Matrix packaging commit
[`18f7bc5e`][matrix-packaging] already offered requests 2.22.0+matrix.1, dateutil
2.8.1+matrix.1 and BeautifulSoup 4.6.3+matrix.1. We do not lower the practical
floors to that historical snapshot. A higher compatible module version can
satisfy a manifest minimum. `xbmc.python` **3.0.0 stays unchanged**: it is a
legitimate common API floor, not a claim that all four releases embed the same
CPython or require a global 3.1.1 import.

### Actual source use and dependency APIs

* **simplejson:** `rg -n -i simplejson --glob '*.py' --glob addon.xml
  --glob '!tests/**' --glob '!tools/**' .` found only the original manifest
  import, no runtime callsites. The focused regression test also scans every
  root/resources Python file. Existing stdlib `json` users are unchanged;
  no serializer substitution or behavior rewrite is involved. Removing this
  direct requirement does not uninstall an existing module or prevent another
  module from using it transitively.
* **requests:** `source.py`, `gui.py`, `fileFetcher.py`, `sdAPI.py`, `utils.py`,
  `logos.py`, `PickImage.py`, and `yo.py` use `get`, sessions/cookies, headers,
  authentication, streamed responses, status codes, `.content`, `.text` and/or
  `.json()`; SD also uses `put`, `post`, `delete`. These APIs remain in the
  official packaged [api.py][requests-api], [sessions.py][requests-sessions]
  and [models.py][requests-models]. No request, parsing, TLS, authentication or
  provider-default behavior is changed here. Requests 2.31 is Python-3 compatible;
  availability and source signatures are not successful HTTP/provider tests.
* **dateutil:** `source.py` imports `tz` and uses `tz.tzlocal()` in the optional
  provider date path. The [packaged implementation][dateutil-tz] retains that
  datetime `tzinfo` API. The unrelated vendored pytz implementation is untouched.
* **BeautifulSoup:** `source.py`'s retained `FixturesSource` uses `BeautifulSoup`,
  `find(class_=...)`, tag attributes and `stripped_strings`. Its
  [packaged implementation][bs4-source] supports Python 3.6+, including 3.8.
  The provider is not newly exposed/enabled. Its implicit parser selection and
  remote-site health are not qualified by this change.
* **PIL/Pillow:** `ResizeLogos.py`, `utils.py`, and `custom_skin.py` use Image
  open/new/convert/crop/resize/save, ImageOps.invert, LANCZOS and decompression
  bomb handling. These are existing Pillow APIs (see upstream
  [Image][pillow-image] / [ImageOps][pillow-ops]); no image algorithm or optional
  import is removed or replaced. Bundled-wrapper evidence is separate from
  platform-specific Pillow API/codec execution.

No new provider, network dependency or package installer is introduced. Optional
sources/features retain their existing choices and defaults.

## Legacy settings: retained intentionally

Primary source reviewed: `xbmc/addons/settings/AddonSettings.cpp` and
`xbmc/settings/lib/Setting.cpp` at these exact Kodi commits:

| Intended release | Pinned source | Relevant legacy loader behavior |
| --- | --- | --- |
| 19.4 Matrix | [`e12e66e0`][matrix-settings] | `InitializeDefinitions` falls back to old definitions; enum integers vs labelenum strings |
| 20.5 Nexus | [`4b95737e`][nexus-settings] | Same old-definition dispatch and representation distinction |
| 21.3 Omega | [`a3a448d2`][omega-settings] | Same; legacy settings not removed |
| 22.0 RC2 Piers | [`d686683a`][piers-settings] | Same retained loader, despite native source implementation changes |

In **each** version, `InitializeFromOldSettingEnums` makes `enum` an integer
option list (indices unless explicit entries), calls `FromString(defaultValue)`,
and makes `labelenum` a string option list with the literal default. `select`
with `values` likewise stores strings, while `select` with `lvalues` uses integer
options. Existing numeric-looking labelenum values (timeouts, channel counts,
spacing) are therefore intentionally left as strings. `skin`, `favourites`,
`source.source` and `up.cat.mode` retain their label/value representations.

The loader also retains bool, number, text/hidden password, path/file/folder/image,
time, slider, separators and action settings, relative enable/visible conditions,
and old stored-value loading (`LoadOldSettingValues` followed by `FromString`).
`ParseOldCondition` specifically maps numeric option indices to string option
values for old string-setting conditions. Consequently the catchup fields'
`eq(-1,0)` / `eq(-2,1)` conditions should **not** be blindly rewritten or taken
as proof that the underlying labelenum stores integer indices.

The exact condition chain was rechecked for the supervisor's interim question:

| Tag / pinned commit above | `AddonSettings.cpp`: string-option index conversion | `StringUtils.cpp`: `IsNaturalNumber` |
| --- | --- | --- |
| 19.4 Matrix | [lines 1455–1486][matrix-condition] | lines 1428–1440 |
| 20.5 Nexus | [lines 1610–1645][nexus-condition] | lines 1480–1492 |
| 21.3 Omega | [lines 1620–1655][omega-condition] | lines 1535–1547 |
| 22RC2 Piers | [lines 1625–1661][piers-condition] | lines 1533–1545 |

In all four sources `IsNaturalNumber` accepts **zero** (one or more digit
characters, not a greater-than-zero test). `eq` is parsed as `Equals`; the
relative offsets **-1** from `catchup.text` and **-2** from `catchup.direct`
both reference `catchup.type`. Its nonlocalized static string options are in the
unchanged order `Meta?`, `Direct`. The conversion replaces `expression.m_value`
with `options.at(valueIndex).value` **before** constructing the dependency.
Therefore `eq(-1,0)` becomes equality with **`Meta?`**, and `eq(-2,1)` becomes
equality with **`Direct`**, not the literal digits. `SettingDependency.cpp`
lines 148–150 (19/20/21) / 146–148 (22RC2) then calls
`setting->Equals(m_value)`. The newly valid default selects the Meta field;
choosing Direct selects the Direct field. A focused XML model checks both
offsets, the option mapping, and the negative literal-digit interpretation.
This is tagged-source reasoning plus a model, **not native GUI observation**.

### Three confirmed mismatches and bounded fixes

| Setting | Confirmed issue | Source-only change / retained representation |
| --- | --- | --- |
| `channel.shortcut` | enum default `None` is not an integer, consumers compare `0`–`3` | Default `0` (None). Same ID, enum, order and stored indices |
| `service.type` | enum default `Period` is not an integer, service compares `0` vs the time path | Default `0` (Period). Same ID, enum, order and stored indices; service code untouched |
| `catchup.type` | labelenum choices return `Meta?`/`Direct`, while all three consumers tested only `0` | Valid default `Meta?`; keep labelenum and both labels; shared predicate recognizes `Meta?` **and** legacy `0` as Meta |

The two invalid enum defaults previously failed integer parsing rather than
selecting their label. Explicit zero documents the intended first option, not a
migration to a new type. Valid stored selections `1`–`3` / `1` remain unchanged.

`settings_compat.is_meta_catchup` is read-only and used at **all three** catchup
decision points: source catchup-channel construction, streaming detection, and
GUI dispatch. Valid stored `Direct` remains Direct. The literal `0` is accepted
if returned by Kodi/older settings; the declared default is now the valid first
label. A returned `1` still takes Direct, but `1` was **not** a valid labelenum
option, so this is not a claim that Kodi will load arbitrary malformed numeric
values. Tagged `CSettingString::CheckValidity` checks options, while `SetDefault`
assigns the literal default; this explains why the old non-option default `0`
could exist even though UI selections produced labels. No code writes or
migrates stored settings, and synthetic tests do not prove Kodi's real-profile
load/save behavior. Fresh defaults, existing valid values, and any malformed old
values still need separately authorized native observation.

No setting IDs, types, option ordering, relative conditions, action entries or
other defaults are removed/changed. No wholesale v2 conversion is justified by
these tagged sources. Previously temporary feature restrictions are not made
permanent by this task.

### Settings actions and remaining boundaries

All **29** action rows are unchanged fixed `RunScript($CWD/<existing>.py,...)`
entries. Their scripts remain present: help, subscriptions, addon-folder refresh,
logo tools, shortcut/action editors/reset, image picker, reminder/autoplay clear,
database/cache reset, catchup editor, yo.tv setup, SchedulesDirect editor, backup
and mapping operations. Tagged `InitializeFromOldSettingAction` / `OnSettingAction`
still handle `$CWD` and the built-in action dispatch. The source-only test checks
unchanged action bytes, bounded local filenames and entry existence; no action
is invoked. These are retained supported entry paths, **not** proof all legacy
provider services or dialogs still function. Existing downloaded-code and
arbitrary-command protections remain in place; no generic user command action
is restored.

One adjacent **deferred finding** is `autoplays.before/after`: their enum labels
end in `10` but consumers currently use the stored index directly, making that
last option six minutes. This predates Task14 and lies in the separately owned
autoplay/schedule work. No setting retype, value migration or scheduling edit is
made here; coordinate a separate preservation fix/review rather than collide
with Task11/13. This audit is not a proof that every legacy provider setting or
data path is otherwise correct.

Task18 separately owns service-time / last-update / service-type **consumer**
robustness and journal/lock cleanup after its SQLite ownership proof. Task14
does not edit `service.py` or those state fields, and makes no service/settings
declaration changes beyond the three defaults already listed. Later integration
and final combined validation belong to the designated supervisor, not this
branch.

## Evidence and limits

Run the credential-free focused source/data suite with an existing tools
interpreter, for example:

```sh
env -i PATH=/usr/bin:/bin LANG=C.UTF-8 \
  /home/kyle/kodi-development/toolkit/.local/matrix/bin/python -B \
  tests/check_dependencies_settings.py
```

It detects all three invalid baseline defaults and the baseline Meta? misroute
in all three consumers, then exercises the actual isolated conditional branches
with inert readers/callbacks for `0`, `Meta?`, `1`, `Direct`. It checks retained
IDs/attributes, dependency floors and manifest entry ordinals,
fixed actions, absence of simplejson runtime use, and Python-3.8 source parsing.
No add-on entry point or third-party package is imported/executed.

Private raw evidence lives in `.git/modernization-evidence/task14-*`, including
official metadata/source bytes, URLs and SHA-256 indexes; source snapshot hashes;
test stdout/stderr and actual subprocess return codes. Toolkit **b8d07f8** is
read-only. The selected Matrix tools interpreter reports host CPython 3.12.3,
Kodistubs 19.0.3, mypy 2.4.0 and checker 0.0.36. This lane is statically mapped to
19.5; the exact **19.4** settings claim above instead uses tagged native source.
The focused helper type check uses the Toolkit's reviewed Matrix annotation
overlay. A nonexistent Kodi API negative control correctly fails with code 1.

Six-stage accounting (not a combined gate): Python-3.8 syntax **PASS**; manifest
and paths **focused data PASS only**; package **not run**; types **helper-only
PASS**; official checker **FAIL** (exit 1, 73 problems / 9 warnings). The one
Matrix checker replay uses the unchanged shared index cache dated
2026-10-20, not the live catalogs above. Its errors concern existing metadata
schema/empty news, undeclared artwork, transparent icon and 69 old language
directories; Task15 owns those areas. Its nine warnings (unverified online URLs,
complex script/service entry points and non-whitelisted fixture/pytz files) are
retained, not silenced. It emitted no dependency failure. That is **not** an
official checker pass, nor full dependency resolution on all native platforms.
No repeated full six-stage/four-lane run was performed; the final settled combined
gate is deferred. No new Nexus/Omega/Piers type qualification is claimed.

**Lab394 remains deferred. Native8–11 are blocked/unrun.** No deployment, smoke,
launch, screenshot, log, lifecycle, native settings save/restart or dependency
installation test was attempted. Fixed video-plugin smoke ineligibility is not
a diagnosis of this script/service add-on. Independent supervisor review is
required before merge; no release/publication/distribution change is included.

## Alpha A2: XMLTV logo opt-in

`parseXMLTV` now uses XMLTV channel icons only when `xmltv.logos == 'true'`;
the nonempty string `'false'` previously enabled them too. No setting is rewritten.
`/usr/bin/python3 -B tests/check_xmltv_logos.py` executes the actual parser with
inert VFS/logo fakes: true/false/empty values, missing icons, folder-match precedence,
TheLogoDB opt-in/keep rules, and an in-memory raw-string negative control.
At A2, the URL-source branch computed but did not assign a replacement logo;
that limitation was deliberately preserved for separate review.
No cache invalidation/forced refresh is added. A2 itself did not run native
persistence/display testing or the full Toolkit gate; private evidence:
`.git/modernization-evidence/alpha-A2-logos/`. The later
[final overview](modernization-status.md#qualification) records GEN7 fresh
Omega/Nexus parses with the false flag, 244 XML icons and zero database logos,
plus the final four-lane static FAIL. This does not accept every logo mode.

### Alpha A3: restore the explicit URL logo source

Selecting `logos.source=2` (Url) now uses the already constructed
`logos.url.rstrip('/') + '/' + title + '.png'` as the channel logo, overriding
XMLTV icons even when `xmltv.logos` is off or no icon exists. Case/spaces, folder
matching, empty-base fallback, and TheLogoDB Always / If Missing / keep precedence
are retained; no URL encoding, probing or download is added. The same parser tests
replace A2's broken-URL expectations and cover trailing slashes and precedence.
A3's private source evidence remains `.git/modernization-evidence/alpha-A3-url-logos/`.
The later final static gate failed as recorded in the overview; native URL-image
display/reachability remains unverified, not inferred from construction tests.

### Phase5: logo-setting visibility

[PR56](https://github.com/kcook98765/script.tvguide.fullscreen/pull/56) changes
only two `resources/settings.xml` visibility attributes: XMLTV and add-on-folder
logo options are visible when the Logos master is on and External is None, and
hidden when the master is off. The focused final **GEN8 Omega-only** retest
independently audited by supervisor Codex observed both options OFF, hid/restored
them using the master, left both options untouched and clicked Cancel. It is not
a save/migration test, new integration or full four-version settings acceptance.
See the [authoritative retest record](modernization-status.md#focused-final-settings-retest--gen8-omega-only)
for exact runtime, preservation, logs and Stop evidence. Historical Task14 failures
and boundaries above remain historical, not current whole-campaign blockers.

[matrix-index]: https://mirrors.kodi.tv/addons/matrix/addons.xml.gz
[nexus-index]: https://mirrors.kodi.tv/addons/nexus/addons.xml.gz
[omega-index]: https://mirrors.kodi.tv/addons/omega/addons.xml.gz
[piers-index]: https://mirrors.kodi.tv/addons/piers/addons.xml.gz
[module-source]: https://github.com/xbmc/repo-scripts/tree/af4e6593d0ea6305e97a90704093a343b2238c22
[matrix-packaging]: https://github.com/xbmc/repo-scripts/commit/18f7bc5eae780e0fefe798d0369c391478b0111b
[matrix-pil]: https://github.com/xbmc/xbmc/blob/e12e66e019af29ba9d5f5a2614315b15a138b81a/addons/script.module.pil/addon.xml
[nexus-pil]: https://github.com/xbmc/xbmc/blob/4b95737efaddf7c869736e539318f18433413ff1/addons/script.module.pil/addon.xml
[omega-pil]: https://github.com/xbmc/xbmc/blob/a3a448d26b8d560a65655dab2cd122994dc4e146/addons/script.module.pil/addon.xml
[piers-pil]: https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/addons/script.module.pil/addon.xml
[matrix-settings]: https://github.com/xbmc/xbmc/blob/e12e66e019af29ba9d5f5a2614315b15a138b81a/xbmc/addons/settings/AddonSettings.cpp
[nexus-settings]: https://github.com/xbmc/xbmc/blob/4b95737efaddf7c869736e539318f18433413ff1/xbmc/addons/settings/AddonSettings.cpp
[omega-settings]: https://github.com/xbmc/xbmc/blob/a3a448d26b8d560a65655dab2cd122994dc4e146/xbmc/addons/settings/AddonSettings.cpp
[piers-settings]: https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/addons/settings/AddonSettings.cpp
[matrix-condition]: https://github.com/xbmc/xbmc/blob/e12e66e019af29ba9d5f5a2614315b15a138b81a/xbmc/addons/settings/AddonSettings.cpp#L1455-L1486
[nexus-condition]: https://github.com/xbmc/xbmc/blob/4b95737efaddf7c869736e539318f18433413ff1/xbmc/addons/settings/AddonSettings.cpp#L1610-L1645
[omega-condition]: https://github.com/xbmc/xbmc/blob/a3a448d26b8d560a65655dab2cd122994dc4e146/xbmc/addons/settings/AddonSettings.cpp#L1620-L1655
[piers-condition]: https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/addons/settings/AddonSettings.cpp#L1625-L1661
[requests-api]: https://github.com/xbmc/repo-scripts/blob/af4e6593d0ea6305e97a90704093a343b2238c22/script.module.requests/lib/requests/api.py
[requests-sessions]: https://github.com/xbmc/repo-scripts/blob/af4e6593d0ea6305e97a90704093a343b2238c22/script.module.requests/lib/requests/sessions.py
[requests-models]: https://github.com/xbmc/repo-scripts/blob/af4e6593d0ea6305e97a90704093a343b2238c22/script.module.requests/lib/requests/models.py
[dateutil-tz]: https://github.com/xbmc/repo-scripts/blob/af4e6593d0ea6305e97a90704093a343b2238c22/script.module.dateutil/lib/dateutil/tz/tz.py
[bs4-source]: https://github.com/xbmc/repo-scripts/blob/af4e6593d0ea6305e97a90704093a343b2238c22/script.module.beautifulsoup4/lib/bs4/__init__.py
[pillow-image]: https://github.com/python-pillow/Pillow/blob/5.1.0/src/PIL/Image.py
[pillow-ops]: https://github.com/python-pillow/Pillow/blob/5.1.0/src/PIL/ImageOps.py
