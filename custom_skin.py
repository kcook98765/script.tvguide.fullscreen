"""Bounded edits to trusted bundled WindowXML, never a general skin interpreter.

Python 3.8 runtime; no Kodi imports. See docs/custom-guide-skins.md for the
deliberately narrow contract. User source is read only, never a WindowXML root.
"""
import io
import hashlib
import os
from pathlib import Path
import re
import stat
import tempfile
import uuid
import xml.etree.ElementTree as ET
from typing import Dict


BUNDLED = ('Default', 'Dark', 'CatBar')
MAX_FILE = 4 * 1024 * 1024
MAX_TOTAL = 32 * 1024 * 1024
TEXTURES = frozenset(('texture', 'texturebg', 'texturefocus', 'texturenofocus',
                      'bordertexture', 'lefttexture', 'midtexture', 'righttexture'))
GEOMETRY = frozenset(('posx', 'posy', 'left', 'top', 'right', 'width', 'height', 'itemgap'))
COLORS = frozenset(('textcolor', 'focusedcolor', 'selectedcolor', 'shadowcolor', 'colordiffuse'))
NAVIGATION = frozenset(('onup', 'ondown', 'onleft', 'onright'))


class SkinError(ValueError):
    """Unsupported custom data: caller must notify and use a bundled skin."""


def local_path(value: str) -> Path:
    # A translated special://profile path may be supplied by the Kodi adapter.
    if not value or '://' in value or value.startswith(('//', '\\\\')):
        raise SkinError('Choose a local filesystem folder, not a VFS/network URL.')
    path = Path(value)
    if not path.is_absolute():
        raise SkinError('The custom skin folder must be an absolute local path.')
    return path


def _component(value: str) -> bool:
    try:
        size = len(value.encode('utf-8'))
    except UnicodeError:
        return False
    return (0 < size <= 240 and value not in ('.', '..') and
            not any(c in value for c in '/\\:') and
            not any(ord(c) < 32 or 127 <= ord(c) <= 159 for c in value))


def _parts(relative: str):
    parts = relative.split('/')
    if (len(parts) > 8 or not all(_component(p) for p in parts) or
            any(c in relative for c in '$[]%?#')):
        raise SkinError('Resource traversal/absolute paths are not supported.')
    return parts


def _plain_path(root: Path, relative: str) -> Path:
    path = root.joinpath(*_parts(relative))
    # Check every ancestor, including the selected root. No recursive traversal
    # of unrelated files (nearby Python is not a reason to refuse a passive skin).
    for component in (path,) + tuple(path.parents):
        if component.is_symlink():
            raise SkinError('Symlinked skin folders/resources are not supported.')
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        if getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400):
            raise SkinError('Reparse-point skin folders/resources are not supported.')
    return path


def _read(root: Path, relative: str) -> bytes:
    path = _plain_path(root, relative)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_FILE:
        raise SkinError(relative + ': expected a regular file of at most 4 MiB.')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(str(path), flags)
    with os.fdopen(fd, 'rb') as handle:
        opened = os.fstat(handle.fileno())
        raw = handle.read(MAX_FILE + 1)
        after = os.fstat(handle.fileno())
    current = _plain_path(root, relative).lstat()
    def identity(info):
        return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
    if (not stat.S_ISREG(opened.st_mode) or len(raw) > MAX_FILE or
            any(identity(s) != identity(before) for s in (opened, after, current))):
        raise SkinError(relative + ': source changed while being read; reopen the guide.')
    return raw


def _xml(raw: bytes) -> ET.Element:
    # UTF-8 only, no DTD/entity expansion, processing instructions or alternate
    # encodings interpreted differently by ElementTree and Kodi's TinyXML.
    try:
        text = raw.decode('utf-8-sig')
        text = re.sub(r'\A\s*<\?xml\s+[^?]*\?>', '', text, count=1)
        if '<!' in text:
            # Comments are harmless but strip them before rejecting declarations.
            text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
        if '<!' in text or '<?' in text:
            raise SkinError('XML declarations/entities/processing instructions are unsupported.')
        root = ET.fromstring(text)
        if sum(1 for _ in root.iter()) > 12000:
            raise SkinError('Layout exceeds 12000 XML elements.')
        pending = [(root, 1)]
        while pending:
            node, depth = pending.pop()
            if depth > 64:
                raise SkinError('Layout exceeds 64 levels of XML nesting.')
            pending.extend((child, depth + 1) for child in node)
        return root
    except (UnicodeError, ET.ParseError) as exc:
        raise SkinError('Expected a well-formed UTF-8 bundled-layout copy.') from exc


