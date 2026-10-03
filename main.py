"""Auto Elden Ring entry point. Imports do not open a window."""
import sys


def main():
    if "--ui-smoke" in sys.argv:
        from auto_elden_ring.ui import App
        from auto_elden_ring import __version__
        import json
        from pathlib import Path
        app = App(persist=False)
        checks = {}
        try:
            app.update()
            for language in ("en","fr","cs","de","es","ja"):
                app.data["language"]=language
                app.apply_appearance()
                for page in ("character","weapons","stones","farm","journal","settings"):
                    app.show(page)
                    app.update()
                checks[language]=True
            app.data["weapon_mode"]="catalogue"
            app.planner.toggle_weapon("Dagger")
            app.planner.toggle_weapon("Black Knife")
            app.show("weapons")
            app.rebuild_weapon_form()
            app.catalogue()
            app.update()
            checks["bundled images"]=len(app.gallery.cache)>0
            checks["selected catalogue costs"]=app.planner.weapons()["total"]>0
            checks["four styles"]=True
            for style in ("modern","elden","xp","rainbow"):
                app.set_visual_style("style_"+style)
                app.update()
            app.data["dyslexic"]=True
            app.apply_appearance()
            checks["reading font"]=app.font_family=="OpenDyslexic"
            checks["no callback errors"]=not app.callback_errors
            report=json.dumps({"app_version":__version__,"status":"PASS" if all(checks.values()) else "FAIL","checks":checks},indent=2)
            if "--report" in sys.argv:
                Path(sys.argv[sys.argv.index("--report")+1]).write_text(report,encoding="utf-8")
            elif sys.stdout is not None:
                print(report)
        finally:
            app.destroy()
        if not all(checks.values()):
            raise RuntimeError("Packaged GUI smoke check failed.")
        return
    if "--self-test" in sys.argv:
        from auto_elden_ring.selfcheck import self_check
        report = self_check()
        if "--report" in sys.argv:
            from pathlib import Path
            Path(sys.argv[sys.argv.index("--report")+1]).write_text(report, encoding="utf-8")
        elif sys.stdout is not None:
            print(report)
        return
    from auto_elden_ring.ui import run
    run()


if __name__ == "__main__":
    main()
