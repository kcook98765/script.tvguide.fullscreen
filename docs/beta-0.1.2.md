# TV Guide Fullscreen 0.1.2 Beta

This maintenance release restores the Stream Setup tabs in Default, Dark and
CatBar. Browse and Addons show their choices again when you switch to them.
Existing channel and stream mapping behavior is unchanged. See
[issue #79](https://github.com/kcook98765/script.tvguide.fullscreen/issues/79)
and the [changelog](../changelog.txt).

## Install or update

Follow the [installation instructions](../README.md#installation). TV Guide
keeps the same Kodi add-on ID and dependency requirements. Back up your settings
and channel mappings before updating. A fresh installation is unnecessary for a
normal same-ID update.

Use the [version-pinned GitHub prerelease](https://github.com/kcook98765/script.tvguide.fullscreen/releases/tag/v0.1.2-beta)
for the installable ZIP and checksum. For repository installation, use the
version your Kodi catalog currently advertises. Piers 22.x is a development
preview and is outside repository publication.

## Qualification

| Kodi | Observed navigation qualification |
| --- | --- |
| Omega 21.3 | **PASS** for Default, Dark and CatBar, including saved stream mappings and harmless local playback. |
| Nexus 20.5 | **PASS** for the focused Default workflow. |
| Matrix 19.4 | **BLOCKED** before Stream Setup rendered. Repeated native `libpython3.10` segmentation faults have an unclassified cause. See [#82](https://github.com/kcook98765/script.tvguide.fullscreen/issues/82). |
| Piers 22.0 RC2 preview | **PASS** for the focused UI through live noVNC. Managed screenshot capture remains blocked. |

These results cover the reviewed Stream Setup runtime change on Claw.
Sustained streaming, audio, optional timed notification delivery and timer-fired
AutoPlay are outside this maintenance qualification. Historical typing and
checker findings remain. The separate provider-response handling issue
[#80](https://github.com/kcook98765/script.tvguide.fullscreen/issues/80) remains open.

The [release history](release-history.md) records the earlier packages and
[artwork provenance](artwork-provenance.md) records the retained artwork.
