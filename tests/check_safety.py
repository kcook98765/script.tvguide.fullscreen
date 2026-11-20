"""Small source-only regression check. Never imports or executes add-on files."""
import ast
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BASE = "0e46733e9e5f7711f2381562cfbb98fd3b54b429"
FORBIDDEN = re.compile(
    r"\b(?:exec|eval|execfile|__import__)\s*\(|"
    r"\b(?:import|from)\s+(?:subprocess|pickle)\b|"
    r"\bos\.(?:system|popen|spawn\w*)\s*\(|"
    r"\b(?:extractall|Popen)\s*\("
)


def original(path):
    return subprocess.check_output(
        ["git", "show", BASE + ":" + path], cwd=ROOT, text=True
    )


def check():
    # Negative controls use original bytes as data, not Python execution.
    for path in ("service.py", "gui.py", "playwith.py", "stopwithchannel.py"):
        assert FORBIDDEN.search(original(path)), "Control missed " + path
        print("DETECTED baseline unsafe source:", path)

    runtime = list(ROOT.glob("*.py")) + list((ROOT / "resources").rglob("*.py"))
    for path in runtime:
        # Vendored pytz has pickle doctest text, not a profile deserializer.
        if "resources/lib/pytz" in path.as_posix():
            continue
        assert not FORBIDDEN.search(path.read_text()), str(path)
    assert not any(p.is_file() for p in (ROOT / "resources/playwith").rglob("*"))
    for path in ("autoplaywith.py", "playwith.py", "playwithchannel.py", "stopwith.py",
                 "stopwithchannel.py", "search.py", "resources/favourites.xml"):
        assert not (ROOT / path).exists(), path

    gui = (ROOT / "gui.py").read_text()
    tree = ast.parse(gui)  # Parse only: no imports, Kodi stubs, or callbacks run.
    guide = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "TVGuide")
    methods = {n.name: n for n in guide.body if isinstance(n, ast.FunctionDef)}
    for name in ("playWithChannel", "stopWith", "showFullAutoplaywiths"):
        callback = ast.get_source_segment(gui, methods[name])
        assert 'PVRRecording' in callback and '.run(' in callback, name
        assert 'executebuiltin' not in callback and 'self.database' not in callback, name
    pvr = (ROOT / 'pvr_recording.py').read_text()
    assert 'import xbmc' not in pvr and 'executebuiltin' not in pvr
    assert "self._accepted('PVR.Record', channel=channel['channelid'], record=True)" in pvr
    assert "self._accepted('PVR.DeleteTimer', timerid=timer['timerid'])" in pvr
    loader = ast.get_source_segment(gui, methods["loadActions"])
    assert 'action_bar.load(' in loader and 'json.loads' not in loader
    click = ast.get_source_segment(gui, methods['onClick'])
    assert 'action_bar.command_at(self.actions, pos)' in click
    assert 'executebuiltin(self.actions' not in click
    # Behavior/injection controls for this boundary live in check_action_bar.py.
    assert 'select_skin(ADDON)' in gui and '_SKIN_SNAPSHOT' in gui
    # External/profile settings may select DATA for the bounded snapshot only;
    # gui never passes the selected source root to WindowXML.
    assert "getSetting('skin.folder')" not in gui
    assert "RunScript" not in gui
    assert "executebuiltin(url)" not in gui and "getSetting('mine1')" not in gui
    service = (ROOT / "service.py").read_text()
    assert "requests" not in service and "base64" not in service and "autoplaywith" not in service
    assert "verify=False" in original("fileFetcher.py")
    assert "verify=False" not in (ROOT / "fileFetcher.py").read_text()

    settings = ET.parse(ROOT / "resources/settings.xml")
    ids = {node.get("id", "") for node in settings.iter("setting")}
    assert not any(i.startswith("autoplaywiths.") for i in ids)
    assert not ids.intersection({"mine1", "search.type"})
    assert settings.find(".//setting[@id='skin.custom.enabled']").get('default') == 'false'
    for path in (ROOT / "resources/skins").glob("*/720p/script-tvguide-menu.xml"):
        skin = ET.parse(path)
        for control in skin.iter("control"):
            if control.get("id") == "4013":
                assert control.findtext("visible") != "false", str(path)
                assert control.findtext("label") == "TMDbHelper lookup…", str(path)
            if control.get("id") == "4009":
                assert control.findtext("visible") != "false", str(path)
                assert control.findtext("label") == "Record (Kodi PVR)…", str(path)
    print("PASS focused source-only safety checks; runtime files scanned:", len(runtime))
    print("NOT a complete security proof, Python 3 validation, or native acceptance")


if __name__ == "__main__":
    check()
