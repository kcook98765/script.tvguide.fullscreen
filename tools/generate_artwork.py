"""Original geometric TV/guide artwork, created by OpenCode under owner direction.

SPDX-License-Identifier: GPL-2.0-or-later
No external images, fonts, logos, randomness or network inputs. Run from any cwd
with Pillow installed. Fixed RGB geometry and encoder options; byte reproduction
requires the same Pillow/libjpeg/zlib versions (recorded in campaign evidence).
Only the two root promotional assets are written; never used by Kodi at runtime.
"""
import hashlib
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw


def artwork():
    """Return encoded assets without reading files or writing anything."""
    result = {}
    for name, size, box, unit in (
        ('icon.png', (512, 512), (48, 88, 464, 392), 8),
        ('fanart.jpg', (1920, 1080), (360, 180, 1560, 852), 20),
    ):
        image = Image.new('RGB', size, (15, 25, 42))
        draw = ImageDraw.Draw(image)
        x0, y0, x1, y1 = box
        draw.rounded_rectangle(box, radius=unit * 3, fill=(54, 79, 103))
        draw.rounded_rectangle((x0 + unit, y0 + unit, x1 - unit, y1 - unit),
                               radius=unit * 2, fill=(22, 39, 59))
        # Guide header, channel column, and unequal programme blocks: no text.
        left, top = x0 + unit * 3, y0 + unit * 3
        right, bottom = x1 - unit * 3, y1 - unit * 3
        gap = unit
        row = (bottom - top - gap * 3) // 4
        draw.rectangle((left, top, right, top + row), fill=(78, 196, 191))
        for index, split in enumerate((0.42, 0.63, 0.32)):
            y = top + (row + gap) * (index + 1)
            channel_end = left + (right - left) // 6
            start = channel_end + gap
            cut = start + int((right - start) * split)
            draw.rectangle((left, y, channel_end, y + row), fill=(78, 112, 143))
            draw.rectangle((start, y, cut - gap, y + row),
                           fill=(234, 176, 87) if index == 1 else (65, 139, 162))
            draw.rectangle((cut, y, right, y + row), fill=(45, 89, 120))
        # Simple rectangular pedestal completes the television silhouette.
        center = size[0] // 2
        draw.rectangle((center - unit * 2, y1, center + unit * 2, y1 + unit * 3),
                       fill=(54, 79, 103))
        draw.rounded_rectangle((center - unit * 9, y1 + unit * 3,
                                center + unit * 9, y1 + unit * 5),
                               radius=unit, fill=(78, 112, 143))
        output = BytesIO()
        if name.endswith('.png'):
            image.save(output, format='PNG', optimize=False, compress_level=9)
        else:
            image.save(output, format='JPEG', quality=95, subsampling=0,
                       optimize=False, progressive=False)
        result[name] = output.getvalue()
    return result


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    for name, raw in artwork().items():
        (root / name).write_bytes(raw)
        print(hashlib.sha256(raw).hexdigest(), name, len(raw), 'bytes')
