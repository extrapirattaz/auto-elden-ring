"""Capture only this application's rendered window for release review."""
from pathlib import Path
import sys
import time
import ctypes
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from PIL import ImageGrab
from auto_elden_ring.ui import App


def capture(window,path):
    ctypes.windll.user32.GetParent.restype=ctypes.c_void_p
    hwnd=ctypes.windll.user32.GetParent(window.winfo_id())
    ImageGrab.grab(window=hwnd).save(path)


def main():
    directory=ROOT/"docs/screenshots"
    directory.mkdir(parents=True,exist_ok=True)
    app=App(persist=False)
    app.geometry("1280x860+30+30")
    app.attributes("-topmost",True)
    app.data["stats_target"]["vigor"]=60
    app.data["runes"]=1500
    app.data["farm"]["runes"]=50000
    app.planner.toggle_weapon("Dagger")
    app.planner.toggle_weapon("Black Knife")
    try:
        for page in ("character","weapons","stones","farm","settings"):
            app.show(page)
            app.lift()
            app.update()
            time.sleep(.3)
            app.update()
            box=(app.winfo_rootx(),app.winfo_rooty(),app.winfo_rootx()+app.winfo_width(),app.winfo_rooty()+app.winfo_height())
            capture(app,directory/(page+".png"))
        app.data["theme"]="elden"
        app.data["language"]="fr"
        app.build_shell()
        app.show("weapons")
        app.update()
        time.sleep(.3)
        capture(app,directory/"elden-fr.png")
        app.catalogue()
        until=time.monotonic()+8
        while time.monotonic()<until:
            app.update()
            time.sleep(.02)
        window=next(w for w in app.winfo_children() if w.winfo_class()=="Toplevel")
        window.attributes("-topmost",True)
        window.lift()
        app.update()
        time.sleep(.4)
        box=(window.winfo_rootx(),window.winfo_rooty(),window.winfo_rootx()+window.winfo_width(),window.winfo_rooty()+window.winfo_height())
        capture(window,directory/"catalogue.png")
    finally:
        app.destroy()


if __name__=="__main__":
    main()
