# Official pytz dependency — issue #54

This is a new **source-only** dependency/package follow-up to the historical
Alpha, not requalification of `965ee470` / GEN8. Native dependency installation
and the later single managed Nexus 20.5 guide-startup/XMLTV smoke are **PENDING**
Codex's independent exact-source/dependency/package/license review. No Kodi
lifecycle, install, deploy or launch was performed. Release support scope remains
owner-pending; this catalog check does not readjudicate Nexus-first scope.

## Official catalog and package evidence

All four official `addons.xml.gz` catalogs resolve the same declaration:

| Intended catalog | Official add-on version | Only dependency | Module |
| --- | --- | --- | --- |
| [Matrix](https://mirrors.kodi.tv/addons/matrix/addons.xml.gz) (19.4) | 2023.3.0+matrix.1 | xbmc.python 3.0.0 | lib/pytz |
| [Nexus](https://mirrors.kodi.tv/addons/nexus/addons.xml.gz) (20.5) | 2023.3.0+matrix.1 | xbmc.python 3.0.0 | lib/pytz |
| [Omega](https://mirrors.kodi.tv/addons/omega/addons.xml.gz) (21.3) | 2023.3.0+matrix.1 | xbmc.python 3.0.0 | lib/pytz |
| [Piers](https://mirrors.kodi.tv/addons/piers/addons.xml.gz) (22.0 RC2) | 2023.3.0+matrix.1 | xbmc.python 3.0.0 | lib/pytz |

Exact official package URLs and SHA-256 (each **510,726 bytes**):

* [Matrix ZIP](https://mirrors.kodi.tv/addons/matrix/script.module.pytz/script.module.pytz-2023.3.0+matrix.1.zip):
  `0ec070d6d0e0b40f6f3cf1615ecfc4534bc676072babb9aea55c37222cd94dc1`
* [Nexus ZIP](https://mirrors.kodi.tv/addons/nexus/script.module.pytz/script.module.pytz-2023.3.0+matrix.1.zip):
  `688a40b069406d930fcad6e421ea740a55279216fe19333b5b4db9cc6afa708d`
* [Omega ZIP](https://mirrors.kodi.tv/addons/omega/script.module.pytz/script.module.pytz-2023.3.0+matrix.1.zip):
  `ac770594355682d2b9c7c9d5a9ad468e14f7fd08ba05ea6ecfaea5333495babe`
* [Piers ZIP](https://mirrors.kodi.tv/addons/piers/script.module.pytz/script.module.pytz-2023.3.0+matrix.1.zip):
  `cc6b55237c50b38179ba0d0f15ebc142a6de51c32eb0ac86014063d0d72f3fc8`

The archives differ, but every one of their **611 file payloads** matches across
the four packages. Catalog and packaged manifests agree. Packaged `addon.xml`
SHA-256 is `fc150f77c8f92ccd982ec3c67e2c3158a25f7d04fdabeab34596f8bae3441e2c`.
These are official mirror downloads, not unofficial repositories or repackages.

The module declares platform `all`, `xbmc.python.module` library `lib`, MIT, and
no third-party/transitive module dependency. Its actual code identifies **pytz
2023.3 / tzdata 2023c**, has Python-3 branches and preserves `timezone`, `utc`,
`localize` and `normalize`. It has no native extension requirement. The API floor
3.0.0 is compatible with the four intended Kodi Python-3 API declarations; it is
not a CPython version. This establishes declaration/source compatibility, not
four-platform native qualification or a claim of the latest timezone database.

Matrix **19.4** is this follow-up's compatibility target. Its exact
[xbmc.python manifest](https://github.com/xbmc/xbmc/blob/e12e66e019af29ba9d5f5a2614315b15a138b81a/addons/xbmc.python/addon.xml)
at the retained Task14 Kodi revision declares **3.0.0** (ABI 3.0.0), satisfying
the official module's API floor. The Matrix catalog is release-family metadata,
not evidence of native installation or testing on 19.4. **19.5** names only the
historical static-tooling target, not this compatibility target. No new native
Matrix test or static gate was performed for this documentation correction.

The common minimum **2023.3.0+matrix.1** selects the exact package verified in all
four current catalogs, not the earliest possible pytz API. The suffix does not
restrict it to Matrix: all four catalogs explicitly carry it. Later compatible
official versions can satisfy this minimum. TV Guide remains **0.0.445**, with
both Program/service extensions and all other dependencies unchanged.

## Focused source and license decision

Only `source.py` imported the vendor from runtime code: `import
resources.lib.pytz as pytz` and `from resources.lib.pytz import timezone`. These
become standard imports. Vendor-internal imports/doctests disappear with the
vendor. Existing `pytz.utc`, both London `normalize(localize(...))` conversion
paths, dateutil `tz.tzlocal()`, XMLTV offsets, reminders and scheduling are
unchanged. No fallback, zoneinfo migration or framework was added.

The baseline copy identifies **2015.7 / 2015g**. Its tracked directory has no
standalone license or copyright notice; original history is retained unchanged.
No substantial vendored implementation remains in the new runtime. For retained
attribution/reference, [pytz-LICENSE.txt](pytz-LICENSE.txt) reproduces the complete
MIT notice shipped by the reviewed official package (Stuart Bishop, 2003–2019),
without claiming it is a newly discovered original-2015 notice. The separately
installed official module ships that notice itself. Root GPL license, manifest
GPLv2 and upstream credits/history are untouched; this is not relicensing.

## Proportional checks and size

The original tracked vendor inventory is **595 files / 801,521 logical bytes**
(not the approximate issue estimate). All are removed. Using the same raw runtime
inventory boundary (all tracked resources, root Python, manifest, changelog,
artwork, GPL license and commands.txt), the count falls from **912 files /
4,894,184 bytes** to **317 files / 4,092,862 bytes**: net reduction **801,322
bytes**, including the small manifest/import/changelog changes. Docs/tests are
outside that runtime boundary; no TV Guide installer ZIP is produced or
published. The official dependency occupies its own separate,
potentially shared Kodi installation; the reduction is not a claim about total
installed Kodi disk use.

Focused checks use an owned disposable extraction of the exact official Nexus
package, with site packages disabled (`-I -S -B`); ambient host pytz is not proof.
`tests/check_official_pytz.py` executes only the real import ASTs and the two
existing pure conversion methods on a few ordinary dates with a deterministic
local offset. Existing dependency/settings, safety and XMLTV offset regressions
are the nearby checks. No full suite, Toolkit validate, timezone-history/DST
campaign, provider request, playback or timer test is part of this follow-up.

All four focused commands passed (exit 0), using the existing Nexus tool
interpreter `/home/kyle/kodi-development/toolkit/.venv/bin/python` (CPython 3.12
host tooling, not Kodi's embedded interpreter), with `-I -S -B`:

* `tests/check_official_pytz.py <reviewed-official-module-lib>` — imports and six
  ordinary conversions across the two existing methods.
* `tests/check_dependencies_settings.py` — retained negative controls detected;
  exact dependency floor, dual extensions and settings contracts passed.
* `tests/check_safety.py` — retained unsafe-baseline controls detected; runtime
  scan passed without a vendor exemption.
* `tests/check_xmltv_source_offsets.py` — all four existing tests passed.

`git diff --check ed1226f695113470197b9e0d6c174f42b6f25487` also passed.
Existing invalid-escape `SyntaxWarning` diagnostics from source/baseline AST
parsing remain unchanged and are retained in full private command logs. No
Toolkit validation/stub-lane or native qualification is claimed.

Native installation is deferred: the normal supported path is Kodi's official
repository UI dependency resolution/installation. Unattended repo-install-by-ID
is unsupported (Lab #339); no arbitrary RPC or invented installer is proposed.
An appropriate supported exact-official-package workflow may instead be chosen
after review. No native method was invoked in this phase.
