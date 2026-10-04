"""Small acceptance check included in both source and Windows executable."""
import hashlib
import json
from . import __version__
from .core import Database, shopping_plan, stone_requirements, inverse_base, stats_level, farm_estimate
from classes_data import CLASS_DATA, ATTRIBUTES


def self_check():
    db = Database()
    checks = {}
    checks["712 level transitions"] = len(db.level_costs) == 712
    checks["exact integer level formula"] = all(db.level_costs[l-1] == ((max(0,l-11)*2+10)*(l+81)**2)//100+1 for l in range(1,713))
    checks["level 1 to 713 = 1692566842"] = db.level_cost(1,713)==1692566842
    checks["487 catalogue entries"] = len(db.weapons)==487
    checks["all 10 classes reach 713"] = all(stats_level(c,{a:99 for a in ATTRIBUTES})==713 for c in CLASS_DATA)
    normal = db.weapons["Dagger"]
    somber = db.weapons["Black Knife"]
    n = shopping_plan([{"weapon":normal,"current":0,"target":24}])
    s = shopping_plan([{"weapon":somber,"current":0,"target":9}])
    checks["normal stones 129600"] = n["stones_cost"]==129600
    checks["somber stones 97000"] = s["stones_cost"]==97000
    checks["ancient stones required"] = stone_requirements(normal,24,25)=={"normal:dragon":1} and stone_requirements(somber,9,10)=={"somber:dragon":1}
    checks["somber final forge step included"] = sum(somber.costs)==5280
    checks["inverse standard normal"] = inverse_base("normal",4,5,180)==[100]
    checks["farm uses measured rate"] = farm_estimate(50000,60,100000)["seconds"]==120
    from .planner import Planner, buff_multiplier
    from .i18n import Translator
    from .core import resource_path
    checks["six complete name tables"]=all(len(Translator(locale).names[locale])==487 for locale in ("en","fr","cs","de","es","ja"))
    checks["487 bundled icons"]=len(list(resource_path("assets/catalogue").glob("*.webp")))==487
    checks["bundled reading font"]=resource_path("assets/fonts/OpenDyslexic-Regular.otf").is_file()
    checks["bundled landscape"]=resource_path("assets/elden-landscape.webp").is_file()
    p=Planner(db)
    p.add_sample(1000,60)
    p.add_sample(2000,60)
    p.add_sample(9000,180)
    checks["weighted five-minute farm"]=p.farm_rates()["measured"]==2400
    checks["silver discovery is not rune gain"]=buff_multiplier("silver","silver_foot")==1
    failed = [name for name,passed in checks.items() if not passed]
    if failed:
        raise RuntimeError("Self-check failed: "+", ".join(failed))
    return json.dumps({"app_version":__version__,"status":"PASS","checks":checks,
        "catalogue_count":len(db.weapons),"regulation":db.metadata["regulation_version"],
        "data_sha256":hashlib.sha256(db.path.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)


def save_check(path):
    """Exercise the packaged reader without exporting character identifiers."""
    from pathlib import Path
    from .save_reader import read_save
    from .profiles import Profiles
    from .history import import_characters
    from .planner import Planner,default_state
    path=Path(path)
    before=path.stat()
    digest=hashlib.sha256(path.read_bytes()).digest()
    db=Database()
    characters=read_save(path,db)
    profiles=Profiles(db)
    ids=import_characters(profiles,characters,default_state())
    checks={"planner levels":all(Planner(db,profiles.select(ident)).character()["current"]==char["level"]
                               for ident,char in zip(ids,characters))}
    import_characters(profiles,read_save(path,db),default_state())
    checks["deduplicated refresh"]=all(len(profiles.data["profiles"][ident]["checkpoints"])==1 for ident in ids)
    checks["file unchanged"]=digest==hashlib.sha256(path.read_bytes()).digest() and before.st_mtime_ns==path.stat().st_mtime_ns
    if not all(checks.values()):
        raise RuntimeError("Save-reader self-check failed.")
    return json.dumps({"app_version":__version__,"status":"PASS","characters":len(characters),
        "weapon_variants":sum(len(c["weapons"]) for c in characters),
        "ordinary_stones_total":sum(sum(c["stock"].values()) for c in characters),"checks":checks},indent=2)
