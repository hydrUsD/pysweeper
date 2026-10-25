"""Sammelt die Testergebnisse für course/_check.py.

Ist PYSWEEPER_CHECK_OUT gesetzt, landet pro Test ein Eintrag
(Beschreibung, Ergebnis, Meldung) als JSON in dieser Datei.
"""
import json
import linecache
import os
import random

import pytest

_results = []


@pytest.fixture(autouse=True)
def _seed():
    # Fester Seed: ein zufällig sofort gewonnenes Spiel soll keinen Test flackern lassen.
    random.seed(20261025)


def _message(report):
    longrepr = report.longrepr
    crash = getattr(longrepr, "reprcrash", None)
    if crash is None:
        return str(longrepr).strip()
    text = crash.message
    text = text.removeprefix("AssertionError: ").removeprefix("Failed: ").strip()
    if text.startswith("assert "):
        # Assert ohne eigene Meldung: nur den Vergleich zeigen, ohne die "+ where ..."-Zeilen
        # (die enthalten Speicheradressen und sind für Lernende nur Rauschen).
        line = linecache.getline(str(crash.path), crash.lineno).strip()
        text = f"Erwartung nicht erfüllt: `{line}`  (tatsächlich: {text.splitlines()[0]})"
    else:
        # pytest hängt die Assertion-Introspektion an ("assert ..."), die ist hier nur Rauschen.
        text = text.split("\nassert ")[0].strip()
    location = ""
    if "pysweeper" in str(crash.path) and "course" not in str(crash.path):
        path = str(crash.path)
        location = f" (in {path[path.rfind('pysweeper'):]}:{crash.lineno})"
    return text + location


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    report.description = (item.obj.__doc__ or item.name).strip()
    if hasattr(item, "callspec"):
        report.description += f" [{item.callspec.id}]"
    return report


def pytest_runtest_logreport(report):
    if report.when == "call" or report.outcome == "failed":
        _results.append({
            "test": report.description,
            "passed": report.outcome == "passed",
            "message": "" if report.outcome == "passed" else _message(report),
        })


def pytest_collectreport(report):
    if report.failed:
        _results.append({
            "test": f"Testdatei laden ({report.nodeid})",
            "passed": False,
            "message": str(report.longrepr).strip().splitlines()[-1],
        })


def pytest_sessionfinish(session, exitstatus):
    out = os.environ.get("PYSWEEPER_CHECK_OUT")
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(_results, f, ensure_ascii=False)
