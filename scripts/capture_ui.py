"""Development-only captures of this application's own rendered Tk window.

Requires Pillow, not needed by the shipped application or the build.
"""

from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from PIL import ImageGrab
from auto_elden_ring.ui import App


def main():
    directory = ROOT / "docs" / "screenshots"
    directory.mkdir(parents=True, exist_ok=True)
    app = App()
    try:
        app.geometry("1200x850+40+40")
        app.attributes("-topmost", True)
        app.lift()
        app.fields["level_current"].set(80)
        app.fields["level_origin"].set(50)
        app.items = [
            {"name": "Dagger", "current": 12, "target": 25, "quantity": 2, "custom": False},
            {"name": "Black Knife", "current": 5, "target": 10, "quantity": 1, "custom": False},
        ]
        app.inventory = {"normal:5": 8, "normal:dragon": 2, "somber:dragon": 1}
        app.extras = [{"name": "Pattes dorées en saumure", "quantity": 10, "unit": 600}]
        app.update_plan()
        app.calculate_levels()
        app.calculate_inverse()
        app.calculate_farm()
        for index, name in enumerate(app.pages):
            app.tabs.select(index)
            app.update()
            time.sleep(0.25)
            app.update()
            box = (
                app.winfo_rootx(),
                app.winfo_rooty(),
                app.winfo_rootx() + app.winfo_width(),
                app.winfo_rooty() + app.winfo_height(),
            )
            path = directory / f"{index+1:02d}.png"
            ImageGrab.grab(bbox=box).save(path)
            print(path)
    finally:
        app.destroy()


if __name__ == "__main__":
    main()
