# Package metadata and translations — Task15

> Historical task record: old activation-blocker / whole-campaign UNRUN statements
> below are superseded by the [current overview](modernization-status.md).
> Original failures and feature-specific unverified limits remain; later core
> native evidence is not blanket acceptance of this feature.

**Source-only partial readiness, not an install/native pass or official approval.**
Based only on `6d1b9162289ccc20c3ba089302dc3a149150d0be`, without merging
concurrent work. Refs #1, #3, #5, #14. Add-on version remains **0.0.445**;
there is no release, tag, repository submission or distribution change.

## Actual checker findings and bounded changes

The installed official `kodi-addon-checker==0.0.36` was inspected before edits.
The baseline has **69 existing PO catalogs**, not strings.xml files. Its focused
schema/artwork/localization functions reproduce **73 problems, 0 warnings**:
69 legacy directory names, whitespace-only news, two undeclared existing assets,
and a genuinely translucent icon. No XML-to-PO conversion is necessary.

- Add a short `en_GB` summary, use `en_GB` for the unchanged English description
  and disclaimer, replace empty news with an explicitly development-only note,
  and declare the existing root `icon.png` and `fanart.jpg` under assets.
- Point source at this development fork; keep primaeval as provider, the upstream
  website, every contributor in the description, and the original disclaimer.
  Omit the empty content-language element: it does not describe UI translations.
- **License text and manifest license (`GPLv2`) are unchanged.** This does not
  reinterpret or relicense the project. Requires and both executable extensions
  are byte-for-byte untouched, including ordinal0 `addon.py` and ordinal1
  `service.py`. No startup/service/settings/skin condition or function changes.
- Move 66 catalogs to verified Kodi language resource IDs. All 69 remain in the
  runtime tree. The [complete explicit mapping](../tests/package_language_map.json)
  includes the three deliberately unmoved exceptions below.

## Localization evidence and unresolved variants

