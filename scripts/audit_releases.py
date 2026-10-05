"""Verify immutable historical source/binary pairs and public archive contents."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parent.parent
PRIVATE_FILES = {"profiles-v3.json", "session-v2.json", "session.json"}


def digest(content):
    return hashlib.sha256(content).hexdigest()


def audit(directory, private_terms=(), allow_private_history=False):
    manifest = json.loads((directory / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    for name, expected in manifest["artifacts_sha256"].items():
        assert (
            digest((directory / name).read_bytes()) == expected
        ), f"Artifact mismatch: {version}/{name}"
    source_path = directory / f"auto-elden-ring-{version}-source.zip"
    personal_paths = []
    with zipfile.ZipFile(source_path) as source:
        entries = source.namelist()
        prefix = f"auto-elden-ring-{version}/"
        for name, expected in manifest["source_files_sha256"].items():
            assert (
                digest(source.read(prefix + name)) == expected
            ), f"Source mismatch: {version}/{name}"
        for name in entries:
            path = Path(name)
            assert path.name not in PRIVATE_FILES and path.suffix not in (
                ".sl2",
                ".co2",
            ), f"Private state: {name}"
            assert (
                ".venv" not in path.parts and ".build" not in path.parts
            ), f"Development data: {name}"
            if path.suffix in (".py", ".md", ".json", ".txt", ".yml", ".toml"):
                content = source.read(name)
                if re.search(
                    rb"[A-Z]:[\\/]+Users[\\/]+(?!Public[\\/]|Default[\\/]|YourName[\\/])[^\\/\r\n\"]+[\\/]",
                    content,
                    re.I,
                ):
                    personal_paths.append(name.removeprefix(prefix))
                for term in private_terms:
                    assert (
                        term.encode("utf-8") not in content
                    ), f"Personal state reference: {version}/{name}"
    exe_name = f"Auto-Elden-Ring-{version}-win-x64.exe"
    with zipfile.ZipFile(directory / f"auto-elden-ring-{version}-windows-x64.zip") as portable:
        assert digest(portable.read(exe_name)) == digest((directory / exe_name).read_bytes())
        for name in portable.namelist():
            path = Path(name)
            assert path.name not in PRIVATE_FILES and path.suffix not in (".sl2", ".co2")
    if personal_paths and not allow_private_history:
        raise AssertionError(
            f"Personal-path example in {version}; exclude it or build a sanitized successor."
        )
    return {
        "version": version,
        "status": "EXCLUDED_FROM_PUBLIC_UPLOAD" if personal_paths else "PASS",
        "source_files": len(manifest["source_files_sha256"]),
        "source_and_binary_hashes_match": True,
        "portable_binary_matches": True,
        "no_local_profiles_saves_or_personal_path": not personal_paths,
        "personal_path_files": personal_paths,
        "assets": sorted(p.name for p in directory.iterdir() if p.is_file()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True)
    parser.add_argument("--private-state", type=Path)
    parser.add_argument("--allow-private-history", action="store_true")
    args = parser.parse_args()
    private_terms = []
    if args.private_state and args.private_state.is_file():
        # Keep private identifiers in memory only; neither values nor paths are
        # written to the public report. Generic placeholder names are not private.
        data = json.loads(args.private_state.read_text(encoding="utf-8"))
        for profile in data.get("profiles", {}).values():
            state = profile["state"]
            name = state.get("character_name", "")
            if len(name) >= 4 and name not in ("Tarnished", "Demo Tarnished", "Demo", "Character"):
                private_terms.append(name)
            for key in ("music_file", "custom_background"):
                if state.get(key):
                    private_terms.append(state[key])
    versions = sorted(
        (ROOT / "releases").iterdir(), key=lambda p: tuple(map(int, p.name.split(".")))
    )
    report = {
        "status": "PASS",
        "personal_identifiers_checked_without_disclosure": len(private_terms),
        "releases": [
            audit(path, private_terms, args.allow_private_history)
            for path in versions
            if path.is_dir()
        ],
        "notes": "Historical artifacts were verified, not rebuilt or silently rewritten. Images are development screenshots; game-media licensing is documented separately.",
    }
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"PASS: {len(report['releases'])} version-matched release folders audited.")


if __name__ == "__main__":
    main()
