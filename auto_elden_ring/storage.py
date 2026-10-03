"""Atomic, versioned persistence for offline build projects."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
from . import __version__
from .planner import validate_state
from .planner import default_state


def load_project(path, db):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("schema") not in (2,3):
            raise ValueError("Unsupported project schema; version 1 projects need version 1.")
        if data["data_sha256"] != hashlib.sha256(db.path.read_bytes()).hexdigest():
            raise ValueError("This project uses a different game cost database.")
        state=data["state"]
        if data["schema"]==2:
            state=upgrade_state(state)
        return validate_state(state, db)
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("Incomplete or invalid project.") from exc


def save_project(path, state, db):
    validate_state(state, db)
    data = {"schema": 3, "app_version": __version__,
            "data_sha256": hashlib.sha256(db.path.read_bytes()).hexdigest(), "state": state}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".auto-elden-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def upgrade_state(state):
    """Import version-2 preferences without discarding build progress."""
    result=default_state()
    result.update(state)
    if "style" not in state:
        result["style"]="elden" if state.get("theme")=="elden" else "modern"
    return result
