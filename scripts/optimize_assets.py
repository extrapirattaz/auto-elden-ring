"""Create compact, offline WebP assets and retain source provenance."""

import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def main():
    path = ROOT / "assets/catalogue_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    before = after = 0
    for entry in manifest["images"].values():
        original = ROOT / entry["file"]
        if original.suffix == ".webp":
            continue
        target = original.with_suffix(".webp")
        before += original.stat().st_size
        with Image.open(original) as image:
            image.thumbnail((136, 136), Image.Resampling.LANCZOS)
            image.save(target, "WEBP", quality=84, method=6)
        with Image.open(target) as image:
            image.load()
        entry["source_sha256"] = entry["sha256"]
        entry["file"] = target.relative_to(ROOT).as_posix()
        entry["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        after += target.stat().st_size
        original.unlink()
    manifest["processing"] = (
        "136px maximum; WebP quality 84; source URLs and original hashes retained."
    )
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print({"catalogue_original_bytes": before, "catalogue_webp_bytes": after})


if __name__ == "__main__":
    main()
