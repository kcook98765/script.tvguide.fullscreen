# Programme title search: bounded #86 investigation

Source baseline: `0c4a3c3f27f5980d616e5995f5a8b37512eace49` (0.1.2 Beta).
This is a source-only candidate, not a release or native qualification.
Related: #4, #5, #14, #49 and PR #50. No dependency on the separate #85 work.

## Reproduction before changing production code

`tests/check_program_title_search.py` builds eleven synthetic XMLTV channels and
programmes afresh for **2026-11-25 12:00**, and freezes the database search clock
to that same reference. All ordinary programmes run from 11:45 to 12:15. There
is no download, retained profile, existing cache or dependence on today's aging
feed. The parser's local timezone is deterministically UTC in this fixture.

The test executes the actual extracted XMLTV routing/parser, Channel/Program
models, `_updateProgramList` writer, timestamp codecs, `_getChannelList` and
`_programSearch`. Parsed values are compared with direct SQLite rows and returned
Program values. The writer's parameterized programme insert is also used by the
full cache importer. This uses the existing #49 **pared in-memory schema**, not
the full foreign-key/cache-refresh lifecycle; it does not prove migration or
refresh safety. No Kodi modules or Kodistubs are executed on the host.

| Query / data representation | Baseline, plot OFF | Candidate, plot OFF |
| --- | --- | --- |
| `60 Minutes` in title | Found | Found |
| `Georgie & Mandy's First Marriage` in title | Found | Found |
| `Roseanne` in title | Found, including the space-padded title | Same |
| `Frontline` in title | Found | Found |
| `Waterfall` in `The Joy Of Painting - Waterfall` title | Found | Found |
| `Waterfall` only in XMLTV `<sub-title>` | **Missing** | **Found** |
| `Waterfall` only in synopsis | Excluded | Excluded |

With plot ON, baseline finds the combined-title and synopsis-only rows; candidate
also finds the subtitle row. The other reported titles already match in both
modes. Uppercase/lowercase ASCII and ordinary partial queries work in both
versions; `WATERFALL`, `waterfall` and `aterfal` expose the same subtitle omission.

Raw XML `&amp;`, `&apos;` and `&#x2019;` become `&`, straight apostrophe and curly
apostrophe respectively, unchanged through storage and returned metadata.
`Double &amp;amp; Escape` becomes literal `Double &amp; Escape`: XML decoding is
once, not an invitation to decode stored titles again.

### Preserved matching semantics and limits

- Matching remains SQLite `LIKE '%query%'`, not fuzzy matching. Straight and curly
  apostrophes are distinct; each exact variant finds its corresponding fixture.
  There is no Unicode-wide casefold/accent/punctuation normalization.
- Padding is literal: `Roseanne` finds a padded stored title, but a padded query
  does not find an unpadded-only title (` Frontline ` returns no rows). There is
  no whitespace collapse or query trimming. The report supplies no exact query
  strings/feed rows to justify changing those independent semantics.
- SQL `%` and `_` remain LIKE wildcards as protected by #49's tests. Query text,
  including `x' OR 1=1 --`, is bound data and cannot widen eligibility. This is
  not a new literal-wildcard escaping policy.
- An empty direct database query still matches eligible rows; the unchanged GUI
  rejects empty/cancelled input before saving history or executing SQL. An
  unmatched query or no eligible channels returns an empty list.
- Each field is searched separately. A full combined series/episode string does
  not bridge the boundary between separate title and subtitle fields.
- The listing dialog still labels the subtitle result `The Joy Of Painting`;
  its original Program retains `sub_title='Waterfall'` for details/selection.
  No skin or list-label redesign is included.

## Intended window and eligibility, not five diagnosed feed defects

Both modes still require active source and `_getChannelList(True)` eligibility
(visible channels, existing channel-category filtering). Both retain #49's
inclusive **containment**, not overlap:

```text
start_date >= now - listing.hours
end_date   <= now + listing.days
```

Exact lower/upper and inside rows match; rows outside or spanning either edge do
not. Nondefault hours/days remain honored. Channel listing deliberately uses
different overlap predicates. A fresh but out-of-window row is an expected
exclusion, not stale data. An absent/old import, wrong active source, hidden
channel or selected channel category can also explain a miss independently of
title matching. This work does not inspect the reporter's feed or establish
which explanation applies to the four ordinary titles or a true combined title.
It must not be presented as fixing all five reported misses or stale EPG.

### Krypton-era comparison

Local history `15cd1117e56aedc56d0b4b30c302db1efc31d80e` (merge of the `krypton`
branch) and preserved original `0e46733e9e5f7711f2381562cfbb98fd3b54b429`
already store XMLTV title/subtitle separately and display them with a hyphen in
guide details. Their search omits subtitle; synopsis/title uses containment but
title-only has no bounds. The extracted **actual `0e46733` search method** was
also run on the same fresh parsed/stored fixture: all five title cases match,
the separate subtitle does not, and the synopsis-only row matches only with plot
ON. Adding a two-day-old `60 Minutes` returns two rows with legacy title-only,
one with synopsis/title. That is the deliberate #49/PR #50 difference, not a
reason to restore unbounded search. This is host SQLite evidence and source
history inspection, **not native Krypton execution**.

## Minimal change

Only `_programSearch` changes: add parameter-bound `sub_title LIKE ?` inside a
parenthesized matching group in **both** modes. Description remains
optional. Source, channel, window, ordering, metadata, GUI, history, selection,
settings, schema and cache logic are unchanged. A title-and-subtitle match still
returns the row once. There is no new framework or show-name special case.

## Test evidence

Host: `/usr/bin/python3`, CPython **3.12.3**, Linux x86_64, SQLite **3.45.1**.
These are host test details, not Kodi embedded-Python or per-version acceptance.

| Command (from add-on root) | Result |
| --- | --- |
| `python3 tests/check_program_title_search.py` before source edit | **FAIL: 10 methods, 13 failing assertions/subtests**, all detecting omitted subtitle results; main titles/parser/storage/literal behavior pass |
| Same test bytes after source edit | **PASS: 10 methods** |
| `python3 -m unittest discover -s tests -p 'check_program*.py'` | **PASS: 17 methods**, includes the unchanged seven #49 tests |
| `python3 tests/check_empty_list_navigation.py` | **PASS: 8 methods** |
| `python3 tests/check_channel_search_empty.py` | **PASS: 5 methods** |
| `python3 tests/check_channel_listing_source.py` | **PASS: 5 methods** |
| `python3 -m unittest discover -s tests -p 'check_xmltv*.py'` | **PASS: 31 methods**, including retained negative controls |
| Changed-file Python 3.8 AST grammar; `git diff --check` | **PASS** |
| `python3 tests/check_program_title_search.py --fixture 2026-11-25T12:00:00Z` | **PASS**, prints the reviewed eleven-channel XML fixture |

Total: **66 distinct focused methods**, not 66 native tests. Original invalid
regex-escape SyntaxWarning/DeprecationWarning messages and the channel test's
deprecated default SQLite adapter warning remain. Initial harness setup failed
for a missing `time` binding; it was corrected before the product baseline above.
Raw baseline failures, candidate output and warnings remain in the implementing
session's tool transcript; they are not silently converted into passes.

The new tests additionally pass real SQL result objects into extracted GUI
handlers/list rendering with inert controls: selected identity, menu/listing/
selection/Back, both sort modes, and history creation/reuse/dedup/removal/cancel.
Existing tests cover empty lists and sorting with distinct times. This does
**not** simulate native input dispatch, fonts, physical keyboard/mouse or pixels.

### Incomplete Toolkit gate