def _literal(value: str) -> bool:
    return len(value) <= 512 and not any(c in value for c in '$[]') and all(
        ord(c) >= 32 and not 127 <= ord(c) <= 159 for c in value)


def _layout(reference: ET.Element, candidate: ET.Element) -> ET.Element:
    """Merge only approved leaf data into the trusted parsed reference tree."""
    ids = {e.get('id') for e in reference.iter('control') if e.get('id')}
    def merge(base, user):
        if (base.tag != user.tag or base.attrib != user.attrib or len(base) != len(user)):
            raise SkinError('Layout structure/control IDs/types/attributes must match the selected bundled skin.')
        if (user.tail or '').strip() != (base.tail or '').strip():
            raise SkinError('Text outside layout properties is unsupported.')
        old, new = (base.text or '').strip(), (user.text or '').strip()
        if old != new:
            tag = base.tag
            valid = False
            if not len(base):
                if tag in GEOMETRY:
                    valid = bool(re.fullmatch(r'-?[0-9]{1,4}', new))
                    if valid:
                        valid = -8192 <= int(new) <= 8192
                        if tag in ('width', 'height'):
                            valid = 1 <= int(new) <= 8192
                elif tag in COLORS:
                    valid = bool(re.fullmatch(r'[0-9A-Fa-f]{8}', new))
                elif tag == 'font':
                    valid = 0 < len(new) <= 64 and _literal(new)
                elif tag in NAVIGATION:
                    valid = new in ids and bool(re.fullmatch(r'[0-9]{1,7}', new))
                elif tag == 'label':
                    # Preserve empty/dynamic fields and boolean marker labels
                    # consumed by Python, not just rendered as captions.
                    valid = bool(old) and old.lower() not in ('true', 'false') and '$' not in old and _literal(new)
                elif tag in TEXTURES:
                    valid = new.endswith('.png')
                    _parts(new)  # resources are read/decoded separately
            if not valid:
                raise SkinError('Unsupported change to <' + str(tag) + '>; only passive leaf styling is supported.')
            base.text = new
        for left, right in zip(base, user):
            merge(left, right)
    merge(reference, candidate)
    return reference


def _png(raw: bytes) -> bytes:
    # Extension alone is not validation. Decode then re-encode a single bounded
    # raster; discard metadata and appended bytes, never pass source bytes on.
    from PIL import Image
    try:
        with Image.open(io.BytesIO(raw)) as image:
            if (image.format != 'PNG' or getattr(image, 'n_frames', 1) != 1 or
                    image.width * image.height > 4096 * 4096):
                raise SkinError('Custom textures must be single-frame PNGs, at most 16 megapixels.')
            image.load()
            output = io.BytesIO()
            raster = image.convert('RGBA')
            raster.info.clear()
            raster.save(output, format='PNG')
            result = output.getvalue()
            if len(result) > MAX_FILE:
                raise SkinError('Decoded PNG exceeds the 4 MiB texture limit.')
            return result
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        raise SkinError('Custom texture is not a supported bounded PNG.') from exc


class Snapshot:
    def __init__(self, directory: tempfile.TemporaryDirectory, skin: str,
                 filenames: Dict[str, str], textures: Dict[str, str]):
        self.directory = directory  # keep alive until this Python invocation ends
        self.path = directory.name + os.sep
        self.skin = skin
        self.filenames = filenames
        self.textures = textures


