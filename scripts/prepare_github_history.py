"""Prepare exact versioned source commits/tags locally, without a remote or push.

The bundle is for a new empty repository. Original release authorship is not
invented: each commit is explicitly an archive import performed now. Historical
code is kept as built; the newest snapshot becomes main. Run after building the
current release. Existing destination repositories are never overwritten.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def git(directory, *args):
    return subprocess.check_output(
        ["git", "-C", str(directory), "-c", "commit.gpgsign=false", *args],
        text=True,
        encoding="utf-8",
        stderr=subprocess.STDOUT,
    ).strip()


def prepare(destination, bundle):
    destination = Path(destination).resolve()
    bundle = Path(bundle).resolve()
    if destination.exists() or bundle.exists():
        raise ValueError("The local history destination or bundle already exists.")
    destination.mkdir(parents=True)
    git(destination, "init", "--initial-branch=main", "--object-format=sha1")
    git(destination, "config", "user.name", "Auto Elden Ring Archive Import")
    git(destination, "config", "user.email", "archive@auto-elden-ring.invalid")
    git(destination, "config", "core.autocrlf", "false")
    git(destination, "config", "core.hooksPath", str(destination / ".git/unused-hooks"))
    previous = set()
    versions = sorted(
        (p for p in (ROOT / "releases").iterdir() if p.is_dir()),
        key=lambda p: tuple(map(int, p.name.split("."))),
    )
    imported = []
    for directory in versions:
        if directory.name == "1.0.0":
            continue  # Original private-path example is replaced by 1.0.1.
        version = directory.name
        manifest = json.loads((directory / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        source = directory / f"auto-elden-ring-{version}-source.zip"
        expected = manifest["artifacts_sha256"][source.name]
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError(f"The {version} source archive does not match its manifest.")
        current = set(manifest["source_files_sha256"])
        blob_hashes = {}
        for name in previous - current:
            target = (destination / name).resolve()
            if (
                not target.is_relative_to(destination)
                or ".git" in target.relative_to(destination).parts
            ):
                raise ValueError("An archive path escapes the source repository.")
            target.unlink(missing_ok=True)
        with zipfile.ZipFile(source) as archive:
            for name, expected in manifest["source_files_sha256"].items():
                target = (destination / name).resolve()
                if (
                    not target.is_relative_to(destination)
                    or ".git" in target.relative_to(destination).parts
                ):
                    raise ValueError("An archive path escapes the source repository.")
                content = archive.read(f"auto-elden-ring-{version}/{name}")
                if hashlib.sha256(content).hexdigest() != expected:
                    raise ValueError(f"The {version} source file does not match its manifest.")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
                blob_hashes[name] = hashlib.sha1(
                    b"blob " + str(len(content)).encode() + b"\0" + content
                ).hexdigest()
        # This new repository contains only verified archive files. Force-stage
        # the snapshot so historical/global ignore patterns cannot omit docs.
        # The complete tree is checked below before any bundle can be emitted.
        git(destination, "add", "--force", "--all")
        git(destination, "commit", "-m", f"Import Auto Elden Ring {version} source snapshot")
        git(
            destination,
            "tag",
            "-a",
            f"v{version}",
            "-m",
            f"Exact {version} release source archive import",
        )
        # Git blobs must also retain the exact source bytes, including line endings.
        tree = git(destination, "ls-tree", "-r", f"v{version}")
        for row in tree.splitlines():
            metadata, name = row.split("\t", 1)
            blob = metadata.split()[2]
            if blob != blob_hashes[name]:
                raise ValueError(f"Git changed the archived bytes of {version}/{name}.")
        if len(tree.splitlines()) != len(current):
            raise ValueError("Git tracked unexpected source files.")
        previous = current
        imported.append(version)
    bundle.parent.mkdir(parents=True, exist_ok=True)
    git(destination, "bundle", "create", str(bundle), "--all")
    git(destination, "bundle", "verify", str(bundle))
    return {
        "status": "PASS",
        "versions": imported,
        "main_version": imported[-1],
        "source_blobs_match_release_manifests": True,
        "remote_publication": False,
        "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    report = prepare(args.destination, args.bundle)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Prepared {len(report['versions'])} exact source tags locally. No remote was created.")


if __name__ == "__main__":
    main()