Current Toolkit development/debugging/validation/version-compatibility skills
were loaded. The execution permission layer refused the requested parent ledger
read, the managed-v2 version reference read and `kodi-toolkit discover .` before
execution. Consequently the current documented isolated interpreters could not
be verified/run. **No `stub-lanes`, six-stage validation or official addon-check
result is claimed for this candidate** on Matrix, Nexus, Omega or Piers. System
Python focused tests/grammar checks are not substitutes. No tool environment,
configuration or pinned dependency was altered or bypassed.

After access is authorized, use each release's documented current interpreter
for `-m kodi_agent_toolkit.cli stub-lanes`, then that **same interpreter** and
matching checker `--branch` for validation. Record exact Python/platform,
Kodistubs/mypy/checker versions, every stage and all warnings/errors. The branch
does not select stubs. Matrix static 19.5 is not native 19.4; Piers is preview
evidence only. Historical release static failures remain historical, not fresh
passes. See [exact 0.1.2 release coverage](beta-0.1.2.md) and
[release history](release-history.md).

## Directions for separately authorized native qualification

Nothing below was performed by this implementation task. Use **kodi-managed-lab**
with the current `kodi-mcp-testing` managed-v2 workflow, authenticated discovery,
owner lease and explicit generation. Use only an explicitly approved disposable
synthetic profile/workspace; this document grants no retained-profile access,
Reset, production/provider-settings changes or external-Kodi authorization.

1. Record exact source commit and native version/platform. Requested lanes are
   Nexus **20.5**, Omega **21.3**, Piers exact preview build, and Matrix **19.4**
   if available. Matrix #82 startup faults and Piers screenshot/input limits are
   separate blockers; preserve failures and stop rather than work around them.
2. In an already existing authorized fixture directory, generate XML immediately
   before each round (replace `FIXTURE_DIR` with that directory):

   ```sh
   python3 tests/check_program_title_search.py --fixture "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$FIXTURE_DIR/title-search.xml"
   ```

   The argument is explicit UTC and the output has `+0000` timestamps. Do not
   reuse the frozen November example as a current native feed. There are eleven
   channels, no external URLs, streams, provider accounts, artwork or rules.
3. With separately authorized synthetic setup only, use the local XMLTV file,
   zero offsets, optional XML sources disabled, all fixture channels visible,
   no channel-category restriction, listing hours **6**, days **1**. Import and
   verify actual parsed/stored programme dates/source/channel identities before
   testing search. Check current guide data independently, not just file mtime or
   an update acknowledgement. Do not Reset an existing profile to force this.
4. Compare baseline and candidate with equivalently newly dated data. Search each
   reported title, `Waterfall` and ASCII upper/lowercase variants. Expect the table
   above. With plot OFF candidate has two Waterfall results (`Fixture combined`
   and `Fixture subtitle`); plot ON adds `Fixture plot` and nothing else.
5. Using keyboard and mouse independently, inspect labels/details/channel/time,
   select the subtitle result, verify its selected identity/context, test Back,
   no-match and empty/cancel; create/reuse/remove history. Do not infer native
   focus/selection success from host tests. No playback or external stream is
   needed; if testing playback is separately approved, use only an owned local
   harmless fixture with distinguishable identity.
6. Regress Category `Fixture`, Channel `Fixture frontline`, Now/Next and sorted
   selection. Repeat synthetic visibility/category/source exclusions without
   altering real provider settings. Reducing previous-hours to **0** excludes
   these programmes from title search because they began 15 minutes earlier,
   while current Channel search can still find them: expected containment, not
   a regression. Restore synthetic settings after that control. Exact one-second
   boundaries use the deterministic host test, not a moving native clock.
7. Record managed status, actual GUI/focus, bounded logs and real pixels where
   available; distinguish deploy/install, launch dispatch and observed behavior.
   Preserve non-clean logs/blocked steps. Close and release the managed owner by
   the supported workflow. No public release, version bump or GitHub write.
