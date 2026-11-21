# Passive guide styling/layout overrides — first partial restoration

> Historical task record: old activation-blocker / whole-campaign UNRUN statements
> below are superseded by the [current overview](modernization-status.md).
> Original failures and feature-specific unverified limits remain; later core
> native evidence is not blanket acceptance of this feature.

Refs #14, #5, #7, #3, #1. This is **not compatibility with arbitrary existing
custom themes**, a native Kodi theme, or a complete skin format. It restores
practical local/profile styling of the existing bundled WindowXML layouts.
Other feature losses remain provisional; no permanent removal is decided here.

## Use / folder structure

1. In Appearance choose **Bundled Skin**: Default, Dark or CatBar. This remains
   the default, the reference layout, and the fallback on error.
2. Make your own copy of the chosen bundled skin outside the installed add-on.
   You may copy just the XML windows and PNGs you want to override. Keep the
   structure below. This code never downloads, installs, edits or deletes your
   originals. A nearby Python file is ignored, not loaded or grounds for refusal.
3. Set the existing **Skin Type** to Profile (legacy value 1) or Local folder
   (legacy value 2), and **User Skin Name**. Finally explicitly enable **Use
   passive styling/layout overrides**. The settings and fallback dialog link
   this web guide; development staging need not contain a `docs` directory.
   Old source/name/folder values are preserved but
   cannot opt you in automatically. Bundled (value 0) always uses bundled files.
4. Reopen the guide after an edit. If unsupported, a dialog explains the reason
   and says which bundled skin is used. Turn off the opt-in to return to bundled.

For Profile the root is the translated add-on profile, normally
`special://profile/addon_data/script.tvguide.fullscreen/`. For Local folder select
the directory **above** `resources/skins`, not the individual skin directory:

```text
<selected root>/
  resources/skins/Café 日本語/
    720p/
      script-tvguide-main.xml       # optional: customized bundled counterpart
      script-tvguide-menu.xml       # optional: same rule for the other windows
    media/
      tvg-program-nofocus.png       # optional: override known bundled texture
      My background 日本語.png     # optional: explicitly referenced by a layout
```

Spaces and ordinary Unicode work in the source skin directory and PNG names;
`My Skin` is also valid. The directory name is one component, at most 240 UTF-8
bytes, without slash/backslash, colon, NUL or control characters. Resource paths
are relative to `media`, at most seven components of the same size. No empty,
`.`/`..`, absolute, URL, drive, backslash, Kodi expression (`$[]`) or URI-escaped
(`%?#`) resource paths. Direct VFS/network roots, symlinks and Windows reparse
points are unsupported. Filesystem-mounted storage is treated as filesystem
input, not an asserted physical-local device. Permissions must allow local reads.

## Bounded useful subset

Each supplied XML window must retain the chosen bundle's **element hierarchy,
order, control IDs, types and attributes**. Omitted windows use the bundle;
windows absent from Dark/CatBar (currently VOD) use the bundled Default window.
Media precedence is **trusted Default → selected bundle → validated user PNG**.
Dark therefore retains Default's `tvg-menu-focus.png`, `tvg-menu-nofocus.png`,
`tvg-transparent.png`, `white.png`; CatBar retains the two missing menu textures.
Selected bundle images still win over Default; user PNG overrides are decoded
and snapshotted, never loaded directly from their source directories.
Missing required controls/types fail clearly; they are not guessed or remapped.
Start with the version of the bundled files shipped alongside this helper.

Permitted changes are **existing leaf text only**:

- `posx`, `posy`, `left`, `top`, `right`, `width`, `height`, `itemgap`: integer
  pixels -8192…8192; width/height must be 1…8192. This is not pixel acceptance
  on any native version; layouts can still be aesthetically unusable.
- Existing color properties: eight-digit hex ARGB. Font names: up to 64 literal
  characters without controls/`$`/bracket markup (installed font IDs, not files).
- Nonempty static captions: literal Unicode text, up to 512 characters, without
  controls, `$` or bracket markup. Existing dynamic/empty/boolean-marker labels
  stay fixed; they include values populated/read by the guide's Python code.
