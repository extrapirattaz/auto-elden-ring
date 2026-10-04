"""Independent journeys and immutable, date-sorted checkpoint snapshots."""
from copy import deepcopy
from datetime import datetime
import json
import os
from pathlib import Path
import tempfile
from uuid import uuid4
from classes_data import CLASS_DATA
from .planner import default_state, validate_state


def timestamp(value=None):
    if value and "/" in value:
        result=datetime.strptime(value,"%d/%m/%Y %H:%M")
    else:
        result=datetime.fromisoformat(value) if value else datetime.now().astimezone()
    # A user-specified local date is assigned the system's local timezone.
    if result.tzinfo is None:
        result=result.astimezone()
    return result.isoformat(timespec="seconds")


class Profiles:
    def __init__(self,db,state=None):
        self.db=db
        ident=uuid4().hex
        self.data={"schema":1,"active":ident,"profiles":{ident:{"state":deepcopy(state or default_state()),"checkpoints":[]}}}

    @property
    def active(self):
        return self.data["profiles"][self.data["active"]]

    def sync(self,state):
        validate_state(state,self.db)
        self.active["state"]=deepcopy(state)

    def create(self,name,journey,class_name,preferences=None):
        if len(self.data["profiles"])>=100:
            raise ValueError("The profile library is full (100 characters).")
        if not name.strip() or not journey.strip() or class_name not in CLASS_DATA:
            raise ValueError("Enter a character name, journey name and starting class.")
        state=default_state()
        state.update(character_name=name.strip(),journey_name=name.strip(),class_name=class_name,profile_created=True)
        state["stats_current"]=deepcopy(CLASS_DATA[class_name]["stats"])
        state["stats_target"]=deepcopy(state["stats_current"])
        if preferences:
            for key in ("style","theme","language","dyslexic","music_file"):
                state[key]=preferences[key]
        ident=uuid4().hex
        self.data["profiles"][ident]={"state":state,"checkpoints":[]}
        self.data["active"]=ident
        return deepcopy(state)

    def select(self,ident):
        if ident not in self.data["profiles"]:
            raise ValueError("Unknown character profile.")
        self.data["active"]=ident
        return deepcopy(self.active["state"])

    def checkpoint(self,state,note="",date=None):
        if len(self.active["checkpoints"])>=10000:
            raise ValueError("The timeline is full (10,000 events).")
        validate_state(state,self.db)
        entry={"id":uuid4().hex,"date":timestamp(date),"note":str(note),"state":deepcopy(state)}
        self.active["checkpoints"].append(entry)
        self.active["checkpoints"].sort(key=lambda e:datetime.fromisoformat(e["date"]))
        return deepcopy(entry)

    def validate(self):
        data=self.data
        if data.get("schema")!=1 or data["active"] not in data["profiles"] or len(data["profiles"])>100:
            raise ValueError("Invalid profile library.")
        from .storage import upgrade_state
        for profile in data["profiles"].values():
            if "profile_created" not in profile["state"]:
                placeholder=profile["state"].get("character_name")=="Tarnished" and profile["state"].get("journey_name")=="Journey 1" and not profile["checkpoints"]
                profile["state"]=upgrade_state(profile["state"])
                profile["state"]["profile_created"]=not placeholder
            validate_state(profile["state"],self.db)
            if not isinstance(profile["checkpoints"],list) or len(profile["checkpoints"])>10000:
                raise ValueError("Invalid checkpoint timeline.")
            for point in profile["checkpoints"]:
                point["state"]=upgrade_state(point["state"])
                timestamp(point["date"])
                if not isinstance(point["note"],str) or not isinstance(point["id"],str):
                    raise ValueError("Invalid checkpoint.")
                validate_state(point["state"],self.db)
        return data

    def save(self,path,state):
        self.sync(state)
        self.validate()
        path=Path(path)
        path.parent.mkdir(parents=True,exist_ok=True)
        fd,temp=tempfile.mkstemp(dir=path.parent,prefix=".profiles-",suffix=".tmp")
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as file:
                json.dump(self.data,file,ensure_ascii=False,separators=(",",":"))
            os.replace(temp,path)
        finally:
            Path(temp).unlink(missing_ok=True)

    @classmethod
    def load(cls,path,db):
        try:
            instance=cls(db)
            instance.data=json.loads(Path(path).read_text(encoding="utf-8"))
            instance.validate()
            return instance
        except (KeyError,TypeError,AttributeError) as exc:
            raise ValueError("Invalid profile library.") from exc
