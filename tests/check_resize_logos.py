"""Real Pillow PNG checks of the extracted function; no Kodi imports/dialogs."""
import ast
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from PIL import Image
from PIL import ImageOps

ROOT = Path(__file__).resolve().parents[1]


class ResizeLogos(unittest.TestCase):
    def check_logo(self, image, crop=None):
        tree = ast.parse((ROOT / 'ResizeLogos.py').read_text(encoding='utf-8'))
        function = next(node for node in tree.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == 'autocrop_image')
        for channels in (9, 6):
            with self.subTest(mode=image.mode, channels=channels):
                translated = []
                settings = []

                def translate(path):
                    translated.append(path)
                    return path

                def setting(key):
                    settings.append(key)
                    return str(channels)

                scope = dict(Image=Image, ImageOps=ImageOps,
                             xbmcvfs=SimpleNamespace(translatePath=translate),
                             ADDON=SimpleNamespace(getSetting=setting))
                exec(compile(ast.Module(body=[function], type_ignores=[]),
                             'ResizeLogos.py', 'exec'), scope)
                with tempfile.TemporaryDirectory(prefix='tvguide-logo-') as temp:
                    source = Path(temp) / 'source.png'
                    output = Path(temp) / 'output.png'
                    image.save(source)
                    original = source.read_bytes()
                    scope['autocrop_image'](str(source), str(output))
                    height = 450 // channels - 2
                    expected = image.crop(crop).convert('RGBA')
                    width = int(height * expected.width / expected.height)
                    expected = expected.resize((width, height), Image.LANCZOS)
                    with Image.open(output) as result:
                        self.assertEqual(result.mode, 'RGBA')
                        self.assertEqual(result.size, (width, height))
                        self.assertEqual(result.tobytes(), expected.tobytes())
                    self.assertEqual(source.read_bytes(), original)
                    self.assertEqual(translated, [str(source), str(output)])
                    self.assertEqual(settings, ['channels.per.page'])

    def test_blank_transparent(self):
        for color in ((0, 0, 0, 0), (90, 30, 10, 0)):
            self.check_logo(Image.new('RGBA', (12, 8), color))

    def test_zero_rgb_black(self):
        self.check_logo(Image.new('RGB', (12, 8), (0, 0, 0)))

    def test_ordinary_content(self):
        image = Image.new('RGBA', (12, 8), (0, 0, 0, 0))
        image.paste((200, 40, 20, 255), (2, 1, 10, 5))
        image.putpixel((4, 2), (20, 180, 50, 128))
        self.check_logo(image, (2, 1, 10, 5))

    def test_existing_white_background(self):
        image = Image.new('RGB', (12, 8), 'white')
        image.paste((200, 40, 20), (2, 1, 10, 5))
        self.check_logo(image, (2, 1, 10, 5))
        self.check_logo(Image.new('RGB', (12, 8), 'white'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
