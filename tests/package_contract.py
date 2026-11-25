"""Shared source-only contracts, not a release builder or a Kodi API stub.

Historical objects are mandatory: never substitute HEAD, fetch, or skip silently.
See docs/test-maintenance.md for shallow-clone preparation and scope.
"""
import ast
from contextlib import contextmanager
from io import BytesIO
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ARTWORK_COMMIT = 'f936c0a514e0de126e62e24fd3d24b66b0c74097'
ARTWORK_TREE = 'c6d014c332f6d24b219f4976518dcf2221ae6a88'
FLOORS = {
    'xbmc.python': '3.0.0',
    'script.module.requests': '2.31.0',
    'script.module.dateutil': '2.8.2',
    'script.module.pytz': '2023.3.0+matrix.1',
    'script.module.pil': '5.1.0',
    'script.module.beautifulsoup4': '4.12.2',
}
# Explicit integration allowance, NOT a wildcard or automatic inventory refresh.
# The independently reviewed Favorites routing fix adds this one helper.
# Optional only because this tests-only branch is based on main before that fix.
OPTIONAL_PAYLOADS = {'favourites_navigation.py'}
# These two intentionally empty Python package markers are original payloads.
EMPTY_PACKAGE_MARKERS = {'resources/__init__.py', 'resources/lib/__init__.py'}
SOURCE_CACHE_DIRS = {'__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.cache'}


def git(*args):
    result = subprocess.run(['git', '-C', str(ROOT), *args],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env={'PATH': os.defpath})
    if result.returncode:
        raise AssertionError(
            'Required local Git evidence unavailable: git {}\n{}\n'
            'Use a full clone or explicitly fetch the pinned objects as described '
            'in docs/test-maintenance.md; tests never fetch or skip.'
            .format(' '.join(args), result.stderr.decode(errors='replace')))
    return result.stdout


def safe_path(path):
    parts = path.split('/')
    assert path and not PurePosixPath(path).is_absolute(), path
    assert all(part not in ('', '.', '..') for part in parts), path
    assert not any(c in path for c in ('\\', '\x00', ':')), path


@contextmanager
def git_snapshot(revision):
    """Export exact local tracked blobs, rejecting links/devices/path traversal.

    No source from the export is imported by this helper. Native entry points
    remain inert. The temporary fixture is cleaned even after a failed assertion.
    """
    raw = git('archive', '--format=tar', revision)
    with tempfile.TemporaryDirectory(prefix='tvguide-fixture-', dir=ROOT / 'tests') as directory:
        root = Path(directory)
        with tarfile.open(fileobj=BytesIO(raw)) as archive:
            for member in archive:
                path = member.name.rstrip('/') if member.isdir() else member.name
                safe_path(path)
                assert member.isdir() or member.isfile(), member.name
                destination = root / path
                if member.isdir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(archive.extractfile(member).read())
        yield root


def runtime(path):
    """The documented historical installer selection, not all repository files."""
    return path.startswith('resources/') or ('/' not in path and (
        path.endswith('.py') or path in ('addon.xml', 'changelog.txt', 'commands.txt',
                                        'LICENSE.txt', 'icon.png', 'fanart.jpg',
                                        'THIRD-PARTY-NOTICES.txt')))


def historical_payloads():
    # Derived only from the pinned immutable artifact, never the working tree.
    paths = git('ls-tree', '-r', '--name-only', ARTWORK_COMMIT).decode().splitlines()
    return {path for path in paths if runtime(path)}


def source_cache(path):
    """Generated checkout artifacts, never eligible for an installer inventory."""
    return (bool(set(PurePosixPath(path).parts) & SOURCE_CACHE_DIRS)
            or PurePosixPath(path).suffix.lower() in ('.pyc', '.pyo'))


def validate_payload_paths(paths, required=None, optional=OPTIONAL_PAYLOADS):
    """Check unprefixed package member names; do not silently discard extras."""
    required = historical_payloads() if required is None else required
    paths = list(paths)
    for path in paths:
        safe_path(path)
        assert not source_cache(path), 'Generated cache in package: ' + path
    actual = set(paths)
    assert len(paths) == len(actual), 'Duplicate package members'
    assert required <= actual, 'Missing payloads: {}'.format(sorted(required - actual))
    assert actual <= required | optional, 'Unreviewed payloads: {}'.format(
        sorted(actual - required - optional))


def validate_runtime_inventory(root):
    paths = []
    assert not (root / 'resources').is_symlink(), 'Runtime resources directory symlink'
    # Include untracked runtime candidates so damage cannot hide behind git ls-files.
    candidates = list(root.iterdir()) + list((root / 'resources').rglob('*'))
    for path in candidates:
        name = path.relative_to(root).as_posix()
        # Host imports and local test/type-check runs may create these. Ignore
        # only in the source scan: explicit package member lists reject them.
        if source_cache(name):
            continue
        if runtime(name):
            assert not path.is_symlink(), 'Runtime symlink: ' + name
            if path.is_file():
                assert path.stat().st_size or name in EMPTY_PACKAGE_MARKERS, (
                    'Empty runtime payload: ' + name)
                paths.append(name)
    required = set(historical_payloads())
    # Before integration the reviewed helper is allowed, not required. Once any
    # payload imports it, deleting it must fail just like deleting gui.py.
    optional_modules = {Path(path).stem: path for path in OPTIONAL_PAYLOADS}
    for path in paths:
        if path.endswith('.py'):
            tree = ast.parse((root / path).read_text('utf-8'), filename=str(root / path))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module]
                required.update(optional_modules[name] for name in names if name in optional_modules)
    validate_payload_paths(paths, required=required)
    return set(paths)


def validate_dependencies(manifest):
    requires = manifest.findall('requires')
    assert len(requires) == 1
    imports = list(requires[0])
    assert len(imports) == len(FLOORS), 'Exactly six required imports'
    assert {n.get('addon'): n.get('version') for n in imports} == FLOORS
    for node in imports:
        assert node.tag == 'import'
        assert node.get('optional', 'false') == 'false', node.attrib
        assert set(node.attrib) <= {'addon', 'version', 'optional'}, node.attrib


def validate_versions(root):
    version = ET.parse(root / 'addon.xml').getroot().get('version')
    assert re.fullmatch(r'\d+\.\d+\.\d+(?:~[a-z]+\d*)?', version or ''), version
    changelog = (root / 'changelog.txt').read_text('utf-8').splitlines()[0]
    assert changelog.startswith('version ' + version + ' '), changelog
    headline = (root / 'README.md').read_text('utf-8').splitlines()[0]
    assert headline.startswith('# TV Guide Fullscreen — ' + version + ' '), headline
    news = ET.parse(root / 'addon.xml').findtext(
        "extension[@point='xbmc.addon.metadata']/news")
    assert re.match(re.escape(version) + r'\s+[^:]+:', news or ''), news


def pyaes_notice(raw):
    """Protect the embedded complete license, not incidental AES code bytes."""
    return raw.split(b'####')[1]


def entrypoint_notice(raw):
    """The original attribution/GPL header ends before the first import."""
    return raw.split(b'\nimport ', 1)[0]
