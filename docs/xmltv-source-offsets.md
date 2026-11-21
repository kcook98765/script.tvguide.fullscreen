# Independent XMLTV source offsets (Alpha A1)

Scope: source-only repair against `95c031089ca1908019376a2c95d3f01a42c240bf`.
Related acceptance tracks: [XMLTV/EPG #4](https://github.com/kcook98765/script.tvguide.fullscreen/issues/4)
and [dependencies/settings #3](https://github.com/kcook98765/script.tvguide.fullscreen/issues/3).

`XMLTVSource.getDataFromExternal` must pass each file its own configured minute
offset. The branch with all three files already did this. With only one optional
source enabled **or available**, secondary received `xmltv.offset`, while tertiary
received `xmltv2.offset`. Only those two arguments change; enablement rules,
required primary file, source order and parsing behavior remain intact. There is
no settings migration, boolean/locale work, dependency or version change.

## Reproduction and regression

Run from the isolated source worktree:

```sh
/usr/bin/python3 -B tests/check_xmltv_source_offsets.py
```

The test AST-extracts the actual routing, file wrapper, parser/date methods and
Channel/Program classes. A recording wrapper delegates to the real
`getDataFromExternal2`; it does not fabricate programmes or model the branch
selection. Small in-memory VFS/settings fakes fail closed on unexpected paths.
UTC inputs and a frozen local-time offset avoid host clock/timezone dependence.
No Kodi/stub module, add-on entry point, network, database or real profile is run.

Four test methods exercise **128 scenarios**: four optional-enabled pairs × all
eight file-presence combinations × four offset triples. The distinct triples
`(0, -45, 90)`, `(60, 0, -120)`, `(-90, 150, 0)` give every slot zero, negative
and positive values; `(0, 0, 0)` shows why defaults hide the defect.

Assertions cover exact forwarded offsets/date/channel list/callback, both start
and end times, channel/program identity/metadata/order, disabled/missing optional
files and missing-primary rejection before any parser/VFS file open. The latter
accounts for 64 scenarios. Small fixtures do not reach the parser's 500-row
progress threshold; this is not progress-UI coverage.

Before the fix: **exit 1, 18 failing subtests** (not test setup errors). With
offsets `(0, -45, 90)` and a 12:00–12:30 UTC programme, secondary-only produced
12:00–12:30 rather than 11:15–11:45; tertiary-only produced 11:15–11:45 rather
than 13:30–14:00. Both optional files present already passed, including distinct
offsets. Both enabled with either optional file missing exposed the same defects.

After the two-argument repair: **exit 0, all 128 scenarios pass**.

Nearby focused commands (not the full static gate):

```sh
/usr/bin/python3 -B tests/check_xmltv_source_cache.py
/usr/bin/python3 -B tests/check_native_fixtures.py
/usr/bin/python3 -B tests/check_dependencies_settings.py
/usr/bin/python3 -B tests/check_python3.py
/usr/bin/python3 -B tests/check_m3u_channel_updates.py
/usr/bin/python3 -B -c "import ast; from pathlib import Path; paths = ('source.py', 'tests/check_xmltv_source_offsets.py'); [ast.parse(Path(p).read_text(encoding='utf-8'), filename=p, feature_version=(3, 8)) for p in paths]; print('PASS Python 3.8 grammar:', ', '.join(paths))"
git diff --check
```

## Evidence and limits

Private raw commands/exits/stdout/stderr and source/test hashes are retained under
the canonical checkout's `.git/modernization-evidence/alpha-A1-offsets/`.
Python 3.12 emits existing invalid-regex-escape `SyntaxWarning`s while parsing
unrelated retained source; outputs preserve them rather than suppress them.

**Native pending.** No Kodi/Lab inspection, lifecycle, workspace deployment,
launch, native settings persistence, GUI/EPG or playback acceptance is performed
in A1. The six-stage Toolkit static gate is also intentionally unrun; focused
stdlib tests and Python 3.8 grammar acceptance do not qualify any Kodi release.
Script+service declarations, GPL/upstream credits, assets and feature coverage
remain unchanged. Codex independently reviews this draft; no merge is authorized.
