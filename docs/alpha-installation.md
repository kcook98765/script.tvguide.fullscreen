# Planned Alpha installation — not yet published

**Planned and unpublished.** There is no Alpha release asset to download yet.
Native qualifications are in progress; final per-version outcomes and static
results are pending. Do not treat a GitHub source archive, inherited tag or
development checkout as a validated installer.

The owner-decided initial scope is **Matrix 19.4, Nexus 20.5, Omega 21.3 and Piers
22 RC2**, using one common TV Guide ZIP, not a Nexus-first rollout. Piers is bounded
RC2 only. This is not stable, all-platform or full legacy-feature qualification.

## Planned installation flow — when a prerelease is available

1. Use a separate development/test Kodi setup, not your everyday profile.
   Preserve its settings, mappings and saved rules before any installation/update.
   Obtain the eventual GitHub **prerelease** asset and build notes.
   Match its exact tag, source/candidate revision, version and published SHA-256.
   No asset URL or checksum is available yet.
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

## Proposed version and release identity

The manifest is still **0.0.445**. **0.0.446~alpha1 is proposed only**, common to
all four versions and subject to owner approval. The [Kodi Wiki version-ordering
examples](https://kodi.wiki/view/Addon.xml#How_versioning_works) document `~alpha`
sorting before the corresponding unsuffixed version. The separate proposed Git
tag is **`v0.0.446-alpha1`**: `~` is valid in the Kodi version but **invalid in a
Git tag**. Neither the proposed tag nor the version change has been created.

The eventual common release asset is proposed as
**`script.tvguide.fullscreen-0.0.446~alpha1.zip`**, with exactly one
`script.tvguide.fullscreen/` root, SHA-256 and exact source/candidate build notes.
Owner approval and a rebuild with the approved version metadata are required
before publication. A private qualification ZIP at unchanged **0.0.445** is
separate from this proposed release and is not a published prerelease.

## Packaging and retained-install limits

The supplied pre-documentation clean runtime inventory is **317 files /
4,092,862 bytes before the latest changelog addition**; no release ZIP is available.
Final changelog/version edits will require new inventory/hashes. The planned ZIP
excludes `resources/lib/pytz`, tests, tools, docs, agent configuration, evidence,
logs, caches and bytecode. Official modules remain separately installed in Kodi.

Retained-copy development installations can contain the **317 reviewed files +
595 old unused vendor files**. Do not call that clean installation or assume a ZIP
update prunes leftovers. Do not delete files or uninstall on rule-bearing profiles
to force cleanliness; use a separate supported test installation for clean-install
evaluation.

The planned prerelease will identify one reviewed common ZIP, SHA-256,
exact tag/candidate build notes and actual results/limits for all four targets.
A GitHub prerelease is not repository availability. Never publish
private feed names/URLs, settings, credentials, private logs or unsanitized images.
See [current status](modernization-status.md) and [official pytz evidence](official-pytz.md).
