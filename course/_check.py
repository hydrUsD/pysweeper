"""Check-Button und Hinweise für oop-kurs.ipynb.

check("l3")      startet die Tests zu Lektion 3 in einem eigenen Prozess,
                 so wird immer der aktuelle Stand deiner Dateien geprüft.
hint("l3", 2)    zeigt Hinweis-Stufe 2 (Stufe 1 muss vorher gelesen sein).
explain("l3")    zeigt die Musterantworten zu den Warum-Fragen.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

from _hints import ANSWERS, HINTS, TITLES

ROOT = next(p for p in [pathlib.Path(__file__).resolve().parent, *pathlib.Path(__file__).resolve().parents]
            if (p / "pyproject.toml").exists())

_SEEN_FILE = pathlib.Path(__file__).resolve().parent / ".hints_seen.json"


def _load_seen():
    try:
        return {tuple(item) for item in json.loads(_SEEN_FILE.read_text(encoding="utf-8"))}
    except (OSError, ValueError):
        return set()


_seen_hints = _load_seen()   # überlebt Kernel-Neustarts


def check(lesson):
    """Führt course/tests/test_<lesson>.py aus und zeigt das Ergebnis."""
    test_file = ROOT / "course" / "tests" / f"test_{lesson}.py"
    if not test_file.exists():
        print(f"Unbekannte Lektion {lesson!r}. Verfügbar: {', '.join(sorted(TITLES))}")
        return
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "results.json"
        env = {**os.environ, "PYSWEEPER_CHECK_OUT": str(out), "PYTHONDONTWRITEBYTECODE": "1"}
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-q", "-p", "no:cacheprovider"],
                cwd=ROOT, env=env, capture_output=True, text=True, timeout=60,
            )
        except subprocess.TimeoutExpired:
            print("⏱  Zeitüberschreitung nach 60 s. Hängt eine Schleife? (z. B. eine Cascade ohne "
                  "'schon aufgedeckt?'-Prüfung oder eine mainloop(), die nie endet)")
            return
        if not out.exists():
            print("Die Tests konnten nicht starten:\n")
            print(proc.stdout[-2000:], proc.stderr[-2000:])
            return
        results = json.loads(out.read_text(encoding="utf-8"))

    print(f"🧪 {TITLES[lesson]}\n")
    shown = {}   # Meldung → Test, bei dem sie zuerst kam
    for r in results:
        print(f"  {'✅' if r['passed'] else '⏭' if r.get('skipped') else '❌'} {r['test']}")
        if r["passed"]:
            continue
        if r["message"] in shown:
            print(f"       → (gleicher Grund wie bei „{shown[r['message']]}“)")
            continue
        shown[r["message"]] = r["test"]
        for line in r["message"].splitlines():
            print(f"       → {line}")
    passed = sum(r["passed"] for r in results)
    skipped = sum(bool(r.get("skipped")) for r in results)
    print(f"\n{passed}/{len(results)} bestanden." + (f" {skipped} übersprungen (siehe ⏭)." if skipped else ""))
    if results and passed == len(results):
        print(f"🎉 {TITLES[lesson]} geschafft! Guter Moment für einen Commit:\n"
              f"   git add -A && git commit -m \"{lesson.upper()}: {TITLES[lesson].split(' – ')[-1]}\"")


def hint(lesson, level=1):
    """Gestufte Hinweise: erst Konzept, dann Prinzip, dann konkreter Schritt."""
    hints = HINTS.get(lesson)
    if not hints:
        print(f"Für {lesson!r} gibt es keine Hinweise.")
        return
    level = max(1, min(level, len(hints)))
    missing = [n for n in range(1, level) if (lesson, n) not in _seen_hints]
    if missing:
        print(f"Lies zuerst Stufe {missing[0]}: hint({lesson!r}, {missing[0]})")
        return
    if level > 1:
        print(f"Bevor du weiterliest: Was hat dir Stufe {level - 1} gesagt, und wo hängst du "
              f"trotzdem noch? (Ein Satz im Kopf reicht.)\n")
    _seen_hints.add((lesson, level))
    try:
        _SEEN_FILE.write_text(json.dumps(sorted(_seen_hints)), encoding="utf-8")
    except OSError:
        pass
    print(f"💡 Hinweis {level}/{len(hints)}:\n")
    print(hints[level - 1])
    if level < len(hints):
        print(f"\nImmer noch fest? hint({lesson!r}, {level + 1})")


def explain(lesson):
    """Musterantworten zu den Warum-Fragen. Erst selbst antworten, dann vergleichen."""
    print(ANSWERS.get(lesson, f"Für {lesson!r} gibt es keine Musterantworten."))
