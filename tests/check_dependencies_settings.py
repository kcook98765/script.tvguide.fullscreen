"""Source/data-only dependency and legacy-settings contracts; no Kodi imports.

Only the stdlib-only catchup predicate and isolated selection ASTs are executed.
No entry point, settings action, provider, profile or dependency is executed.
"""
import ast
import copy
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BASE = '6d1b9162289ccc20c3ba089302dc3a149150d0be'
FLOORS = {
    'xbmc.python': '3.0.0',
    'script.module.requests': '2.31.0',
    'script.module.dateutil': '2.8.2',
    'script.module.pil': '5.1.0',
    'script.module.beautifulsoup4': '4.12.2',
}


def baseline(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT, text=True)


def settings(text):
    return {node.get('id'): node for node in ET.fromstring(text).iter('setting') if node.get('id')}


def bad_defaults(nodes):
    errors = []
    for key, node in nodes.items():
        kind, value = node.get('type'), node.get('default')
        if kind == 'enum' and value is not None:
            options = (node.get('values') or node.get('lvalues')).split('|')
            if not value.isdigit() or not 0 <= int(value) < len(options):
                errors.append(key)
        if kind == 'labelenum' and value not in node.get('values').split('|'):
            errors.append(key)
    return errors


def catchup_visible_values(text):
    """Model ONLY the reviewed ParseOldCondition static-string option mapping.

    This is XML/source regression coverage, not execution of Kodi's C++ loader.
    Exact four-tag evidence and the numeric-zero predicate are documented.
    """
    category = next(c for c in ET.fromstring(text).findall('category')
                    if c.find("setting[@id='catchup.type']") is not None)
    rows = list(category)
    result = {}
    for key in ('catchup.text', 'catchup.direct'):
        index = next(i for i, row in enumerate(rows) if row.get('id') == key)
        match = re.fullmatch(r'eq\((-\d+),(\d+)\)', rows[index].get('visible'))
        assert match
        referenced = rows[index + int(match[1])]
        assert referenced.get('id') == 'catchup.type'
        assert referenced.get('type') == 'labelenum'
        result[key] = referenced.get('values').split('|')[int(match[2])]
    return result


def catchup_choices(path, text, predicate):
    """Run only the real catchup if-test and its two selection assignments/calls.

    Never compile the enclosing method (source DB writes and GUI playback remain
    unexecuted). Supply a fake settings reader and inert catchup callbacks.
    """
    candidates = [node for node in ast.walk(ast.parse(text)) if isinstance(node, ast.If)
                  and "getSetting('catchup.type')" in ast.unparse(node.test)]
    assert len(candidates) == 1, (path, len(candidates))
    branch = candidates[0]
    # Each branch is exactly one assignment or callback; don't execute extra code.
    assert len(branch.body) == len(branch.orelse) == 1
    code = compile(ast.Module(body=[copy.deepcopy(branch)], type_ignores=[]), path, 'exec')
    results = {}
    for value in ('0', 'Meta?', '1', 'Direct'):
        class Reader:
            def getSetting(self, key):
                return {'catchup.type': value, 'catchup.text': 'meta-fixture',
                        'catchup.direct': 'direct-fixture'}[key]

            def catchup_meta(self, channel):
                results[value] = 'meta-fixture'

            def catchup_direct(self, channel):
                results[value] = 'direct-fixture'

        reader = Reader()
        reader.addon = reader
        namespace = {'ADDON': reader, 'self': reader, 'channel': object(),
                     'is_meta_catchup': predicate}
        exec(code, namespace)
        if 'catchup' in namespace:
            results[value] = namespace['catchup']
    return results


