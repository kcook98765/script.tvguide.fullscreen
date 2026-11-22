# Artwork provenance — 0.1.1 Beta successor

This is a specific correction for the successor, not a blanket legal/rights
certification, repository admission or invented owner decision. Codex selected
the owner-authorized omission fallback after individually visually inspecting all five actual
screenshots and the Earth icon/fanart from published 0.1.0. Native recapture would
require unnecessary runtime setup solely for promotional images. No new Kodi
capture, simulated screenshot, external photo or replacement sports art is used.
Public 0.1.0 Beta/Alpha 1 and all historical evidence remain unchanged.

## Screenshot dispositions

Paths below are under `resources/screenshots/`. Published source baseline:
`c19f256333efbe7af12418312f17e00f99792dc2`.

| Image | Successor disposition and specific basis |
| --- | --- |
| `fullscreen-guide.png` | Omitted from source/package and current manifest/README list: third-party sports composite, no demonstrated redistribution basis. |
| `programme-actions.png` | Omitted from source/package and current manifest/README list: third-party sports composite, no demonstrated redistribution basis. |
| `on-now.png` | Omitted from source/package and current manifest/README list: third-party sports composite, no demonstrated redistribution basis. |
| `search-results.png` | Omitted from source/package and current manifest/README list: third-party sports composite, no demonstrated redistribution basis. |
| `channel-management.png` | Retained exact bytes: owner-authored actual Nexus 20.5 capture; ordinary channel labels/UI, no separately identified artwork blocker in Codex's visual review. Retained as project screenshot under the project's GPL-2.0-or-later redistribution basis, not a claim of rights over channel names/marks. |

The retained capture remains **1280×720 RGB PNG**, 36,778 bytes. It is historical
development UI, not a new 0.1.1 native observation. Original capture history is
preserved in the historical source/release and private
`screenshots-beta-20261121` capture index/reports; omissions do not rewrite that
history. Labels are not an endorsement or content entitlement.

## Root icon and fanart — original procedural geometry

The old Earth-image source/license evidence is insufficient. **No license is
invented for those old images.** They are replaced, not relicensed. The successor
retains the filenames and dimensions needed by existing runtime resource
references, without copying the Earth silhouette or composition.

[tools/generate_artwork.py](../tools/generate_artwork.py) creates new rectangular
TV/guide-grid artwork from fixed geometry and colors only. Created by **OpenCode
under owner direction** for this project; no invented human copyright attribution.
The generator and its original outputs are offered under the project's
**GPL-2.0-or-later** redistribution basis (see [LICENSE.txt](../LICENSE.txt) and
retained v2-or-later source notices). No external image/font input, text, logo,
brand mark, photograph, network input, randomness or copied upstream composition.
These are promotional artwork, **not Kodi screenshots**.

Reproduce from the source checkout with Pillow installed:

```sh
python3 -I -B tools/generate_artwork.py
```

Recorded encoders: CPython 3.12.3, Pillow 12.3.0, libjpeg API 6.2, zlib 1.3.
PNG compress level 9; JPEG quality 95, subsampling 0, non-progressive, no optimize.
Fixed geometry is deterministic; exact encoded-byte reproduction requires the
same encoder toolchain. The generator is source-only and excluded from installers.

### SHA-256 review identities

| Retained/new source asset | Bytes | SHA-256 |
| --- | ---: | --- |
| `icon.png` (512×512 opaque RGB PNG) | 2106 | `d98b03eca9634ecdb880df30f82053169e22522b53e34b2978f5e70194c5bcef` |
| `fanart.jpg` (1920×1080 RGB JPEG) | 119353 | `9d33b3b1a0615eebd508f6b58c33c13859d851461aac7b80f9d75d7df509fbb0` |
| `resources/screenshots/channel-management.png` | 36778 | `8cb237ffa11107047553a3859683c173a5ab3f8ebb6d4e6278009aa48a037bd8` |
| `tools/generate_artwork.py` | 3024 | `32878038e8c44877aa925008883c06c44e533a10e06be1b554729a171047c2eb` |

The evidence asset audit also records old Earth and four omitted-image hashes;
no omitted bytes are redistributed in the successor installer. The installer
inventory records each included payload's Git blob/hash independently.

## Retained ordinary skin UI — all 166 images

All **166** images under `resources/skins/` remain exact published bytes. Codex
reviewed the retained upstream GPL/credits history for this ordinary skin UI;
that is the recorded redistribution basis, not new authorship by OpenCode or an
automatic inference from file extension. Local byte comparison also matches all
166 against retained upstream commit
`565d9b4b407e534bff0ae9fec0661c1df0c211fe` (primaeval, 2017-06-02). The retained
initial upstream commit `b17351383fe6825b6708bd0361dbb1acbaee84d6` carries the
root GPL license; `addon.py`/`service.py` preserve Tommy Winther, Thomas Geppert
(bluezed), primaeval and GPL v2-or-later source notices. The manifest disclaimer,
contributor list and README attribution remain verbatim. This upstream history
and credits basis for ordinary UI is distinct from the insufficient Earth/sports
image evidence; GPL presence alone is not asserted to clear unrelated content.

`LICENSE.txt` and `THIRD-PARTY-NOTICES.txt` remain byte-identical. The complete
Raymond Hettinger OrderedDict MIT notice/provenance and the separate Marti
Raudsepp pyaes MIT notice remain unchanged. No upstream credit/license is removed
or assigned to the owner. Runtime logos fetched from user-configured sources,
TV feeds, programmes and third-party services still require their own rights;
this artwork correction supplies none of those permissions.
