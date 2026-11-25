# Issue #93 — historical fixtures and current contracts

These source-only checks preserve the artwork-only **0.1.1** release claim
without imposing it on subsequent runtime development. They neither execute
Kodi entry points nor change shipped files, settings, versions or releases.

## Public immutable fixture

| Evidence | Git object |
| --- | --- |
| [`v0.1.1-beta`](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.1.1-beta) source | `f936c0a514e0de126e62e24fd3d24b66b0c74097` |
| Complete artwork-era tree | `c6d014c332f6d24b219f4976518dcf2221ae6a88` |
| Pre-artwork published source | `c19f256333efbe7af12418312f17e00f99792dc2` |
| Original metadata/catalog migration baseline | `6d1b9162289ccc20c3ba089302dc3a149150d0be` |

Independent release review verified all **318 runtime members** against the
public 0.1.1 installer ZIP, SHA-256
`76533fcb570cd813e2deb885c919b59eea21171c6ce344d5a40ef5d8fba287b9`.
See [release provenance](beta-0.1.1.md) and [artwork provenance](artwork-provenance.md).

Use a full Git clone with history; for shallow CI use `fetch-depth: 0`, or
explicitly prepare a shallow clone with `git fetch --unshallow origin`.
`git rev-parse f936c0a514e0de126e62e24fd3d24b66b0c74097^{tree}` must return
the tree above. Ordinary discovery exports this pinned public fixture into a
disposable test directory, rejecting archive links/devices/traversal. Missing
history fails with preparation guidance: no fetching, HEAD fallback or skips.
A source ZIP without Git history is not sufficient for these preservation tests.

## Baseline classification

Independent **unmodified full-suite** runs used Python 3.12.3, Pillow 10.2.0,
polib 1.2.0 and pytz 2024.1. The operator's independent review recorded:

| Baseline | Cases | Failure assertions | Conditional |
| --- | ---: | ---: | --- |
| Published `v0.1.2-beta` (`8fe6ede7c84cabd4d7d699335ed4e739a542b7d4`) | 234 | 6 | None |
| Prior integrated candidate | 302 | 13 | One existing Favorites exact-tag source check |

All thirteen failures occur within these four original methods, abbreviated
below: **A** = artwork `test_exact_screenshot_dispositions_and_no_missing_current_links`;
**B** = artwork `test_manifest_non_artwork_semantics_preserved`;
**C** = metadata `test_manifest_metadata_and_entrypoint_identity`;
**D** = license `test_exact_318_payload_delta_and_45_python_files_unchanged`.
They are stale historical assertions, not evidence that the reviewed runtime
fixes damaged artwork or licensing. The conditional is separate, not a failure.

| # | Original assertion/subcase | Published | Candidate | Actual invariant retained |
| --- | --- | --- | --- | --- |
| 1 | A: README embeds retained capture | FAIL | FAIL | Frozen README embeds it; current README may link to history. Retained bytes, manifest asset, advertised screenshot links and four omissions remain checked. |
| 2 | B: description byte equality | FAIL | FAIL | Frozen non-artwork manifest semantics and artwork-only news stay exact; current release prose may evolve while identity, credits, license and entry points remain protected. |
| 3 | C: version equals `0.1.1` | FAIL | FAIL | Historical version stays 0.1.1; current manifest, changelog heading, README heading and news prefix must agree dynamically. |
| 4 | D: CatBar Stream Setup XML bytes | FAIL | FAIL | Frozen bytes stay exact; current reviewed visibility changes are allowed, and the payload remains required. |
| 5 | D: Dark Stream Setup XML bytes | FAIL | FAIL | Same historical-byte/current-required-member invariant. |
| 6 | D: Default Stream Setup XML bytes | FAIL | FAIL | Same historical-byte/current-required-member invariant. |
| 7 | D: `action_bar.py` bytes | — | FAIL | Frozen implementation stays exact; current implementation may evolve, with required inventory and behavioral tests. |
| 8 | D: `fileFetcher.py` bytes | — | FAIL | Same; no incidental current runtime hashes. |
| 9 | D: `gui.py` bytes | — | FAIL | Same; original legal notices remain separately protected. |
| 10 | D: CatBar menu XML bytes | — | FAIL | Frozen XML stays exact; current payload remains required without freezing reviewed layout fixes. |
| 11 | D: Default menu XML bytes | — | FAIL | Same historical-byte/current-required-member invariant. |
| 12 | D: `source.py` bytes | — | FAIL | Frozen implementation stays exact; current required inventory and behavioral tests own subsequent changes. |
| 13 | D: extra `favourites_navigation.py` | — | FAIL | Only this explicitly reviewed extra is allowed; once imported by a runtime payload it is mandatory. No wildcard or automatic inventory updates. |

