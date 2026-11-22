# Alpha 1 download and installation

**Historical Alpha 1 instructions.** For the proposed next version and current
limits see [0.1.0 Beta preparation](beta-0.1.0.md). Alpha 1's tag, assets and hash
below remain unchanged; no beta download or tested Alpha-to-beta migration is implied.

**Published GitHub prerelease:** [TV Guide Fullscreen 0.0.446 Alpha 1](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.0.446-alpha1).
This is not Kodi repository publication or expanded qualification.
As of **21 November 2026 UTC**, the independently reviewed bounded aggregate
retained-install native gate passed on all four initial-scope versions, with
explicit historical component reuse; the final static gate remains **FAIL**.
See [qualification and limits](modernization-status.md), including unverified
current Nexus/Omega LAN picture motion. Do not treat a GitHub source archive,
inherited tag or development checkout as a validated installer.

The owner-decided initial scope is **Matrix 19.4, Nexus 20.5, Omega 21.3 and Piers
22 RC2**, using one common TV Guide ZIP, not a Nexus-first rollout. Piers is bounded
RC2 only. This is not stable, all-platform or full legacy-feature qualification.

## Installation flow

1. Use a separate development/test Kodi setup, not your everyday profile.
   Preserve its settings, mappings and saved rules before any installation/update.
   Download the [installer `script.tvguide.fullscreen-0.0.446.alpha1.zip`](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.0.446-alpha1/script.tvguide.fullscreen-0.0.446.alpha1.zip)
   and [SHA256SUMS](https://github.com/kcook98765/script.tvguide.fullscreen/releases/download/v0.0.446-alpha1/SHA256SUMS)
   from the [Alpha 1 prerelease](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.0.446-alpha1),
   not GitHub's automatic source archives. Save both files in the same directory,
   keep the ZIP's published filename, and verify before installation:

   ```sh
   sha256sum -c SHA256SUMS
   ```

   Require `script.tvguide.fullscreen-0.0.446.alpha1.zip: OK`.
   The installer's SHA-256 is
   `dd10ec02c5a3e9c8f133c87c3cc0ac1806a650473cad7ef877554346daa903e7`.
   Match the release identity below; do not install if verification fails.
2. Keep the official Kodi repository available for the declared required modules:

   | Dependency | Minimum version |
   | --- | --- |
   | `xbmc.python` (provided by Kodi) | `3.0.0` |
   | `script.module.requests` | `2.31.0` |
   | `script.module.dateutil` | `2.8.2` |
   | `script.module.pytz` | `2023.3.0+matrix.1` |
   | `script.module.pil` | `5.1.0` |
   | `script.module.beautifulsoup4` | `4.12.2` |

   Kodi needs installed/enabled suitable dependencies; a catalog entry alone is
   not enough. The pytz suffix does not limit it to Matrix: the reviewed official
   catalogs carry that version for all four families. If manual installation is
   necessary, use supported native repository UI and verify the exact module's
   **Info**, official origin, ID and version before Install. Do not select an
   unrelated add-on to obtain its dependencies. Never bundle pytz in TV Guide.
3. Use Kodi's supported **Add-ons → Install from zip file** on the reviewed local
   TV Guide ZIP. It must contain exactly one `script.tvguide.fullscreen/` root,
   including its manifest, both entry points, runtime assets and license. If
   installation or source enablement is unavailable, ask your Kodi administrator.
   Keep both the Program and service, with explicit background-service consent.
4. Open **Configure** to select your listing source and mappings as described
   below. Then use **Add-ons → My add-ons →
   Program add-ons → TV Guide Fullscreen → Info → Run** for `addon.py`. Do not run
   `service.py` manually. Allow the initial listings import to finish, then select
   a mapped channel to watch; use ordinary **Stop** to return to the guide.

## First-use configuration

In the add-on's source settings, select a valid **XMLTV file or URL** containing
current listings. Set the **M3U mappings** source to a matching playlist: channel
identifiers must correspond to the XMLTV channels for the intended streams to be
mapped. Save settings, then use ordinary **Run**. Use sources you are entitled to
access; keep private feed names, endpoints, credentials and settings private.

If listings appear at the wrong time, check the feed's timezone and the applicable
XMLTV source offset before changing it. **Changing an offset alone does not
invalidate cached programmes.** If unchanged feed data remains cached, a normal
listings refresh/reimport is needed for the corrected offset to take effect;
closing and reopening alone may reuse the cache.

Before a forced refresh, back up settings, mappings and saved rules. Ensure the
channel-preservation option is enabled: a refresh that deletes channels can also
delete their associated reminder/AutoPlay rules. If using **Reset on Start** for
a listings refresh, turn it off after a successful import. This is a guide-data
refresh, not a reason to reset the Kodi profile or delete its database. See
[source-offset notes](xmltv-source-offsets.md) and [current limits](modernization-status.md).

## Published version and release identity

The manifest remains **`0.0.446~alpha1`**, common to all four versions.
The [Kodi Wiki version-ordering
examples](https://kodi.wiki/view/Addon.xml#How_versioning_works) document `~alpha`
sorting before the corresponding unsuffixed version. The immutable annotated Git
tag **`v0.0.446-alpha1`** points to
**`fc2f021ef6edc8c957e1ca91bfaa024d17c5f510`**: `~` is valid in the Kodi version
but **invalid in a Git tag**.

The public common installer ZIP is named
**`script.tvguide.fullscreen-0.0.446.alpha1.zip`**; the GitHub asset filename differs
from the Kodi manifest spelling. It has exactly one
`script.tvguide.fullscreen/` root, SHA-256 and exact source/candidate build notes.
It is built reproducibly from a clean committed candidate, using the explicit
317-path reviewed runtime inventory; private build notes retain source commit/tree,
per-file hashes, byte sizes, exclusions and ZIP SHA-256. Publication does not change
the frozen ZIP or add qualification evidence. The older private qualification ZIP
at **0.0.445** is separate and must not be renamed or have its checksum reused as
this release's identity.

## Packaging and retained-install limits

The prior clean qualification export was **317 files / 4,093,191 bytes**, including
the 329-byte changelog addition. This candidate retains those **317 paths**,
totaling **4,093,446 logical bytes**; only manifest/changelog payloads change,
with their own inventory/hashes. The published ZIP
excludes `resources/lib/pytz`, README, tests, tools, docs, configuration,
agent/development/CI files, reports, evidence,
logs, caches and bytecode. Root GPL and embedded third-party notices remain in
the payload. The reference-only `docs/pytz-LICENSE.txt` need not be added: no pytz
implementation is bundled, and the separately installed official module carries
its own notice. Official modules remain separately installed in Kodi.

The prior all-four native qualification used retained installations with **317
reviewed files + 595 unchanged unused old vendor files**. A private **0.0.445**
qualification preview is not a release installer or proof of native clean
installation.
Do not assume a ZIP update prunes leftovers. Do not delete files or uninstall on
rule-bearing profiles to force cleanliness; use a separate supported test
installation for clean-install evaluation.

### Representative clean-install smoke — PASS on Nexus 20.5 only

The **actual `0.0.446~alpha1` candidate ZIP** passed ordinary Kodi **Install from
zip file** in a new, genuinely clean, isolated **Nexus 20.5** environment; this was
not source-copy deployment. The installed Alpha was enabled. Kodi automatically
installed required official requests **2.31.0**, dateutil **2.8.2**, pytz
**2023.3.0+matrix.1** and BeautifulSoup **4.12.2**; PIL **5.1.0** was already bundled
with that Kodi environment, not bundled in the TV Guide ZIP.

Ordinary Program **Info → Run**, after synthetic XMLTV configuration, displayed
**two visible fixture channels and two programmes**, with titles, times and
description. Codex independently viewed the populated guide. **Actual background
service work also independently passed** after one ordinary restart of the same disposable instance:
the background update started and finished, and its saved update timestamp
advanced. The service was not executed manually. This is separate work evidence,
not an inference from enabled state or foreground parsing. Final Stop exited
gracefully with no forced kill. **Codex accepted the complete bounded installation
smoke after independent stopped-file, provenance and log review.**

All **317 installed file payloads and modes** matched the tested ZIP, all **69
catalogs** were preserved, and no `resources/lib/pytz` remained; the only extra
runtime files were generated bytecode. Required downloaded modules were enabled
with official Kodi repository origin; the separate pytz module's **611 files**
matched the reviewed official package. Complete current and previous logs had no
`ImportError`, `ModuleNotFoundError` or Python traceback, but **were not clean**:
audio/environment errors and existing syntax warnings remained.

This is one representative clean Nexus installation, not clean-install testing on
all four versions, a new playback/timer qualification, or proof that an update
prunes old vendor files. No original retained profile may be reset, uninstalled
or pruned to manufacture cleanliness. The candidate's 317 runtime payloads remain
frozen; this checkpoint changes nonpackaged documentation only.

The [published prerelease](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.0.446-alpha1)
identifies one reviewed common ZIP, SHA-256, exact tag/candidate build notes and
actual results/limits for all four targets. A GitHub prerelease is not Kodi
repository availability; no Kodi repository publication has occurred. Never publish
private feed names/URLs, settings, credentials, private logs or unsanitized images.
See [current status](modernization-status.md) and [official pytz evidence](official-pytz.md).
