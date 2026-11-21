"""Focused import/conversion check against an explicitly supplied official lib.

Run with Python -I -S -B and the extracted script.module.pytz/lib directory as
the sole argument. No installation, entry-point import, Kodi, provider or DB use.
Package URL/SHA review belongs to the accompanying evidence, not this test.
"""
import ast
import datetime
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def check():
    assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
    assert len(sys.argv) == 2, 'Supply the reviewed official module lib directory'
    library = Path(sys.argv[1]).resolve(strict=True)
    assert (library / 'pytz/__init__.py').is_file()
    assert not (ROOT / 'resources/lib/pytz').exists()
    assert 'pytz' not in sys.modules
    sys.path.insert(0, str(library))
    tree = ast.parse((ROOT / 'source.py').read_text())
    imports = [n for n in tree.body
               if (isinstance(n, ast.Import) and any(a.name == 'pytz' for a in n.names))
               or (isinstance(n, ast.ImportFrom) and n.module == 'pytz')]
    assert [ast.unparse(n) for n in imports] == ['import pytz', 'from pytz import timezone']
    namespace = {'datetime': datetime, 're': re, 'time': SimpleNamespace(timezone=0)}
    exec(compile(ast.Module(body=imports, type_ignores=[]), 'source.py imports', 'exec'), namespace)
    pytz = namespace['pytz']
    assert Path(pytz.__file__).resolve() == library / 'pytz/__init__.py'
    assert namespace['timezone'] is pytz.timezone
    manifest = ET.parse(ROOT / 'addon.xml')
    dependency = manifest.findall("requires/import[@addon='script.module.pytz']")
    assert len(dependency) == 1
    assert dependency[0].attrib == {'addon': 'script.module.pytz', 'version': '2023.3.0+matrix.1'}
    for path in list(ROOT.glob('*.py')) + list((ROOT / 'resources').rglob('*.py')):
        assert 'resources.lib.pytz' not in path.read_text(), path
    print('PASS vendor physically absent; real source imports from:', pytz.__file__)
    print('Official module Python version:', pytz.__version__, 'tzdata:', pytz.OLSON_VERSION)
    # Execute only the two existing pure conversion methods, with a deterministic
    # local UTC offset. No enclosing source class/constructor/provider is run.
    for name in ('TVGUKSource', 'FixturesSource'):
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'local_time')
        exec(compile(ast.Module(body=[method], type_ignores=[]), 'source.py ' + name, 'exec'), namespace)
        for month, clock, utc_hour in ((1, '12:30pm', 12), (7, '12:30pm', 11), (7, '12:30am', 23)):
            result = namespace['local_time'](None, clock, 2026, month, 15)
            expected = datetime.datetime(2026, month, 15, tzinfo=pytz.utc)
            if clock.endswith('am'):
                expected -= datetime.timedelta(days=1)
            expected = expected.replace(hour=utc_hour, minute=30)
            assert result == expected, (name, clock, result, expected)
        print('PASS', name, 'ordinary winter/summer/noon/midnight localize/normalize conversions')
    print('NOT native dependency installation, guide/XMLTV startup or scheduler acceptance')


if __name__ == '__main__':
    check()
