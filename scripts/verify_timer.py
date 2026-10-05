"""Measure a real one-minute GUI timer; do not simulate gameplay."""

import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from auto_elden_ring.ui import App
from auto_elden_ring import __version__


def main():
    app = App(persist=False)
    app.withdraw()
    app.show("farm")
    started = time.monotonic()
    app.start_timer()
    report = {}

    def check():
        if app.awaiting_result:
            elapsed = time.monotonic() - started
            report.update(
                app_version=__version__,
                status="PASS" if 60 <= elapsed < 63 else "FAIL",
                elapsed_seconds=elapsed,
                recorded_seconds=app.data["farm"]["seconds"],
                countdown=app.timer_label.cget("text"),
                gameplay_tested=False,
            )
            app.reset_timer()
            report["reset_countdown"] = app.timer_label.cget("text")
            app.destroy()
        else:
            app.after(100, check)

    app.after(100, check)
    app.mainloop()
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".build/timer-v2.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if (
        report["status"] != "PASS"
        or report["recorded_seconds"] != 60
        or report["reset_countdown"] != "01:00"
    ):
        raise SystemExit("Real GUI timer verification failed.")
    print(report)


if __name__ == "__main__":
    main()
