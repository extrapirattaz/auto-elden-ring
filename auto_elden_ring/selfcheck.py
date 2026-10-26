"""Small acceptance check included in both source and Windows executable."""

import hashlib
import json
from . import __version__
from .core import (
    Database,
    shopping_plan,
    stone_requirements,
    inverse_base,
    stats_level,
    farm_estimate,
)
from classes_data import CLASS_DATA, ATTRIBUTES


def self_check():
    db = Database()
    checks = {}
    checks["712 level transitions"] = len(db.level_costs) == 712
    checks["exact integer level formula"] = all(
        db.level_costs[l - 1] == ((max(0, l - 11) * 2 + 10) * (l + 81) ** 2) // 100 + 1
        for l in range(1, 713)
    )
    checks["level 1 to 713 = 1692566842"] = db.level_cost(1, 713) == 1692566842
    checks["487 catalogue entries"] = len(db.weapons) == 487
    checks["all 10 classes reach 713"] = all(
        stats_level(c, {a: 99 for a in ATTRIBUTES}) == 713 for c in CLASS_DATA
    )
    normal = db.weapons["Dagger"]
    somber = db.weapons["Black Knife"]
    n = shopping_plan([{"weapon": normal, "current": 0, "target": 24}])
    s = shopping_plan([{"weapon": somber, "current": 0, "target": 9}])
    checks["normal stones 129600"] = n["stones_cost"] == 129600
    checks["somber stones 97000"] = s["stones_cost"] == 97000
    checks["ancient stones required"] = stone_requirements(normal, 24, 25) == {
        "normal:dragon": 1
    } and stone_requirements(somber, 9, 10) == {"somber:dragon": 1}
    checks["somber final forge step included"] = sum(somber.costs) == 5280
    checks["inverse standard normal"] = inverse_base("normal", 4, 5, 180) == [100]
    checks["farm uses measured rate"] = farm_estimate(50000, 60, 100000)["seconds"] == 120
    from .planner import Planner, buff_multiplier
    from .i18n import Translator
    from .core import resource_path

    checks["six complete name tables"] = all(
        len(Translator(locale).names[locale]) == 487
        for locale in ("en", "fr", "cs", "de", "es", "ja")
    )
    items = json.loads(resource_path("assets/item_catalogue.json").read_text(encoding="utf-8"))[
        "items"
    ]
    checks["offline inventory names and icons"] = len(items) >= 2950 and all(
        resource_path(i["icon"]).is_file() for i in items.values()
    )
    checks["487 bundled icons"] = len(list(resource_path("assets/catalogue").glob("*.webp"))) == 487
    checks["bundled reading font"] = resource_path(
        "assets/fonts/OpenDyslexic-Regular.otf"
    ).is_file()
    from .styles import STYLES, PALETTES

    checks["static style palettes"] = set(STYLES) == set(PALETTES) and len(STYLES) == 2
    p = Planner(db)
    p.add_sample(1000, 60)
    p.add_sample(2000, 60)
    p.add_sample(9000, 180)
    checks["weighted five-minute farm"] = p.farm_rates()["measured"] == 2400
    checks["silver discovery is not rune gain"] = buff_multiplier("silver", "silver_foot") == 1
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError("Self-check failed: " + ", ".join(failed))
    return json.dumps(
        {
            "app_version": __version__,
            "status": "PASS",
            "checks": checks,
            "catalogue_count": len(db.weapons),
            "regulation": db.metadata["regulation_version"],
            "data_sha256": hashlib.sha256(db.path.read_bytes()).hexdigest(),
        },
        ensure_ascii=False,
        indent=2,
    )


def audio_check():
    """Packaged decoder/device lifecycle proof; silence is not audible-output proof."""
    import os
    from .audio import Music
    from .core import resource_path

    os.environ["SDL_AUDIODRIVER"] = "dummy"
    checks = {}
    music = Music()
    try:
        for path in resource_path("assets/audio-check").iterdir():
            if path.suffix not in (".mp3", ".wav", ".flac", ".ogg", ".opus"):
                continue
            music.play(path)
            loaded = music.backend.music.get_busy()
            music.pause()
            music.play(path)
            checks[path.name] = loaded and not music.paused and music.backend.music.get_busy()
            music.close()
    finally:
        music.close()
    if len(checks) != 6 or not all(checks.values()):
        raise RuntimeError("Packaged audio decoder check failed.")
    return json.dumps(
        {
            "app_version": __version__,
            "status": "PASS",
            "checks": checks,
            "audible_output": "NOT TESTED",
        },
        indent=2,
    )


