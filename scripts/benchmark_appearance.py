"""Measure retained-window appearance transitions without writing user state."""

import argparse
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import statistics
import sys
import time

from benchmark_ui import memory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.root)
    from auto_elden_ring import __version__
    from auto_elden_ring.ui import App
    from auto_elden_ring.styles import STYLES

    app = App(persist=False)
    user = ctypes.windll.user32
    user.GetParent.argtypes = [wintypes.HWND]
    user.GetParent.restype = wintypes.HWND
    user.IsWindowVisible.argtypes = [wintypes.HWND]
    hwnd = user.GetParent(app.winfo_id())
    result = {"version": __version__, "all_pages_cached": True}
    try:
        state = app.profiles.create("Benchmark", "Benchmark", "Warrior", app.data)
        app.activate_profile(state)
        for page in ("character", "weapons", "stones", "farm", "journal", "settings"):
            app.show(page)
        app.update()
        initial = memory()
        visible = []
        original = app.update_controls_appearance

        def observed():
            visible.append(bool(user.IsWindowVisible(hwnd)))
            original()
            visible.append(bool(user.IsWindowVisible(hwnd)))

        app.update_controls_appearance = observed
        timings = []
        for i in range(12):
            start = time.perf_counter()
            if i < 6:
                app.set_palette(STYLES["modern"]["themes"][i % len(STYLES["modern"]["themes"])])
            else:
                app.dyslexic_var.set(not app.data["dyslexic"])
                app.set_reading_mode()
            app.update()
            timings.append(time.perf_counter() - start)
        result.update(
            {
                "median_transition_seconds": round(statistics.median(timings), 4),
                "maximum_transition_seconds": round(max(timings), 4),
                "samples_seconds": [round(value, 4) for value in timings],
                "native_window_always_visible_during_changes": all(visible),
                "native_window_identity_retained": user.GetParent(app.winfo_id()) == hwnd,
                "initial_memory": initial,
                "final_memory": memory(),
                "callback_errors": app.callback_errors,
                "notes": "Same local Windows desktop; all six pages cached. Source runtime measurement, not a game-concurrency or minimum-hardware claim.",
            }
        )
    finally:
        app.destroy()
    Path(args.report).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
