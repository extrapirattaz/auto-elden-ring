"""Measure this app only: startup, catalogue, idle CPU and process memory."""

import argparse
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import sys
import time


class Counters(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("faults", wintypes.DWORD)] + [
        (name, ctypes.c_size_t)
        for name in (
            "peak_working",
            "working",
            "peak_page",
            "page",
            "peak_nonpage",
            "nonpage",
            "pagefile",
            "peak_pagefile",
            "private",
        )
    ]


def memory():
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.windll.kernel32
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    function = ctypes.windll.psapi.GetProcessMemoryInfo
    function.argtypes = [ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD]
    if not function(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError()
    return {
        "working_mib": round(counters.working / 1048576, 2),
        "private_mib": round(counters.private / 1048576, 2),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.root)
    start = time.perf_counter()
    from auto_elden_ring.ui import App
    from auto_elden_ring import __version__

    app = App(persist=False)
    app.update()
    result = {
        "version": __version__,
        "startup_seconds": round(time.perf_counter() - start, 3),
        "startup_memory": memory(),
    }
    try:
        app.show("weapons")
        app.update()
        start = time.perf_counter()
        app.catalogue()
        app.update()
        result["catalogue_seconds"] = round(time.perf_counter() - start, 3)
        result["catalogue_memory"] = memory()
        if hasattr(app, "gallery"):
            result["visible_cards"] = len(app.gallery.hitboxes)
            result["image_cache"] = len(app.gallery.cache)
        else:
            result["image_cache"] = len(app.images)
        wall = time.perf_counter()
        cpu = time.process_time()
        while time.perf_counter() - wall < 3:
            app.update()
            time.sleep(0.02)
        result["idle_cpu_seconds_per_3_seconds"] = round(time.process_time() - cpu, 4)
        result["callback_errors"] = getattr(app, "callback_errors", [])
        result["notes"] = (
            "Same Windows host and Python environment; no Elden Ring process or minimum-spec PC tested."
        )
    finally:
        app.destroy()
    Path(args.report).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
