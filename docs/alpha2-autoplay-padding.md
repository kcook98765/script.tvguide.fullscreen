# Alpha2 S1: autoplay padding (refs #21)

Source-only correction based on main `439b8b72059a2f5031459a7dbefaa1a05b3bb24c`.
The two legacy enums display `0|1|2|3|4|5|10`, but save indices `0` through `6`.
`Autoplay._scheduleAutoplay` previously converted those strings directly to
minutes: selecting **10** therefore used **6**. `_paddingMinutes` now maps the
seven canonical saved strings to `(0, 1, 2, 3, 4, 5, 10)` at both consumers.

## Version-specific basis

Official `xbmc/addons/settings/AddonSettings.cpp`,
`CAddonSettings::InitializeFromOldSettingEnums`, checked on 2026-11-21:

| Exact Kodi source | Pinned method |
| --- | --- |
| Matrix 19.4 | [e12e66e, lines 1076–1193](https://github.com/xbmc/xbmc/blob/e12e66e019af29ba9d5f5a2614315b15a138b81a/xbmc/addons/settings/AddonSettings.cpp#L1076-L1193) |
| Nexus 20.5 | [4b95737, lines 1209–1334](https://github.com/xbmc/xbmc/blob/4b95737efaddf7c869736e539318f18433413ff1/xbmc/addons/settings/AddonSettings.cpp#L1209-L1334) |
| Omega 21.3 | [a3a448d, lines 1219–1344](https://github.com/xbmc/xbmc/blob/a3a448d26b8d560a65655dab2cd122994dc4e146/xbmc/addons/settings/AddonSettings.cpp#L1219-L1344) |
| Piers 22 RC2 | [d686683, lines 1219–1346](https://github.com/xbmc/xbmc/blob/d686683a55d50e576dd282f53fb2bf9914931b38/xbmc/addons/settings/AddonSettings.cpp#L1219-L1346) |

All four split `values` on `|`, assign `label = values[i]`, `value = i` for
`type="enum"`, and only override that value with an explicit `entries` attribute.
They parse the default into `CSettingInt`. Neither padding row has `entries`;
both retain default index `1`. This is not `labelenum` semantics. Tagged source
establishes the contract, not native GUI/persistence acceptance on these releases.

## Consumer trace and preservation

The only runtime padding readers are the start subtraction and optional stop
addition in `autoplay.py`. GUI registration (`gui.py` → `addAutoplay`) and GUI /
background reconstruction (`scheduleAutoplays`, including
`service.py:Service.onCachesUpdated`) converge on `_scheduleAutoplay`.
Database selection stays in `source.py`; padding is not stored in guide rows.
`play.py` / `stop.py` receive encoded channel/start identity, not padding settings.

The complete `resources/settings.xml` stays byte-identical to the base: IDs,
indices/order, defaults, visibility and actions remain unchanged. Saved selections
need no migration or rewrite. Unknown/empty/noncanonical strings fall back to the
existing one-minute default (including `-1`, `7`, literal label `10`, `bogus`,
`1.5`, ` 6`, `06`, `+6`); no numeric parsing or settings framework is introduced.
This is defensive handling if such strings reach the reader, not a claim Kodi
normally saves them. Settings-read exceptions are not swallowed.

Start/end floor rounding, past-start skipping, possibly negative start delays,
legacy cancellation, source/channel-scoped alarm names, payloads, callbacks and
ownership checks are unchanged. Stop remains conditional on `autoplays.stop ==
'true'`; when off, `after` is not read and no stop alarm is added. Background
service, DB, reminders, playback and safety code are unmodified.

## Focused evidence

Run with an existing tools interpreter and no inherited credentials:

```sh
env -i PATH=/usr/bin:/bin LANG=C.UTF-8 \
  /home/kyle/kodi-development/toolkit/.local/matrix/bin/python -B \
  tests/check_autoplay_data.py
```

The new tests first ran against the exact unmodified base scheduler (Git blob
`29b788bbaf5c42593eab6e9655c965dfd3f0e095`): **exit 1**, 4 tests,
26 failing subtests / 6 invalid-string errors. All 36 combinations of indices
0–5 and the default passed; 13 combinations involving index 6 and the stop-off
index-6 case failed. For an event starting in 10m30s and ending in 40m30s,
index 6 emitted start delay **4**, stop **46**, instead of **0**, **50**.

After the fix: **exit 0**, AutoPlay **10 tests**, including all 49 before/after
pairs, exact command/payload identity, reconstruction, seven stop-off cases,
enum options/defaults and 18 independent invalid-string cases. Existing callback,
ownership and hostile-data checks remain active. In-memory mutations returning
six instead of ten and using before for after both exit **1**, respectively
13 and 42 failing subtests; no mutated runtime file is written.

Also **exit 0**: schedule ownership (7 tests), reminders (6), service safety (5),
dependencies/settings, command-data, source safety, Python compatibility and
`git diff --check`. Python-3.8 AST parsing passes for both changed Python files.
Existing invalid-escape `SyntaxWarning`s from legacy source/baseline AST checks
are retained, not suppressed. These are inert captures/pure helpers and in-memory
SQLite checks, not native Kodi execution.

Private raw commands, actual exits, stdout/stderr, mutation driver, upstream
responses/hashes and preservation receipts are in
`.git/modernization-evidence/alpha2-scheduler/`, outside version control.
The Matrix tools lane reports host CPython 3.12.3/Linux, Kodistubs 19.0.3,
mypy 2.4.0, checker 0.0.36; it targets 19.5, not exact 19.4. No other stub lane
is qualified by that invocation; Piers remains bounded prerelease evidence.

Six-stage accounting: syntax **focused PASS**; manifest, paths, package, types,
official checker **not run** (full static gate excluded from S1). No dependency
installation, native startup, deployment, smoke, launch, UI, playback, settings
save/restart or lifecycle test was performed. No version/release/distribution
change. Stop for independent Codex review before any merge.

### Focused review correction

The scheduler test asserts only the two enum IDs/types, ordered options, defaults
and absence of `entries`; it no longer freezes the entire settings file to a
historical revision. Whole-file equality to the campaign base remains recorded
as private preservation evidence, not a product-test requirement. The affected
contract/default test rerun passes (1 test, exit 0); both mutations still exit 1
with 13 / 42 failing subtests. The 49-combination test is unchanged. The earlier
10-test suite result above predates this assertion-only correction; no full suite
or native gate was rerun. Existing baseline tests still require Git history, so
this is not an archive-portability fix or a claim the export failure was new.
