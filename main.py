"""Auto Elden Ring entry point. Imports do not open a window."""

import sys


def main():
    if "--self-test" in sys.argv:
        from auto_elden_ring.selfcheck import self_check

        report = self_check()
        if "--report" in sys.argv:
            from pathlib import Path

            Path(sys.argv[sys.argv.index("--report") + 1]).write_text(report, encoding="utf-8")
        elif sys.stdout is not None:
            print(report)
        return
    from auto_elden_ring.ui import run

    run()


if __name__ == "__main__":
    main()
