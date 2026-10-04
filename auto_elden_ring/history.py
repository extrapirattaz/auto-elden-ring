"""Import snapshots, stable save-slot matching and human-readable changes."""
from copy import deepcopy
from .planner import default_state


def differences(before,after):
    changes=[]
    for key in ("class_name","character_name","runes"):
        if before[key]!=after[key]:
            changes.append({"field":key,"before":before[key],"after":after[key]})
    for stat,value in after["stats_current"].items():
        if before["stats_current"][stat]!=value:
            changes.append({"field":stat,"before":before["stats_current"][stat],"after":value})
    def owned(state):
        return {(i["name"],i["current"]):i["quantity"] for i in state["inventory_weapons"]}
    old,new=owned(before),owned(after)
    for weapon in sorted(set(old)|set(new)):
        if old.get(weapon,0)!=new.get(weapon,0):
            changes.append({"field":"weapon","name":weapon[0],"upgrade":weapon[1],
                            "before":old.get(weapon,0),"after":new.get(weapon,0)})
    for key,value in after["stock"].items():
        if before["stock"].get(key,0)!=value:
            changes.append({"field":key,"before":before["stock"].get(key,0),"after":value})
    return changes


def import_characters(profiles,characters,preferences,replace_manual=False):
    # A rejected character must not leave a partially imported profile library.
    previous=deepcopy(profiles.data)
    try:
        if replace_manual and characters:
            profiles.data["profiles"]={i:p for i,p in profiles.data["profiles"].items()
                if p["state"]["save_link"] or not p["state"]["profile_created"]}
        return _apply_import(profiles,characters,preferences)
    except Exception:
        profiles.data=previous
        raise


def _apply_import(profiles,characters,preferences):
    active=profiles.data["active"]
    results=[]
    for character in characters:
        ident=next((ident for ident,p in profiles.data["profiles"].items()
                    if p["state"]["save_link"].get("path")==character["source"] and
                    p["state"]["save_link"].get("slot")==character["slot"] and
                    p["state"]["class_name"]==character["class_name"]),None)
        if ident:
            old=deepcopy(profiles.data["profiles"][ident]["state"])
            changed=old["save_link"].get("fingerprint")!=character["fingerprint"]
            state=deepcopy(old)
            previous=next((p["state"] for p in reversed(profiles.data["profiles"][ident]["checkpoints"])
                           if p["note"]=="save_import" and p["state"]["save_link"].get("fingerprint")==old["save_link"].get("fingerprint")),old)
        else:
            state=profiles.create(character["name"],character["name"],character["class_name"],preferences)
            ident=profiles.data["active"]
            old=deepcopy(state)
            previous=old
            changed=True
        state.update(character_name=character["name"],journey_name=character["name"],class_name=character["class_name"],
                     stats_current=deepcopy(character["stats"]),runes=character["runes"],stock=deepcopy(character["stock"]),
                     inventory_weapons=deepcopy(character["weapons"]),purchased={},
                     save_link={"path":character["source"],"slot":character["slot"],"fingerprint":character["fingerprint"],
                                "unknown_items":character["unknown_items"]})
        state["stats_target"]={k:max(v,state["stats_target"][k]) for k,v in state["stats_current"].items()}
        for selected in state["selected"]:
            found=[w for w in state["inventory_weapons"] if w["name"]==selected["name"]]
            if found:
                selected["current"]=min(w["current"] for w in found)
                selected["target"]=max(selected["current"],selected["target"])
        profiles.data["active"]=ident
        if changed:
            point=profiles.checkpoint(state,"save_import")
            next(p for p in profiles.active["checkpoints"] if p["id"]==point["id"])["changes"]=differences(previous,state)
        profiles.sync(state)
        results.append(ident)
    profiles.data["active"]=active if active in profiles.data["profiles"] else results[0]
    return results
