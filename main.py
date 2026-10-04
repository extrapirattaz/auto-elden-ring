"""Auto Elden Ring entry point. Imports do not open a window."""
import sys


def main():
    if "--save-check" in sys.argv:
        from auto_elden_ring.selfcheck import save_check
        from pathlib import Path
        report=save_check(sys.argv[sys.argv.index("--save-check")+1])
        if "--report" in sys.argv:
            Path(sys.argv[sys.argv.index("--report")+1]).write_text(report,encoding="utf-8")
        elif sys.stdout is not None:
            print(report)
        return
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
            app.data["dyslexic"]=False
            app.set_visual_style("style_modern")
            state=app.profiles.create("Release fixture","Release fixture","Warrior",app.data)
            app.activate_profile(state)
            app.show("journal")
            checks["empty character timeline"]=len(app.timeline.find_all())==1
            app.profiles.checkpoint(app.data,"Release checkpoint")
            app.draw_timeline()
            checks["timeline event"]=len(app.timeline.find_all())>1
            app.show("farm")
            app.data["farm_spots"]=[{"name":"Release spot","farm":dict(app.data["farm"])}]
            app.select_farm_spot("Release spot")
            checks["named farm spot"]=app.spot_option.get()=="Release spot"
            app.set_farm_option("goal","maximum")
            app.farm_vars["maximum_current"].set("150")
            app.farm_vars["runes"].set("20000")
            app.calculate_farm()
            projection=app.planner.farm_projection()
            checks["maximum goal and investment"]=(
                app.farm_metrics.values[2].master.winfo_manager()==""
                and app.invested_metrics.winfo_manager()=="pack"
                and projection["invested"]==app.db.level_cost(8,150)
                and projection["goal"]==app.db.level_cost(150,713))
            app.compact_mode()
            app.compact_window.rune_var.set("1500")
            app.update()
            checks["compact companion"]=app.data["runes"]==1500 and len(app.views)==1 and app.compact_window.winfo_viewable() and not app.winfo_viewable()
            app.compact_window.reopen()
            app.update()
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