def check():
    old = settings(baseline('resources/settings.xml'))
    new = settings((ROOT / 'resources/settings.xml').read_text())
    assert set(bad_defaults(old)) == {'channel.shortcut', 'service.type', 'catchup.type'}
    print('DETECTED baseline invalid enum/labelenum defaults:', sorted(bad_defaults(old)))
    assert bad_defaults(new) == [], bad_defaults(new)
    assert set(old) == set(new), 'Setting IDs added/removed'
    changed = {'channel.shortcut': '0', 'service.type': '0', 'catchup.type': 'Meta?'}
    for key in old:
        expected = dict(old[key].attrib)
        if key in changed:
            expected['default'] = changed[key]
        assert new[key].attrib == expected, key
    print('PASS all setting IDs/types/options/conditions and other defaults retained')

    text = (ROOT / 'resources/settings.xml').read_text()
    visible = catchup_visible_values(text)
    assert visible == {'catchup.text': 'Meta?', 'catchup.direct': 'Direct'}
    for stored, expected_fields in (('Meta?', ['catchup.text']), ('Direct', ['catchup.direct'])):
        assert [key for key, value in visible.items() if value == stored] == expected_fields
    assert [key for key, value in visible.items() if value == new['catchup.type'].get('default')] == ['catchup.text']
    # Negative control: interpreting 0/1 as literal strings would hide both.
    literal = {'catchup.text': '0', 'catchup.direct': '1'}
    assert not any(value == 'Meta?' for value in literal.values())
    assert not any(value == 'Direct' for value in literal.values())
    assert not any(value == old['catchup.type'].get('default') for value in visible.values())
    print('PASS reviewed static-string UI condition model: offsets -1/-2 resolve catchup.type; 0/1 map Meta?/Direct')
    print('DETECTED literal-index condition model and baseline default hide both provider fields; not native UI proof')

    namespace = {}
    helper = ROOT / 'settings_compat.py'
    tree = ast.parse(helper.read_text(), feature_version=(3, 8))
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'is_meta_catchup')
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(helper), 'exec'), namespace)
    predicate = namespace['is_meta_catchup']
    for value in ('0', 'Meta?'):
        assert predicate(value) is True
    for value in ('1', 'Direct', '', None, 'meta?', 'Meta?\n', 'RunScript(fixture.py)'):
        assert predicate(value) is False
    expected = {'0': 'meta-fixture', 'Meta?': 'meta-fixture', '1': 'direct-fixture', 'Direct': 'direct-fixture'}
    for path in ('source.py', 'gui.py', 'streaming.py'):
        old_choices = catchup_choices(path, baseline(path), predicate)
        assert old_choices['Meta?'] == 'direct-fixture', (path, old_choices)
        assert catchup_choices(path, (ROOT / path).read_text(), predicate) == expected
        assert 'from settings_compat import is_meta_catchup' in (ROOT / path).read_text()
        print('DETECTED baseline Meta? misroute; PASS both retained representations:', path)

    old_manifest = ET.fromstring(baseline('addon.xml'))
    manifest = ET.parse(ROOT / 'addon.xml').getroot()
    imports = {node.get('addon'): node.get('version') for node in manifest.findall('requires/import')}
    assert imports == FLOORS, imports
    assert 'script.module.simplejson' in {n.get('addon') for n in old_manifest.findall('requires/import')}
    assert [e.attrib for e in manifest.findall('extension')[:2]] == [
        {'point': 'xbmc.python.script', 'library': 'addon.py'},
        {'point': 'xbmc.service', 'library': 'service.py'}]
    for path in list(ROOT.glob('*.py')) + list((ROOT / 'resources').rglob('*.py')):
        text = path.read_text()
        assert not re.search(r'\bsimplejson\b', text), path
        ast.parse(text, filename=str(path), feature_version=(3, 8))
    print('PASS dependency floors, no simplejson runtime use, dual entry points and Python 3.8 AST')

    # Settings actions are fixed trusted local script paths, not profile commands.
    actions = [n.get('action') for n in ET.parse(ROOT / 'resources/settings.xml').iter('setting')
               if n.get('type') == 'action']
    assert actions == [n.get('action') for n in ET.fromstring(baseline('resources/settings.xml')).iter('setting')
                       if n.get('type') == 'action']
    for action in actions:
        match = re.fullmatch(r'RunScript\(\$CWD/([A-Za-z_][A-Za-z_0-9]*\.py)(?:,\s*([A-Za-z_0-9.,]+))?\)', action)
        assert match, action
        assert (ROOT / match[1]).is_file(), action
    print('PASS unchanged fixed settings actions:', len(actions))
    print('NOT native dependency installation, settings GUI/persistence, providers or playback acceptance')


if __name__ == '__main__':
    check()