def prepare(addon_root: str, source_root: str, name: str, bundled: str,
            temp_root: str) -> Snapshot:
    """Snapshot exact validated data, with bundled fallback for omitted layouts.

    The returned directory contains only known XML files and bounded resources;
    neither the selected root nor unchecked extras are ever given to WindowXML.
    """
    if bundled not in BUNDLED or not _component(name):
        raise SkinError('Skin name must be one local directory name (up to 240 UTF-8 bytes; no separators or controls).')
    source = local_path(source_root)
    # Source names are filesystem data only, never Kodi expressions/filenames.
    # Unlike resource references they may contain literal $, [] or % as well.
    source = source / 'resources' / 'skins' / name
    _plain_path(source, '720p')
    if not source.is_dir():
        raise SkinError('Missing resources/skins/<User Skin Name> folder.')
    bundle = Path(addon_root) / 'resources' / 'skins' / bundled
    layouts = {}  # type: Dict[str, ET.Element]
    original_texts = {}
    payload = {}  # type: Dict[str, bytes]
    # Copy a known bundle inventory, never recursively copy the selected folder.
    windows = {p.name: p for p in (Path(addon_root) / 'resources/skins/Default/720p').glob('*.xml')}
    windows.update({p.name: p for p in (bundle / '720p').glob('*.xml')})
    for filename, path in sorted(windows.items()):
        base = _xml(path.read_bytes())
        original_texts[filename] = [node.text for node in base.iter()]
        relative = '720p/' + path.name
        user_path = _plain_path(source, relative)
        if user_path.exists():
            try:
                base = _layout(base, _xml(_read(source, relative)))
            except SkinError as exc:
                raise SkinError(path.name + ': ' + str(exc)) from exc
        layouts[path.name] = base
    total = 0
    for path in sorted((bundle / 'media').iterdir()):
        if path.is_file():
            relative = 'media/' + path.name
            user_path = _plain_path(source, relative)
            raw = path.read_bytes()
            if user_path.exists():
                user_raw = _read(source, relative)
                if path.suffix == '.png':
                    raw = _png(user_raw)
                elif user_raw != raw:
                    raise SkinError('Only PNG texture overrides are supported; leave other bundled assets unchanged.')
            payload[relative] = raw
            total += len(raw)
            if total > MAX_TOTAL:
                raise SkinError('Skin resources exceed the 32 MiB snapshot limit.')
    # Existing optional Python-drawn channel-column texture, not a new loader.
    optional = 'media/tvg-alt-channel-column.png'
    if _plain_path(source, optional).exists() and optional not in payload:
        payload[optional] = _png(_read(source, optional))
        total += len(payload[optional])
    # Only static PNG references can be customized; dynamic references remain
    # the exact trusted bundled expressions, not new user-provided providers.
    for layout in layouts.values():
        for node in layout.iter():
            value = (node.text or '').strip()
            if node.tag in TEXTURES and value.endswith('.png') and '$' not in value:
                relative = 'media/' + value
                _plain_path(source, relative)
                if relative not in payload:
                    path = _plain_path(source, relative)
                    if path.exists():
                        payload[relative] = _png(_read(source, relative))
                        total += len(payload[relative])
                        if total > MAX_TOTAL:
                            raise SkinError('Skin resources exceed the 32 MiB snapshot limit.')
                    # Inherited missing textures stay missing in the snapshot;
                    # a NEW missing texture is rejected below.
    # Check every changed texture reference is actually in the snapshot.
    for filename, layout in layouts.items():
        for old_text, new in zip(original_texts[filename], layout.iter()):
            if new.tag in TEXTURES and new.text != old_text and 'media/' + (new.text or '') not in payload:
                raise SkinError(filename + ': missing custom PNG texture.')
    if total + sum(len(ET.tostring(v)) for v in layouts.values()) > MAX_TOTAL:
        raise SkinError('Skin resources exceed the 32 MiB snapshot limit.')
    directory = tempfile.TemporaryDirectory(prefix='tvguide-passive-', dir=str(local_path(temp_root)))
    try:
        token = uuid.uuid4().hex
        skin = 'Passive-' + token
        root = Path(directory.name) / 'resources' / 'skins' / skin
        (root / '720p').mkdir(parents=True)
        (root / 'media').mkdir()
        textures = {}
        for relative, raw in payload.items():
            # Resource names (including Unicode/spaces) identify INPUT only.
            # Kodi receives generated ASCII paths, never URI/expression syntax
            # derived from a custom filename.
            digest = hashlib.sha256(relative.encode('utf-8')).hexdigest()
            path = root / 'media' / (digest + Path(relative).suffix)
            path.write_bytes(raw)
            textures[relative[len('media/'):]] = str(path)
        filenames = {}
        written = total
        for filename, layout in layouts.items():
            # Unique names avoid Kodi's active-skin-first XML lookup selecting a
            # different unchecked file with the legacy guide window filename.
            unique = token + '-' + filename
            filenames[filename] = unique
            for node in layout.iter():
                value = (node.text or '').strip()
                if node.tag in TEXTURES and value not in ('', '-') and '$' not in value:
                    # Even inherited missing bundled images stay confined to
                    # this root, not a similarly named active-theme resource.
                    _plain_path(source, 'media/' + value)
                    missing = 'missing-' + hashlib.sha256(value.encode('utf-8')).hexdigest() + '.png'
                    node.text = textures.get(value, str(root / 'media' / missing))
            xml_bytes = ET.tostring(layout, encoding='utf-8', xml_declaration=True)
            written += len(xml_bytes)
            if len(xml_bytes) > MAX_FILE or written > MAX_TOTAL:
                raise SkinError('Serialized skin exceeds the 4 MiB/file or 32 MiB snapshot limit.')
            (root / '720p' / unique).write_bytes(xml_bytes)
        return Snapshot(directory, skin, filenames, textures)
    except Exception:
        directory.cleanup()
        raise
