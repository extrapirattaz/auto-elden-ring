"""Capture only this application's rendered window for release review."""

from pathlib import Path
import sys
import time
import ctypes
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from PIL import ImageGrab
from auto_elden_ring.ui import App


def capture(window, path):
    ctypes.windll.user32.GetParent.restype = ctypes.c_void_p
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    ImageGrab.grab(window=hwnd).save(path)


def main():
    directory = ROOT / "docs/screenshots"
    directory.mkdir(parents=True, exist_ok=True)
    with (
        tempfile.TemporaryDirectory() as temporary,
        patch.dict("os.environ", {"LOCALAPPDATA": temporary}),
    ):
        startup = App(persist=True)
        try:
            startup.update()
            capture(startup, directory / "startup.png")
        finally:
            startup.close()
    app = App(persist=False)
    app.geometry("1280x860+30+30")
    app.attributes("-topmost", True)
    state = app.profiles.create("Demo Tarnished", "Demo Tarnished", "Vagabond", app.data)
    app.activate_profile(state)
    app.data["stats_target"]["vigor"] = 60
    app.data["runes"] = 1500
    app.data["farm"]["runes"] = 50000
    app.planner.toggle_weapon("Dagger")
    app.planner.toggle_weapon("Black Knife")
    app.data["equipment"] = [
        {"id": 1000006, "slot": 1, "quantity": 1, "name": "Dagger", "current": 6}
    ]
    app.data["inventory_armor"] = [{"id": 0x100249F0, "quantity": 1}]
    app.data["inventory_items"] = [{"id": 1073750775, "quantity": 1}]
    app.data["inventory_weapons"] = [
        {"name": "Dagger", "current": 6, "quantity": 1},
        {"name": "Black Knife", "current": 4, "quantity": 1},
    ]
    app.profiles.checkpoint(app.data, "Starting journey", "2026-10-03T12:00:00+02:00")
    app.data["stats_current"]["vigor"] = 25
    app.data["selected"][0]["current"] = 6
    app.profiles.checkpoint(app.data, "After exploring Limgrave", "2026-10-03T14:30:00+02:00")
    app.replace_views()
    try:
        for page in ("character", "weapons", "stones", "farm", "journal", "settings"):
            app.show(page)
            app.lift()
            app.update()
            time.sleep(0.3)
            app.update()
            box = (
                app.winfo_rootx(),
                app.winfo_rooty(),
                app.winfo_rootx() + app.winfo_width(),
                app.winfo_rooty() + app.winfo_height(),
            )
            capture(app, directory / (page + ".png"))
        app.set_visual_style("style_elden")
        app.data["language"] = "fr"
        app.apply_appearance()
        app.show("weapons")
        app.update()
        time.sleep(0.3)
        app.update()
        capture(app, directory / "gothic-fr.png")
        app.catalogue()
        until = time.monotonic() + 0.3
        while time.monotonic() < until:
            app.update()
            time.sleep(0.02)
        window = app.gallery_window
        window.lift()
        app.update()
        time.sleep(0.4)
        box = (
            window.winfo_rootx(),
            window.winfo_rooty(),
            window.winfo_rootx() + window.winfo_width(),
            window.winfo_rooty() + window.winfo_height(),
        )
        capture(app, directory / "catalogue.png")
        window.destroy()
        details = app.checkpoint_detail(app.profiles.active["checkpoints"][-1])
        app.update()
        time.sleep(0.2)
        capture(app, directory / "checkpoint.png")
        details.render_tab(app.t("armor"))
        app.update()
        capture(app, directory / "equipment-armor.png")
        details.render_tab(app.t("items"))
        app.update()
        capture(app, directory / "equipment-items.png")
        details.destroy()
        picker = app.show_profile_picker()
        app.update()
        time.sleep(0.2)
        capture(app, directory / "profiles.png")
        picker.back.invoke()
        for palette in ("moon", "ember"):
            app.set_palette(palette)
            app.update()
            time.sleep(0.2)
            app.update()
            capture(app, directory / ("gothic-" + palette + ".png"))
        for style in ("modern", "elden", "xp"):
            app.set_visual_style("style_" + style)
            app.show("settings")
            app.update()
            time.sleep(0.2)
            app.update()
            capture(
                app, directory / ("style-" + ("gothic" if style == "elden" else style) + ".png")
            )

        app.data["dyslexic"] = True
        app.apply_appearance()
        app.update()
        capture(app, directory / "reading.png")
        app.data["dyslexic"] = False
        app.set_visual_style("style_modern")
        app.show("settings")
        app.compact_mode()
        app.update()
        time.sleep(0.2)
        capture(app.compact_window, directory / "compact.png")
        app.compact_window.mode_var.set("weapons")
        app.compact_window.refresh_summary()
        app.update()
        capture(app.compact_window, directory / "compact-stones.png")
        app.compact_window.mode_var.set("farm")
        app.compact_window.refresh_summary()
        app.update()
        capture(app.compact_window, directory / "compact-farm.png")
        app.compact_window.reopen()
    finally:
        app.destroy()


if __name__ == "__main__":
    main()