def save_check(path):
    """Exercise the packaged reader without exporting character identifiers."""
    from pathlib import Path
    from .save_reader import read_save
    from .profiles import Profiles
    from .history import import_characters
    from .planner import Planner, default_state

    path = Path(path)
    before = path.stat()
    digest = hashlib.sha256(path.read_bytes()).digest()
    db = Database()
    characters = read_save(path, db)
    profiles = Profiles(db)
    ids = import_characters(profiles, characters, default_state())
    checks = {
        "planner levels": all(
            Planner(db, profiles.select(ident)).character()["current"] == char["level"]
            for ident, char in zip(ids, characters)
        )
    }
    import_characters(profiles, read_save(path, db), default_state())
    checks["deduplicated refresh"] = all(
        len(profiles.data["profiles"][ident]["checkpoints"]) == 1 for ident in ids
    )
    checks["file unchanged"] = (
        digest == hashlib.sha256(path.read_bytes()).digest()
        and before.st_mtime_ns == path.stat().st_mtime_ns
    )
    if not all(checks.values()):
        raise RuntimeError("Save-reader self-check failed.")
    return json.dumps(
        {
            "app_version": __version__,
            "status": "PASS",
            "characters": len(characters),
            "weapon_variants": sum(len(c["weapons"]) for c in characters),
            "ordinary_stones_total": sum(sum(c["stock"].values()) for c in characters),
            "checks": checks,
        },
        indent=2,
    )


def rescan_check(path):
    """Exercise startup and manual rescans with an isolated local profile library."""
    import os
    from pathlib import Path
    import tempfile
    import time
    from .profiles import Profiles
    from .history import import_characters
    from .planner import default_state
    from .save_reader import read_save
    from .ui import App

    path = Path(path).resolve()
    before = (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns)
    db = Database()
    characters = read_save(path, db)
    profiles = Profiles(db)
    ids = import_characters(profiles, characters, default_state())
    state = profiles.select(ids[0])
    state["stats_target"]["vigor"] = min(99, state["stats_current"]["vigor"] + 1)
    profiles.data["save_sources"] = [str(path)]
    previous_env = {k: os.environ.get(k) for k in ("LOCALAPPDATA", "APPDATA")}
    checks = {}
    with tempfile.TemporaryDirectory(prefix="auto-elden-rescan-") as temporary:
        os.environ["LOCALAPPDATA"] = temporary
        os.environ["APPDATA"] = temporary
        app = None
        try:
            profiles.save(Path(temporary) / "AutoEldenRing/profiles-v3.json", state)
            app = App(persist=True, db=db)
            native = app.winfo_id()
            picker = app.profile_picker
            end = time.monotonic() + 15
            while (
                getattr(app, "scan_message_key", (None,))[0] != "scan_done"
                and time.monotonic() < end
            ):
                app.update()
                time.sleep(0.01)
            checks["startup remembered save"] = (
                getattr(app, "scan_message_key", (None,))[0] == "scan_done"
            )
            checks["chooser retained"] = (
                app.profile_picker is picker
                and picker.winfo_exists()
                and app.profile_selection_pending
            )
            app.activate_profile(app.profiles.select(ids[0]))
            app.show("farm")
            app.start_timer()
            deadline = app.deadline
            frames = {k: v["frame"] for k, v in app.views.items()}
            app.rescan_game()
            end = time.monotonic() + 15
            while getattr(app, "import_in_progress", False) and time.monotonic() < end:
                app.update()
                time.sleep(0.01)
            checks["manual background scan"] = (
                not getattr(app, "import_in_progress", False)
                and app.scan_message_key[0] == "scan_done"
            )
            checks["native window and pages retained"] = native == app.winfo_id() and frames == {
                k: v["frame"] for k, v in app.views.items()
            }
            checks["running farm timer retained"] = app.deadline == deadline
            checks["goal retained"] = app.data["stats_target"] == state["stats_target"]
            checks["identical scan has no new event"] = all(
                len(app.profiles.data["profiles"][ident]["checkpoints"]) == 1 for ident in ids
            )
            checks["saved current progression"] = (
                app.data["stats_current"] == characters[0]["stats"]
                and app.data["runes"] == characters[0]["runes"]
            )
            checks["no callback errors"] = not app.callback_errors
        finally:
            if app is not None:
                app.close()
            for key, value in previous_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    checks["save content and timestamp unchanged"] = before == (
        hashlib.sha256(path.read_bytes()).hexdigest(),
        path.stat().st_mtime_ns,
    )
    if not all(checks.values()):
        raise RuntimeError(
            "Rescan self-check failed: " + ", ".join(k for k, v in checks.items() if not v)
        )
    return json.dumps(
        {
            "app_version": __version__,
            "status": "PASS",
            "characters": len(characters),
            "checks": checks,
        },
        indent=2,
    )