- Existing `onup/ondown/onleft/onright`: a decimal **existing control ID**.
  Arbitrary builtin strings, even apparently helpful navigation commands, fail.
- Existing texture leaf properties: relative `.png` files under `media`.
  Known bundled PNG filenames can also be overridden without editing the XML.
  The existing optional `tvg-alt-channel-column.png` Python-drawn texture works.

PNG input is actually decoded and re-encoded as one RGBA raster, not trusted by
extension. Maximum input/output file 4 MiB, 16 megapixels, one frame; no custom
GIF/JPEG/SVG/XBT/animations, metadata or appended data are forwarded. An unchanged
bundled GIF in a copied folder is fine; a modified non-PNG override fails. Snapshot
resources plus serialized layouts are limited to 32 MiB, each XML to 4 MiB and
12000 elements/64 nesting levels. Serialized output obeys the same file/total
byte caps. Unsupported/oversized selected data produces the fallback dialog.
Only referenced/known resources are read; unrelated files are ignored.

## Security / actual consumer contract

XML is **not inherently passive**. Reuses task04's official Kodi 19.4/20.5/21.3/
22 RC2 research in [#14](https://github.com/kcook98765/script.tvguide.fullscreen/issues/14),
especially `WindowXML.cpp`, `GUIControlFactory.cpp`, window/include/provider
consumers. The Matrix `WindowXML` active-skin-first lookup and `Skin.cpp`
`GetSkinPath` were rechecked for this implementation. The resource correction
also checked Matrix's [TextureManager.cpp](https://github.com/xbmc/xbmc/blob/19.4-Matrix/xbmc/guilib/TextureManager.cpp):
`HasTexture` checks loaded/image bundles then `GetTexturePath`'s registered image
paths; `Load` uses image/animation decoding. This is distinct from WindowXML
selection/action/include loading, not authority to load arbitrary texture URIs.
No broad research repeat or new four-version native qualification.

This is a constrained **diff against trusted bundled behavior**, not a blacklist
of a few dangerous tag names. Any added/reordered element, attribute, include,
template, content provider, action or changed unapproved text fails. In
particular new or changed onload/onclick/onfocus/onunload/ontextchange hooks,
action strings in navigation, and `plugin://` list content cannot enter. The
bundled guide's own fixed hooks, dynamic labels/artwork and existing VOD library
providers remain trusted application behavior; this task does not claim the
whole guide or installed Kodi skin is action-free or offline. No user-supplied
expression, provider, command, Python or include is enabled. Custom PNG resources
pass the separate data-only gate below.

Candidate XML is parsed as bounded UTF-8, without DTD/entities/processing
instructions. Approved leaf data is merged into the trusted parsed tree and
serialized, not reopened from the original later. Resource reads check file
identity/change and reject symlinks; custom PNG bytes are decoded before use.
Only this validated data is materialized in a fresh private temporary directory
for that Python invocation. No selected source root is passed to WindowXML.
Window filenames and output texture paths are generated ASCII names. Unique
window names avoid ordinary installed-skin files shadowing legacy guide window
names; captured static XML textures and Python-drawn EPG textures use the
snapshot's explicit paths. Trusted dynamic artwork expressions remain unchanged.
For an **unchanged property inherited from trusted original XML**, a missing
shipped image may retain its exact safe fixed raster basename and Kodi's normal
image lookup (loaded textures, installed-skin bundles/registered texture paths).
This does not select active-skin XML, includes or actions. The selected custom
source directory is never registered as a texture path. A newly supplied texture
reference, even one naming an image inherited elsewhere, still requires a
validated captured PNG; no new basename/URI/provider fallback is permitted.

In particular the shipped Default inventory does not resolve `menu-stream.png`,
`menu.png`, `tvguide-background-right.png`, `vod-focus.png`, `white50.png`.
Those unchanged trusted basenames are no longer forced to nonexistent generated
paths. Their actual image availability depends on native Kodi's installed image
resources, so this is source-level lookup preservation, **not rendering parity**.
Custom files supplied for those references are decoded/captured like other PNGs.
The snapshot stays alive for dialogs and is cleaned up on interpreter teardown;
an abrupt Kodi/process death can leave temp data for normal temp maintenance.
This does not defend against a hostile same-user process rewriting private Kodi
memory/temp files, or replace trust in Kodi, Pillow and the installed add-on.

## Preservation gaps and verification

Structural, reordered, include-based and complex legacy themes (including
unverified WMC/WhiteSnow), VFS/network themes, font packs, arbitrary visibility
expressions, new controls, attribute-based layout changes and non-PNG custom
resources are **temporarily unsupported gaps**, not permanent owner-approved
cuts. Existing user layouts are not migrated, overwritten, sanitized in place,
or declared malicious merely because they exceed this first subset. No remote
Python, profile code, command interpreter or automatic skin download is restored.

Focused `tests/check_custom_skins.py` imports only the new pure helper and Pillow;
it exercises real source directories, regenerated XML/PNG bytes, Unicode/spaces,
changed-source controls, hooks/providers/includes/path/symlink/control failures,
and extracted adapter/WindowXML handoffs as inert data/AST captures. No Kodi or
Kodistubs host imports. Existing safety/command/reminder/fixture regressions are
retained. Matrix 19.5-stub typing is not embedded Matrix 19.4 Python/native proof;
runtime library calls are deliberately Python 3.8-compatible. Toolkit CPython
3.12, syntax and source-level contracts do not qualify all native versions.

Initial `af83ca9` focused results: ten custom-skin tests, six reminder tests, four fixture
tests and the safety, Python3 and command-data scripts each exit 0. The Toolkit's
focused Matrix type stage passes the two new helpers; its API negative control
still fails with two expected extra-argument errors. It uses Kodistubs 19.0.3,
mypy 2.4.0, the reviewed validator-only Matrix annotation overlay and a Python
3.10 type target; separate AST checks plus library-API review cover the intended
Python 3.8 surface, not execution on an embedded 3.8 interpreter. Legacy escape
warnings remain. No full four-lane suite, new six-stage report, official checker,
package export or broad GUI typing run is claimed. The historical task03
type/checker failures in [the port notes](modernization-python3.md#checks-and-remaining-gates)
remain open; their old counts are not measurements of this changed snapshot.

The resource correction reproduces the missing-media/forced-missing-lookup
regressions before the fix, then passes twelve skin tests and narrow helper
typing. Tests use the actual Dark/CatBar/Default images and XML: Default fallback,
selected-image precedence, validated user PNG precedence and unchanged inherited
image lookup are checked separately. Newly supplied unresolved/URI/provider
textures remain rejected. These are pure data/AST checks, not native rendering.

Integration: original implementation base remains `9d0c225`; resource correction
is `e68a6e6d9755eefa08e4a8d2cbe805fb425ca39f`. A normal merge reconciles pinned
reviewed PR17 main `c96189c7a7a9d5ad20f8946d280166be0aa15e69` in this isolated
worktree. Its parents are `9d0c225` and reviewed PVR head
`d712b23aa04732fb4c4f0d07e3b89b8a5f7350e9`; its tree equals that PVR head.
Both PVR-safe callbacks/visible 4009 and snapshot/explicit-opt-in skin guards are
preserved. Metadata 4013 remains disabled exactly as on this pinned main, not
incidentally re-disabled by a skin change. Combined focused checks include the
twelve PVR tests as well as the twelve skin tests, reminder/fixture and prior
safety/command/Python3 scripts. Task10's metadata and task11's AutoPlay worktrees,
refs, private evidence and canonical source/index are untouched. Their later
integration must retain both safety boundaries; neither branch is merged here.

**All native stages remain blocked/unperformed.** Preserve Program + background
service. The installed Lab source-enable policy still excludes this mixed
manifest ([Lab #112](https://github.com/kcook98765/kodi-lab/issues/112#issuecomment-7023719173)).
No fresh Lab inspection/lifecycle/selection/import/deploy/enable/launch/settings,
UI/log/screenshot or production calls belong to this task. Task06 receipts,
workspace generation 0 and profile archives remain untouched. Native WindowXML
path resolution, Matrix pixel behavior, fonts, textures, controls, dialogs and
all-version interaction remain pending independently authorized acceptance.
