"""Inert command captures + source wiring checks; never run legacy add-on code.

Only the new, stdlib-only command_safety helper is loaded. No Kodi/stub imports.
The tiny parser below covers unquoted examples, NOT Kodi's full grammar.
"""
import ast
from functools import lru_cache
import importlib.util
from pathlib import Path
import re
import subprocess
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
BASE = 'fe5e72f9b0bb6ffe37ec5b7ac72eaaa99251bb7f'


def source(path, baseline=False):
    if baseline:
        return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT, text=True)
    return (ROOT / path).read_text()


@lru_cache(maxsize=None)
def tree(path, baseline=False):
    return ast.parse(source(path, baseline))


def templates(path, prefix, baseline=False):
    # Extract literal format strings as data. Never compile/evaluate legacy code.
    return [n.left.value for n in ast.walk(tree(path, baseline))
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod)
            and isinstance(n.left, ast.Constant) and isinstance(n.left.value, str)
            and n.left.value.startswith(prefix)]


def args(command):
    depth, result, part = 0, [], ''
    for char in command[command.index('(') + 1:command.rindex(')')]:
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        if char == ',' and depth == 0:
            result.append(part)
            part = ''
        else:
            part += char
    return result + [part]


def check():
    hostile = 'x,RunScript(INERT_MARKER),1,True'
    start = '2026-11-20 12:00:00'
    # Negative controls: actual baseline templates, no builtin execution.
    reminder = templates('notification.py', 'AlarmClock(', True)[0] % (
        'tvguide-%s-%s' % (hostile, start), hostile, 'Channel', 'icon.png', 10)
    autoplay = templates('autoplay.py', 'AlarmClock(', True)[0] % (
        'tvguide-%s-%s' % (hostile, start), 'station,extra', start, 10)
    catchup = templates('gui.py', 'AlarmClock(', True)[0] % (
        hostile + '-' + start, 'RunPlugin(plugin://demo/title)', 10)
    for label, capture in [('notification', reminder), ('autoplay', autoplay), ('catchup', catchup)]:
        assert args(capture)[1] == 'RunScript(INERT_MARKER)'
        print('DETECTED baseline alarm-command replacement:', label, repr(capture))
    for path, prefix in [('play.py', 'PlayMedia('), ('gui.py', 'XBMC.RunPlugin(')]:
        capture = templates(path, prefix, True)[0] % 'plugin://demo/a,b'
        assert len(args(capture)) == 2
        print('DETECTED baseline URL argument split:', path, repr(capture))
    capture = templates('autoplay.py', 'AlarmClock(', True)[0] % ('ordinary-name', 'station,extra', start, 10)
    assert len(args(args(capture)[1])) == 4  # script path + TWO ID arguments + start
    print('DETECTED baseline channel-ID argument split:', repr(capture))
    capture = templates('gui.py', 'RunPlugin(', True)[0] % ('meta', 'News', 'en,INERT_MARKER')
    assert len(args(capture)) == 2
    print('DETECTED baseline GUI metadata argument split:', repr(capture))
    capture = templates('gui.py', 'CancelAlarm(', True)[0] % 'saved-name,extra'
    assert len(args(capture)) == 3
    print('DETECTED baseline profile alarm-name argument split:', repr(capture))

    spec = importlib.util.spec_from_file_location('command_safety', ROOT / 'command_safety.py')
    assert spec is not None and spec.loader is not None
    safe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(safe)  # New pure helper only, never legacy modules.
    for value in [hostile, 'a,b', 'a(b)', 'a"b', "a'b", 'a\\b', 'a\nb', 'a\x00b', 'a\x7fb', '']:
        assert not safe.is_builtin_data(value), repr(value)
    for value in ['News HD', 'Café & Sport', 'station-1', 'special://home/icon.png']:
        assert safe.is_builtin_data(value), value
    for path, kind in [('notification.py', 'notification'), ('autoplay.py', 'autoplay')]:
        text = source(path)
        assert "alarm_name('%s', programTitle, startTime)" % kind in text
        assert 'if not ' in text and 'is_builtin_data(' in text
        assert text.index('is_builtin_data(', text.index('def _schedule')) < text.index("xbmc.executebuiltin('AlarmClock")
        name = safe.alarm_name(kind, hostile, start)
        assert re.fullmatch('tvguide-' + kind + '-[0-9a-f]{64}', name)
        assert name == safe.alarm_name(kind, hostile, start)
        assert name != safe.alarm_name(kind, hostile, start + '1')
        assert len(args('CancelAlarm(%s-now,True)' % name)) == 2
    name = safe.alarm_name('notification', 'News HD', start)
    capture = templates('notification.py', 'AlarmClock(')[0] % (name, 'News HD', 'Channel', 'icon.png', 10)
    assert len(args(capture)) == 4 and len(args(args(capture)[1])) == 4
    print('PASS positive reminder capture:', repr(capture))

    gui = source('gui.py')
    assert gui.count("for value in (title, program.language, program.season, program.episode)") == 2
    assert gui.count("urllib.quote(str(value), safe='')") == 2
    assert gui.count("re.match(r'\\A[a-z0-9_.-]+\\Z', catchup)") == 2
    assert "re.match(r'\\Atvguide-catchup-[0-9a-f]{64}\\Z', name)" in gui
    assert "alarm_name('catchup', program.channel.id, program.startDate)" in gui
    for value in [hostile, 'Café, News (HD)', 'en/../../x', '1)\nRunScript(INERT_MARKER)']:
        encoded = quote(value.encode('utf-8'), safe='')
        assert unquote(encoded) == value and safe.is_builtin_data(encoded)
        for template in templates('gui.py', 'RunPlugin('):
            count = template.count('%s')
            command = template % tuple(['meta'] + [encoded] * (count - 1))
            alarm = 'AlarmClock(%s,%s,10,True)' % (safe.alarm_name('catchup', value, start), command)
            assert len(args(alarm)) == 4 and len(args(args(alarm)[1])) == 1
    assert 'XBMC.RunPlugin' not in gui and 'alternative.playback' not in gui
    assert 'alternative.playback' not in source('resources/settings.xml')
    assert 'executebuiltin' not in source('play.py')
    assert 'xbmc.Player().play(item=url)' in source('play.py')
    assert gui.count('self.player.play(item=url, windowed=self.osdEnabled)') >= 4
    # Only the common Python3 syntax/logging port is allowed in this service.
    expected_service = source('service.py', True).replace('xbmc.LOGNOTICE', 'xbmc.LOGINFO').replace(
        'except Exception, ex:', 'except Exception as ex:')
    assert source('service.py') == expected_service
    print('PASS hostile delimiter rejection, digest names, encoded catchup captures, Player/source wiring')
    print('No native execution, legacy imports, stub imports or full hostile-input audit')


if __name__ == '__main__':
    check()