## Permanent acceptance checks

- **Frozen public artifact:** exact commit/tree, original manifest semantics and
  0.1.1 metadata, retained README capture, and **322 minus four = 318** runtime
  members. Exactly four changed payloads and **314 unchanged**, including all
  **45 Python files**, remain byte-checked against the pre-artwork release.
- **Artwork in both trees:** exact retained capture, original procedural icon
  and fanart plus generator/provenance hashes, deterministic encoded generation,
  image dimensions/RGB/encoding/metadata hygiene, all **166 skin images**, and
  absence of the four omitted captures. Damage controls reject modified assets
  even if their documented hashes are edited, extra images and bad links.
- **Current metadata:** original identity/provider, executable Program + service,
  existing entry points, license/disclaimer/contributors, maintained URLs, safe
  existing asset references, nonempty summary and bounded news. Consistent future
  versions and changed release prose pass; partial bumps and metadata damage fail.
- **Dependencies:** exactly six required minimum declarations: `xbmc.python`
  `3.0.0`, requests `2.31.0`, dateutil `2.8.2`, pytz `2023.3.0+matrix.1`, PIL
  `5.1.0`, beautifulsoup4 `4.12.2` (external modules use `script.module.*` IDs).
  Each has deletion, duplicate, optional=true and wrong-floor controls; an
  unrelated seventh import also fails. Explicit optional=false remains valid.
- **Licenses/attributions:** exact GPL and third-party notice, complete original
  addon/service GPL-v2-or-later headers and pyaes MIT block, full OrderedDict
  provenance/permission/conditions/disclaimer, and README credits. Legal damage
  fails; changes outside protected legal blocks do not freeze runtime code.
- **Catalogs:** all **69 catalogs / 2,492 entries**, metadata, decoded messages,
  IDs/plurals/flags/comments/attributions and fallback behavior remain checked.
  Only the recorded English/German final LF differences are allowed. Ambiguous
  locale variants and translation/ID/escape negative controls are retained.
- **Inventory/package safety:** require the pinned artifact's path set, not its
  current code hashes. Only the reviewed Favorites helper is additionally
  allowed (and required when imported). Missing/extra/duplicate members,
  unrelated root Python or resource files, packaged docs/tests, unsafe paths,
  symlinks and empty payloads fail; the two original empty package markers remain
  allowed. Changed valid runtime implementation bytes pass.
- **Source caches versus package candidates:** normal checkout `__pycache__`,
  `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.cache`, `.pyc` and `.pyo`
  artifacts are ignored by the source scan only. Explicit package member lists
  reject them even if an inventory declaration attempts to allow them. Regression
  controls also prove unrelated resources beside ignored caches still fail.

The source payload policy remains root Python, all distributable `resources/`
and the named manifest/changelog/commands/legal/artwork files. Docs/tests/tools
are not installer payloads. These checks do not replace an audit of a built ZIP
or qualify dependency installation, native behavior or all-platform compatibility.

## Normal verification

With Python 3 and Pillow/polib/pytz installed in an isolated test environment:

```sh
python3 tests/check_artwork.py
python3 tests/check_license_preservation.py
python3 tests/check_package_metadata.py
python3 tests/check_dependencies_settings.py
python3 tests/check_stream_setup_visibility.py
python3 tests/check_python3.py
python3 -m unittest discover -s tests -p 'check_*.py'
```

The amended tests-only worktree passes **250/250** discovered cases, with no
failures, errors or skips, using Python 3.12.3, Pillow 10.2.0, polib 1.2.0 and
pytz 2024.1. Its focused artwork, license/inventory and metadata suites pass
**13/13**, **10/10** and **8/8** respectively. Existing invalid-escape warnings
are retained, not silenced.

Exact image re-encoding is codec-sensitive; retain the recorded artwork
toolchain evidence rather than regenerating/blessing different assets.
The existing conditional Favorites unit, where present, can separately use
`--kodi-source-dir` with authorized exact-tag source copies; do not change or
blanket-skip that check.

Independent review also reported replaying the four version-specific Toolkit
lanes (Matrix/Nexus/Omega/Piers) against the prior and amended integrated ZIPs:
structure passed, **zero new normalized typing diagnostics** in every lane, with
the same **three inherited locale issues**. This is comparative static evidence,
not a claim of a clean checker gate or new native qualification.