[Official language documentation](https://kodi.wiki/view/Language_support)
specifies `resources/language/resource.language.en_gb/strings.po` as the English
fallback. It specifies per-language resource directories and UTF-8 PO files.
The existing verified Toolkit index cache supplies **65 exact add-on ID/name
matches independently on Matrix, Nexus, Omega and Piers**; English is separately
verified as Kodi's bundled `resource.language.en_gb`. This is a name mapping,
not qualification of those language add-ons or their installed availability.

Useful non-obvious **official names**, not guessed ISO suffixes:

| Legacy name | Verified official ID |
| --- | --- |
| Norwegian | `resource.language.nb_no` |
| Persian | `resource.language.fa_af` |
| Persian (Iran) | `resource.language.fa_ir` |
| Serbian | `resource.language.sr_rs@latin` |
| Serbian (Cyrillic) | `resource.language.sr_rs` |
| Esperanto | `resource.language.eo` |
| Vietnamese | `resource.language.vi_vn` |

Primary catalog endpoints are `https://mirrors.kodi.tv/addons/{branch}/addons.xml.gz`
for `matrix`, `nexus`, `omega`, `piers`. A corroborating source tree is
[official repo-resources Omega](https://github.com/xbmc/repo-resources/tree/2c7beda5ab6f1e7e458662a0ff861e38df9d204d).
Cache date, per-index sizes/hashes and exact checked pairs are retained privately;
the shared cache was not refreshed or changed.

**Do not merge or delete these catalogs to silence diagnostics:**

| Retained legacy directory | Reason and current limitation |
| --- | --- |
| `Georgian` | Header says `ka`; no corresponding language resource ID/name was found in the four verified catalogs. No invented `ka_ge` destination. The original two entries and legacy-name fallback opportunity remain. |
| `Haitian (Haitian Creole)` | Header says `ht`; likewise no verified corresponding official resource add-on identity. All six entries and the old directory remain. |
| `Vietnamese (Viet Nam)` | Header `vi_VN` conflicts with the separate `Vietnamese` catalog at ID30100: `Chung` vs `Tổng Quan`. The official resource name is `Vietnamese`, whose 13-entry catalog is moved intact. The four-entry variant remains separately intact, not silently overwritten/unioned. |

These three directories still cause **three official checker problems**. An
administrator/translator-reviewed identity or variant decision is a follow-up,
not a permanent user-facing removal. Catalog absence alone does not prove a
language is unsupported. Current official `Vietnamese` selection continues to
use the same catalog it previously found via its legacy name; the separately
named variant is not claimed to become newly selectable.

The fallback and stale-msgid behavior was inspected in official tagged source:

- [19.4 Matrix](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/guilib/LocalizeStrings.cpp)
- [20.5 Nexus](https://github.com/xbmc/xbmc/blob/20.5-Nexus/xbmc/guilib/LocalizeStrings.cpp)
- [21.3 Omega](https://github.com/xbmc/xbmc/blob/21.3-Omega/xbmc/guilib/LocalizeStrings.cpp)
- [22 RC2 Piers](https://github.com/xbmc/xbmc/blob/22.0rc2-Piers/xbmc/resources/LocalizeStrings.cpp)

`LoadStr2Mem` first tries the resource directory, then the installed language
add-on's legacy name; `LoadWithFallback` loads English defaults. `LoadPO` checks
ID/msgid freshness. The shared implementation is unchanged here. Tests compare
the before/after ID/decoded text tables, headers, plural fields, flags and the
modeled effective fallback tables for **all 2,492 entries**. No plural entries
are present; plural headers remain intact. Unicode, escapes, markup and comments
are not translated/re-escaped. **67 files are byte-identical; only English and
German gain one final LF from patch-tool normalization.** Their other bytes,
decoded values and attribution are identical. Initial overly strict byte tests
caught those two EOF differences; that failure is preserved, not erased.

## Existing icon, no redesign

The original is RGBA 512x512, alpha range **79–255**, with **112,893 partially
transparent pixels**, no fully transparent pixels, and black corners with alpha
92. The official checker actually tests transparency, not just RGBA mode.
Composite onto **black** using Pillow `Image.alpha_composite` and save as RGB PNG.
Black matches the existing corner/background RGB and the dark space graphic,
preserving the white television silhouette and opaque artwork pixels. It is an
explicit matte choice, not a claim of identical appearance on every background.
No crop/rescale/redesign/new asset. A pixel-for-pixel test checks the entire
result against that mathematical composite and rejects simply dropping alpha.

See [official metadata/assets conventions](https://kodi.wiki/view/Addon.xml) and
[official artwork checks](https://github.com/xbmc/addon-check/blob/master/kodi_addon_checker/check_artwork.py).
The **installed pinned 0.0.36 implementation**, not moving master, controls the
reported results.

## Focused evidence and remaining gates

Run the source-only preservation suite with the existing environment:

```sh
/home/kyle/kodi-development/toolkit/.local/omega/bin/python -I -B tests/check_package_metadata.py
```

It needs the preserved Git baseline and existing polib/Pillow, imports no add-on
or Kodi modules, and launches Git with a PATH-only environment (no credentials).
Five tests pass; per-language original/result SHA-256 and entry counts are kept.
Controls detect changed translated text, changed IDs, and escaped newline versus
literal backslash+n. Changed test syntax parses as Python3.8; tooling is host
CPython3.12.3. There is no new runtime Python implementation or framework.

One **Omega official-checker-only** offline replay on an explicit runtime export:

| Check | Actual result |
| --- | --- |
| Candidate official checker | **Exit1: 3 problems, 11 warnings**; not PASS |
| Manifest schema / existing artwork / all PO parsing | Accepted within that checker invocation |
| Locale name mapping | 65 exact pairs in each of four cached official indexes; bundled English verified separately |
| Preservation tests | Exit0, five tests / 69 catalogs / 2,492 entries |
| Negative metadata/artwork/legacy-directory fixture | **Expected exit1, five problems, zero warnings**; empty news, missing asset declarations, translucent icon and one old directory all detected |
| Whitespace / Python3.8 test-source AST | Passed |

All **11 checker warnings are retained**: three offline/unverified URL checks;
Omega's Python3.0.1 advice; missing beautifulsoup4 minimum version; complex entry
points for both script and service; the lawful deterministic fixture `mapping.m3u`;
and three bundled pytz `.tab` files. No dependency floor is changed to silence
advice (Task14 owns requires). No fixture/timezone data is removed to silence the
whitelist. The cache replay is not a live URL or dependency/native installation
test. The initial polib inspection needed the checker's historical comment
normalization; it did not require rewriting catalogs.

Private raw streams, actual subprocess returncodes, replay/cache provenance,
per-file runtime hashes, original icon hashes/pixel diagnostics, tagged primary
source hashes and the initial preservation-test failure are under the common Git
admin directory: `modernization-evidence/task15-package-metadata/`.
The export contains runtime root scripts, metadata/license/assets and complete
resources (including native fixtures), with exactly one add-on ID root. It excludes
Git, agent/config files, caches, tests, tools, docs and development evidence. It is
checker input only, not a published or native-validated installer.

**Not performed:** full six-stage CLI validation, broad typing, four-lane reruns,
or final combined settled gate. The selected Omega lane reports Kodistubs21.0.0,
mypy2.4.0 and checker0.0.36; `--branch` did not switch stubs. Matrix19.5 static is
not native19.4; Piers remains bounded RC2. Historical failures/warnings are not
overwritten by this narrower result. Full package readiness remains partial.

**Native #8–#11 remain BLOCKED/UNRUN under deferred Lab394.** No Lab calls,
lifecycle, import/deploy/launch/smoke, UI/navigation/screenshots/logs, profiles,
production access, infrastructure/config/Toolkit changes, permission changes,
publication or removal decision. Fixed video smoke ineligibility says nothing
about this preserved Program+service add-on's overall functional health.
Independent Codex review is required before any merge.

## Reviewed current-main integration

The sections above describe the initial package candidate and its original
checker receipt. [Independent initial review](https://github.com/kcook98765/script.tvguide.fullscreen/pull/27#issuecomment-7026034219)
accepted exact `006fdb5695b810234315f64da50d9c7105c7a667`, independently passed
all five preservation tests, and visually inspected both icon versions.

After dependency/settings PR24 was normally merged, Task15 normally merged exact
main `891151d2318f3178df61c77fa1da6482eaade2eb` as
`9f5f0b66b9b787f3756b2f6b64f343d61196e408` (no rebase or force push).
Approved requires/settings, scheduler, cache, AutoPlay, skins and metadata source
are retained from that main. This supersedes the initial comparison saying that
requires still equal the older `6d1b916` baseline: they now equal reviewed main.

The package test no longer freezes the entire pre-metadata manifest prefix or
the implementation bytes of `addon.py`/`service.py` at the old baseline. It still
checks complete extension identity/library/order, both entry files' presence and
nonempty content, metadata semantics, GPL and assets. Dependency correctness
remains covered separately by `check_dependencies_settings.py`. Every existing
translation/fallback/data-loss/escape and pixel-composite control is retained.
This allows legitimate future startup/service fixes instead of requiring their
reversion to satisfy an unrelated package test.

Durable private Git-tree evidence compares the integration to **pinned main**:
every path outside the explicit package/docs/test ownership set has the same Git
mode/blob, with no non-owned additions or removals. It separately proves that the
manifest outside its metadata extension equals main, while the metadata extension,
icon, fanart, language map and all 69 catalogs equal the reviewed package candidate.
The integration runs only the five package tests, dependency/settings, source
safety and command-data controls, plus changed-test Python3.8 AST/whitespace checks.
Raw streams, actual process returncodes and path/blob proof are retained under
`modernization-evidence/task15-package-metadata/integration-*`.

Focused integration results: all five package tests **pass (actual exit0)**;
dependency/settings, safety and command-data scripts each **exit0**, retaining
their baseline/unsafe-data negative controls. Changed-test Python3.8 AST and
whitespace checks pass. The proof verifies **865 non-owned main paths** by mode/blob
and confirms **69 catalogs / 2,492 entries** with the reviewed asset/catalog bytes.

The **original** Omega checker exit1 / three problems / eleven warnings is reused
only for the unchanged metadata/localization/artwork slice; **it is not a fresh
whole-integrated-tree checker result**. Approved dependency changes can alter its
dependency warnings. No new official-checker/full-six-stage/four-lane or final
combined gate is run. The three unresolved legacy directories remain intact;
no guessed mappings or new metadata/icon changes. Native #8–#11 remain unrun under
deferred Lab394, with no Lab/native/infrastructure/publication actions. Draft PR27
still requires independent final review before any merge.
