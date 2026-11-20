"""Inert command captures + source wiring checks; never run legacy add-on code.

Only the new, stdlib-only command_safety helper is loaded. No Kodi/stub imports.
The tiny parser below covers unquoted examples, NOT Kodi's full grammar.
"""
import ast
import copy
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
        if kind == 'autoplay':
            assert 'is_builtin_data' not in text
            assert 'payload = encode_identity(channelId, str(startTime))' in text
            assert text.index('encode_identity(', text.index('def _schedule')) < text.index("xbmc.executebuiltin('AlarmClock")
            for template in templates(path, 'AlarmClock('):
                assert template.count('%s') == 2  # digest name + one opaque argument
        else:
            assert 'is_builtin_data' not in text and ',Notification(' not in text
            assert "alarm_command(name, token, '5mins', timeToNotification - 5)" in text
            assert "alarm_command(name, token, 'now', timeToNotification)" in text
            assert 'self.reminders.cancel(name)' in text
        name = safe.alarm_name(kind, hostile, start)
        assert re.fullmatch('tvguide-' + kind + '-[0-9a-f]{64}', name)
        assert name == safe.alarm_name(kind, hostile, start)
        assert name != safe.alarm_name(kind, hostile, start + '1')
        assert len(args('CancelAlarm(%s-now,True)' % name)) == 2
    # Actual fixed callback captures/exact text transfer and all phases are tested
    # independently in check_reminders.py. Never recreate the old nested guard.
    assert "CALLBACK = 'special://home/addons/script.tvguide.fullscreen/reminder_callback.py'" in source('reminder_data.py')

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
    # Task18 changes startup cleanup/schedule parsing only. Keep original callback
    # behavior and every fixed command byte, not the old unsafe file deletions.
    expected_service = source('service.py', True).replace('xbmc.LOGNOTICE', 'xbmc.LOGINFO').replace(
        'except Exception, ex:', 'except Exception as ex:')
    expected_tree = ast.parse(expected_service)
    current_tree = tree('service.py')
    def unchanged_service(module, legacy):
        module = copy.deepcopy(module)
        module.body = [n for n in module.body if not (isinstance(n, ast.FunctionDef) and n.name == '_time_left')]
        for node in module.body:
            if isinstance(node, ast.Import):
                node.names = [n for n in node.names if n.name != 'xbmcvfs']
        main = next(n for n in module.body if isinstance(n, ast.If))
        if legacy:
            # Only the two startup deletes and their marker assignment go away.
            main.body = [n for n in main.body if not (
                (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                 and isinstance(n.value.func, ast.Attribute) and n.value.func.attr == 'delete')
                or (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'lock' for t in n.targets)))]
        loop = next(n for n in ast.walk(main) if isinstance(n, ast.While))
        if legacy:
            loop.body = loop.body[2:]  # Old schedule arithmetic + negative clamp.
        else:
            assert isinstance(loop.body[0], ast.Assign)
            assert loop.body[0].value.func.id == '_time_left'
            loop.body = loop.body[1:]
            abort = ast.parse('if monitor.abortRequested():\n    break').body[0]
            assert ast.dump(loop.body[2]) == ast.dump(abort)
            del loop.body[2]
        return ast.dump(module)
    # Entire unreviewed module/control flow still has to match the original port,
    # including autostart/startup/folder gates, timestamp writes and exceptions.
    assert unchanged_service(current_tree, False) == unchanged_service(expected_tree, True)
    service_class = lambda module: next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'Service')
    assert ast.dump(service_class(current_tree)) == ast.dump(service_class(expected_tree))
    def fixed_commands(module):
        calls = [n for n in ast.walk(module) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == 'executebuiltin']
        assert all(len(n.args) == 1 and isinstance(n.args[0], ast.Constant)
                   and isinstance(n.args[0].value, str) and not n.keywords for n in calls)
        return sorted(n.args[0].value for n in calls)
    assert fixed_commands(current_tree) == fixed_commands(expected_tree)
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                   and n.func.attr == 'delete' for n in ast.walk(current_tree))
    print('PASS hostile delimiter rejection, digest names, encoded catchup captures, Player/source wiring')
    print('No native execution, legacy imports, stub imports or full hostile-input audit')


if __name__ == '__main__':
    check()
