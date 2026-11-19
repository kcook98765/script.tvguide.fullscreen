"""Bounded port checks: AST + extracted pure date/sqlite helpers, no Kodi imports.

No add-on module, stub, entry point, provider, GUI or service is imported/run.
Only the named stdlib-only functions below are compiled out of parsed source.
"""
import ast
import configparser
import datetime
from html import entities
import io
from pathlib import Path
import re
import sqlite3
import time
from types import SimpleNamespace
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def pure_function(tree, owner, name, namespace):
    parent = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == owner) if owner else tree
    node = next(n for n in parent.body if isinstance(n, ast.FunctionDef) and n.name == name)
    node.decorator_list = []
    code = ast.Module(body=[node], type_ignores=[])
    exec(compile(code, '<extracted-pure-' + name + '>', 'exec'), namespace)
    return namespace[name]


def check():
    runtime = list(ROOT.glob('*.py')) + list((ROOT / 'resources').rglob('*.py'))
    for path in runtime:
        text = path.read_text(encoding='utf-8')
        ast.parse(text, filename=str(path), feature_version=(3, 6))
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                assert (node.value.id, node.attr) not in {
                    ('xbmc', 'translatePath'), ('xbmc', 'LOGNOTICE'),
                    ('xbmc', 'LOGSEVERE'), ('xbmc', 'abortRequested')}, (path, node.lineno)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == 'ListItem':
                    assert len(node.args) <= 2, (path, node.lineno)
                    assert not {'iconImage', 'thumbnailImage'}.intersection(k.arg for k in node.keywords)
                if node.func.attr == 'ok':
                    assert len(node.args) <= 2, (path, node.lineno)
    print('PASS runtime AST: conservative Python 3.6 grammar and removed Kodi API/signature guards:', len(runtime))

    gui = (ROOT / 'gui.py').read_text()
    sort_keys = [node for node in ast.walk(ast.parse(gui)) if isinstance(node, ast.Lambda)
                 and 'order.index' in ast.get_source_segment(gui, node)]
    assert len(sort_keys) == 5
    for node in sort_keys:
        assert isinstance(node.body, ast.IfExp) and isinstance(node.body.body, ast.Tuple)
        assert isinstance(node.body.orelse, ast.Tuple)
    print('PASS all five category-order keys avoid Python2 mixed int/string comparison')

    tree = ast.parse((ROOT / 'source.py').read_text())
    namespace = {'datetime': datetime, 'time': time, 're': re, 'htmlentitydefs': entities}
    unescape = pure_function(tree, None, 'unescape2', namespace)
    assert unescape('Caf&#233; &amp; &#x1f4fa;') == 'Café &amp; 📺'
    # The parser normalizes to machine-local naive datetimes; freeze its offset
    # inputs at UTC without touching the process/host timezone.
    namespace['time'] = SimpleNamespace(daylight=0, timezone=0)
    parse_date = pure_function(tree, 'XMLTVSource', 'parseXMLTVDate', namespace)
    assert parse_date(None, '20261120123000 +0230') == datetime.datetime(2026, 11, 20, 10)
    assert parse_date(None, '20261120123000 -0530') == datetime.datetime(2026, 11, 20, 18)
    assert parse_date(None, '20261120123000') == datetime.datetime(2026, 11, 20, 12, 30)
    namespace['time'] = time
    adapt = pure_function(tree, 'Database', 'adapt_datetime', namespace)
    convert = pure_function(tree, 'Database', 'convert_datetime', namespace)
    stamp = datetime.datetime(2026, 11, 20, 12, 30)
    assert convert(str(adapt(stamp)).encode('ascii')) == stamp
    assert convert(b'not-a-date') is None
    connection = sqlite3.connect(':memory:')
    connection.execute('CREATE TABLE mapping (title TEXT, url TEXT)')
    title, url = 'Café 📺', 'plugin://fixture/été?q=1%2C2'
    connection.execute('INSERT INTO mapping VALUES (?, ?)', (title, url))
    assert connection.execute('SELECT * FROM mapping').fetchone() == (title, url)
    connection.close()
    print('PASS extracted pure entity/date/sqlite converter checks and Unicode sqlite TEXT roundtrip')

    # Real binary XML must reach ElementTree unchanged (including declarations).
    xml = '<?xml version="1.0" encoding="iso-8859-1"?><tv><channel id="é"><display-name>Café</display-name></channel></tv>'
    parsed = list(ET.iterparse(io.BytesIO(xml.encode('iso-8859-1')), events=('start', 'end')))
    assert parsed[0][1].find('channel/display-name').text == 'Café'
    wrapper = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'FileWrapper')
    wrapper_text = ast.get_source_segment((ROOT / 'source.py').read_text(), wrapper)
    assert 'readBytes(byteCount)' in wrapper_text and 'len(data)' in wrapper_text
    parser = configparser.RawConfigParser(strict=False)
    parser.optionxform = str
    parser.read_string('[fixture]\nCafé=' + url + '\n')
    assert parser.get('fixture', title.split()[0]) == url
    for path in ('notification.py', 'autoplay.py'):
        assert '.encode(' not in (ROOT / path).read_text()
    print('PASS binary XML declaration / mapping percent-escape controls and alarm text wiring')
    print('No Kodi/native execution; not provider, UI, AES or dependency acceptance')


if __name__ == '__main__':
    check()
