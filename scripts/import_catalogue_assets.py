"""Import item names and icons from pinned community data sources.

No network access is required by the desktop application. Run this maintenance
script explicitly to update its locally bundled assets and provenance manifest.
"""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Auto-Elden-Ring-Asset-Importer"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def main():
    data = json.loads((ROOT / "elden_ring_costs.json").read_text(encoding="utf-8"))
    weapons = {n: v for entries in data["weapons_by_category"].values() for n, v in entries.items()}
    target = ROOT / "assets" / "catalogue"
    target.mkdir(parents=True, exist_ok=True)
    repositories = ("oisis/EldenRing-SaveForge", "elden-ring-data/msg", "ividyon/Impalers-Archive")
    commits = {
        repo: json.loads(fetch(f"https://api.github.com/repos/{repo}/commits/main"))["sha"]
        for repo in repositories
    }
    manifest = {"repositories": commits, "images": {}, "names": {}}
    repo = repositories[0]
    icon_paths = {}
    tree = json.loads(
        fetch(f"https://api.github.com/repos/{repo}/git/trees/{commits[repo]}?recursive=1")
    )["tree"]
    for file in tree:
        path = file["path"]
        if (
            path.startswith("backend/db/data/")
            and path.endswith(".go")
            and any(k in path for k in ("melee_armaments", "ranged_and_catalysts", "shields.go"))
        ):
            text = fetch(
                f"https://raw.githubusercontent.com/{repo}/{commits[repo]}/{path}"
            ).decode()
            for address, name, icon in re.findall(
                r'0x([0-9A-Fa-f]+):\s*\{Name:\s*"([^"]+)"[^\n]*?IconPath:\s*"([^"]+)"', text
            ):
                icon_paths[int(address, 16)] = icon

    def download(item):
        name, entry = item
        icon = icon_paths.get(entry["id"])
        if not icon:
            return name, None
        url = f"https://raw.githubusercontent.com/{repo}/{commits[repo]}/frontend/public/{icon}"
        destination = target / f"{entry['id']}.png"
        try:
            raw = fetch(url)
            image = Image.open(io.BytesIO(raw)).convert("RGBA")
            image.thumbnail((192, 192), Image.Resampling.LANCZOS)
            image.save(destination, optimize=True)
            return name, {
                "file": str(destination.relative_to(ROOT)).replace("\\", "/"),
                "source": url,
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
            }
        except Exception as exc:
            return name, {"error": str(exc)}

    with ThreadPoolExecutor(max_workers=8) as pool:
        for name, result in pool.map(download, weapons.items()):
            if result:
                manifest["images"][name] = result
    print("Icons imported:", sum("file" in result for result in manifest["images"].values()))
    names = {lang: {} for lang in ("en", "fr", "de", "es", "ja", "cs")}
    repo = repositories[1]
    for lang, directory in (
        ("en", "engus"),
        ("fr", "frafr"),
        ("de", "deude"),
        ("es", "spaes"),
        ("ja", "jpnjp"),
    ):
        url = f"https://raw.githubusercontent.com/{repo}/{commits[repo]}/{directory}/item.msgbnd.dcx.json"
        text = json.loads(fetch(url))
        table = next(v for k, v in text.items() if k.endswith("WeaponName.fmg"))
        names[lang] = {
            name: table[str(entry["id"])]
            for name, entry in weapons.items()
            if table.get(str(entry["id"]))
        }
        manifest["names"][lang] = {"source": url, "official_base_count": len(names[lang])}
    repo = repositories[2]
    for lang, prefix, directory in (("en", "GameText", "engUS"), ("ja", "GameTextJP", "jpnJP")):
        for suffix in ("01", "02"):
            url = f"https://raw.githubusercontent.com/{repo}/{commits[repo]}/{prefix}/GR/data/INTERROOT_win64/msg/{directory}/WeaponName_dlc{suffix}.fmg.xml"
            table = {e.attrib["id"]: (e.text or "") for e in ET.fromstring(fetch(url)).iter("text")}
            names[lang].update(
                {
                    name: table[str(entry["id"])]
                    for name, entry in weapons.items()
                    if table.get(str(entry["id"]))
                }
            )
        manifest["names"][lang]["base_and_dlc_count"] = len(names[lang])
    (ROOT / "assets" / "weapon_names.json").write_text(
        json.dumps(names, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ROOT / "assets" / "catalogue_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Names imported:", {lang: len(entries) for lang, entries in names.items()})
    print("Missing localized DLC names:", [n for n in weapons if n not in names["fr"]])


if __name__ == "__main__":
    main()
