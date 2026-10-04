"""Shared character, weapon, material and farming workflows.

The UI only edits this state. Purchases and completed upgrades are explicit
transactions, so reopening a screen never spends runes or consumes materials.
"""
from copy import deepcopy
from fractions import Fraction
from classes_data import CLASS_DATA, ATTRIBUTES
from .core import (integer, stats_level, generic_weapon, inverse_base,
                   shopping_plan, STONE_PRICES, MAX_LEVEL)
from .styles import STYLES, PALETTES

LANGUAGES = ("en","fr","cs","de","es","ja")
THEMES = tuple(PALETTES)
TALISMANS = {"none":100,"gold":120,"silver":100}
CONSUMABLES = {"none":100,"gold_foot":130,"silver_foot":100,"gold_horn":140,"silver_horn":100}


def default_state():
    stats = deepcopy(CLASS_DATA["Vagabond"]["stats"])
    return {"language":"en","theme":"calm","style":"modern","dyslexic":False,
            "character_name":"Tarnished","journey_name":"Journey 1","music_file":"",
            "custom_background":"","inventory_armor":[],"inventory_items":[],"equipment":[],"profile_created":False,"save_link":{},"inventory_weapons":[],"farm_spots":[],
            "purchased":{},"class_name":"Vagabond",
            "stats_current":deepcopy(stats),"stats_target":deepcopy(stats),"runes":0,
            "wallet_baseline":None,"runes_spent":0,"weapon_mode":"manual",
            "manual":{"name":"","kind":"normal","base":130,"input_mode":"base",
                      "observed":130,"current":0,"target":24,"quantity":1},
            "selected":[],"stock":{k:0 for k in STONE_PRICES if not k.endswith("dragon")},
            "prices":{},"farm":{"runes":0,"seconds":60,"efficiency":100,"talisman":"none",
              "consumable":"none","notes":"","goal":"combined","free_goal":100000,"maximum_current":None,"samples":[],"use_samples":False}}


def buff_multiplier(talisman,consumable):
    if talisman not in TALISMANS or consumable not in CONSUMABLES:
        raise ValueError("Unknown rune buff.")
    # Consumables are mutually exclusive. The talisman stacks multiplicatively.
    return Fraction(TALISMANS[talisman]*CONSUMABLES[consumable],10000)


def validate_state(state,db):
    if not isinstance(state,dict) or set(state)!=set(default_state()):
        raise ValueError("Invalid project structure.")
    if state["language"] not in LANGUAGES or state["theme"] not in THEMES:
        raise ValueError("Unknown language or theme.")
    if state["style"] not in STYLES or state["theme"] not in STYLES[state["style"]]["themes"]:
        raise ValueError("The selected color palette does not belong to this style.")
    if not isinstance(state["dyslexic"],bool):
        raise ValueError("Invalid reading preference.")
    for key in ("character_name","journey_name","music_file","custom_background"):
        if not isinstance(state[key],str) or len(state[key])>4096:
            raise ValueError("Invalid profile text.")
    if not isinstance(state["profile_created"],bool) or not isinstance(state["save_link"],dict):
        raise ValueError("Invalid profile metadata.")
    if not isinstance(state["inventory_weapons"],list) or len(state["inventory_weapons"])>4608:
        raise ValueError("Invalid owned weapons.")
    for item in state["inventory_weapons"]:
        weapon=db.weapons[item["name"]]
        integer(item["current"],"Owned upgrade",0,weapon.maximum)
        integer(item["quantity"],"Owned copies",1)
    for key in ("inventory_armor","inventory_items","equipment"):
        if not isinstance(state[key],list) or len(state[key])>4608:
            raise ValueError("Invalid inventory records.")
        for item in state[key]:
            integer(item["id"],"Item ID",1,0xffffffff)
            integer(item["quantity"],"Item quantity",1,999999)
            if key=="equipment":
                integer(item["slot"],"Equipment slot",0,21)
                if "name" in item:
                    integer(item["current"],"Equipped upgrade",0,db.weapons[item["name"]].maximum)
    if not isinstance(state["farm_spots"],list) or len(state["farm_spots"])>100:
        raise ValueError("Invalid farming spots.")
    for spot in state["farm_spots"]:
        if not isinstance(spot["name"],str) or not spot["name"].strip():
            raise ValueError("Invalid farming spot name.")
        validate_state({**state,"farm_spots":[],"farm":spot["farm"]},db)
    for key,value in state["purchased"].items():
        if key not in state["stock"]:
            raise ValueError("Invalid purchased material.")
        integer(value,"Purchased quantity",1)
    for key in ("stats_current","stats_target"):
        stats_level(state["class_name"],state[key])
    for key in ("runes","runes_spent"):
        integer(state[key],key)
    if state["wallet_baseline"] is not None:
        integer(state["wallet_baseline"])
    if state["weapon_mode"] not in ("manual","catalogue"):
        raise ValueError("Unknown weapon mode.")
    m = state["manual"]
    if m["kind"] not in ("normal","somber") or m["input_mode"] not in ("base","next") or not isinstance(m["name"],str):
        raise ValueError("Invalid manual weapon.")
    maximum = 25 if m["kind"]=="normal" else 10
    current = integer(m["current"],"Current upgrade",0,maximum)
    integer(m["target"],"Target upgrade",current,maximum)
    integer(m["base"],"Base cost",1)
    integer(m["observed"],"Observed cost",1)
    integer(m["quantity"],"Copies",1,999)
    if not isinstance(state["selected"],list):
        raise ValueError("Invalid weapon selection.")
    seen = set()
    for item in state["selected"]:
        w = db.weapons[item["name"]]
        if w.name in seen:
            raise ValueError("Duplicate selected weapon.")
        seen.add(w.name)
        current = integer(item["current"],"Current upgrade",0,w.maximum)
        integer(item["target"],"Target upgrade",current,w.maximum)
        integer(item["quantity"],"Copies",1,999)
    for key,value in state["stock"].items():
        if key not in STONE_PRICES or key.endswith("dragon"):
            raise ValueError("Unknown inventory material.")
        integer(value,"Owned stones")
    for key,value in state["prices"].items():
        if key not in STONE_PRICES or key.endswith("dragon"):
            raise ValueError("Ancient dragon stones are outside the purchase planner.")
        integer(value,"Stone price")
    f = state["farm"]
    integer(f["runes"],"Measured runes")
    integer(f["seconds"],"Measured duration",1,86400)
    integer(f["efficiency"],"Efficiency",1,100)
    integer(f["free_goal"],"Free goal")
    if f.get("maximum_current") is not None:
        integer(f["maximum_current"],"Current level",1,MAX_LEVEL)
        if f["goal"]=="maximum":
            integer(f["maximum_current"],"Current level",CLASS_DATA[state["class_name"]]["level"],MAX_LEVEL)
    buff_multiplier(f["talisman"],f["consumable"])
    if f["goal"] not in ("combined","character","weapons","maximum","free") or not isinstance(f["notes"],str):
        raise ValueError("Invalid farming goal.")
    if not isinstance(f["samples"],list) or len(f["samples"])>100:
        raise ValueError("Invalid farming samples.")
    for sample in f["samples"]:
        integer(sample["runes"],"Sample runes")
        integer(sample["seconds"],"Sample duration",1,86400)
        buff_multiplier(sample["talisman"],sample["consumable"])
        if not isinstance(sample["notes"],str):
            raise ValueError("Invalid sample notes.")
    if not isinstance(f["use_samples"],bool):
        raise ValueError("Invalid sample mode.")
    return state


class Planner:
    def __init__(self,db,state=None):
        self.db = db
        self.state = deepcopy(state) if state is not None else default_state()
        validate_state(self.state,db)

    def character(self):
        s = self.state
        current = stats_level(s["class_name"],s["stats_current"])
        requested = stats_level(s["class_name"],s["stats_target"])
        target = max(current,requested)
        reachable,left = self.db.affordable_level(current,s["runes"])
        respec = any(s["stats_target"][a]<s["stats_current"][a] for a in ATTRIBUTES)
        return {"current":current,"target":requested,"levels":max(0,requested-current),
                "cost":self.db.level_cost(current,target),
                "spent":self.db.level_cost(CLASS_DATA[s["class_name"]]["level"],current),
                "maximum_cost":self.db.level_cost(current,MAX_LEVEL),
                "reachable":reachable,"left":left,"respec":respec,
                "deficit":max(0,self.db.level_cost(current,target)-s["runes"])}

    def set_wallet(self,value):
        value = integer(value,"Runes held")
        if self.state["wallet_baseline"] is None:
            self.state["wallet_baseline"] = value
        self.state["runes"] = value

    def tracked_gain(self):
        baseline = self.state["wallet_baseline"]
        return max(0,self.state["runes"]-(baseline or 0)+self.state["runes_spent"])

    def manual_weapon(self):
        m = self.state["manual"]
        base = m["base"]
        if m["input_mode"]=="next":
            maximum = 25 if m["kind"]=="normal" else 10
            if m["current"]>=maximum:
                raise ValueError("A maximum-upgrade weapon has no next upgrade.")
            bases = inverse_base(m["kind"],m["current"],m["current"]+1,m["observed"])
            if len(bases)!=1:
                raise ValueError("The observed cost does not identify one standard-profile base cost.")
            base = bases[0]
        return generic_weapon(m["name"],m["kind"],base)

    def items(self):
        if self.state["weapon_mode"]=="manual":
            m = self.state["manual"]
            return [{"weapon":self.manual_weapon(),"current":m["current"],"target":m["target"],"quantity":m["quantity"]}]
        return [{**item,"weapon":self.db.weapons[item["name"]]} for item in self.state["selected"]]

    def weapons(self,items=None):
        s = self.state
        plan = shopping_plan(self.items() if items is None else items,owned=s["stock"],prices=s["prices"])
        plan["deficit"] = max(0,plan["total"]-s["runes"])
        plan["dragon_needed"] = sum(row["missing"] for row in plan["stones"] if row["key"].endswith("dragon"))
        return plan

    def affordable_targets(self):
        """Find the highest shared target affordable for the selected copies.

        Current upgrades are never reduced. The ordinary-material budget stops
        at +24/+9 because ancient dragon stones are outside this workflow.
        """
        items = self.items()
        if not items:
            return [],self.state["runes"]
        best = [{**item,"target":item["current"]} for item in items]
        paid = 0
        low,high=1,24
        # Total costs are monotone: at most five shared-budget evaluations.
        while low<=high:
            common=(low+high)//2
            candidate = [{**i,"target":max(i["current"],min(common,24 if i["weapon"].maximum==25 else 9 if i["weapon"].maximum==10 else 0))} for i in items]
            cost = self.weapons(candidate)["total"]
            if cost>self.state["runes"]:
                high=common-1
            else:
                best,paid = candidate,cost
                low=common+1
        return best,self.state["runes"]-paid

    def toggle_weapon(self,name):
        selection = self.state["selected"]
        existing = next((i for i in selection if i["name"]==name),None)
        if existing:
            selection.remove(existing)
        else:
            w = self.db.weapons[name]
            current=min((i["current"] for i in self.state["inventory_weapons"] if i["name"]==name),default=0)
            selection.append({"name":name,"current":current,"target":max(current,24 if w.maximum==25 else 9 if w.maximum==10 else 0),"quantity":1})

    def without_dragon(self):
        if self.state["weapon_mode"]=="manual":
            m = self.state["manual"]
            m["target"] = max(m["current"],24 if m["kind"]=="normal" else 9)
        else:
            for item in self.state["selected"]:
                w = self.db.weapons[item["name"]]
                item["target"] = max(item["current"],24 if w.maximum==25 else 9 if w.maximum==10 else 0)

    def purchase(self,key):
        if key.endswith("dragon"):
            raise ValueError("Ancient dragon stones are outside the purchase planner.")
        row = next((r for r in self.weapons()["stones"] if r["key"]==key),None)
        if not row or not row["missing"]:
            raise ValueError("No missing stones of this type.")
        self.state["stock"][key] = self.state["stock"].get(key,0)+row["missing"]
        # This acknowledges an in-game action, independent of the planning wallet.
        self.state["purchased"][key]=self.state["purchased"].get(key,0)+row["missing"]
        return row["missing"],row["cost"]

    def complete_upgrades(self,dragon_confirmed=False):
        plan = self.weapons()
        # The user confirms the real outcome, not a simulated purchase transaction.
        base=self.manual_weapon().base if self.state["weapon_mode"]=="manual" else None
        self.state["stock"]={key:0 for key in self.state["stock"]}
        self.state["runes"]=0
        self.state["wallet_baseline"]=0
        self.state["runes_spent"]=0
        self.state["purchased"]={}
        if self.state["weapon_mode"]=="manual":
            m = self.state["manual"]
            # Preserve the recovered base when the observed next passage expires.
            m["base"] = base
            m["current"] = m["target"]
            m["input_mode"] = "base"
        else:
            for item in self.state["selected"]:
                item["current"] = item["target"]

    def add_sample(self,runes,seconds,talisman=None,consumable=None,notes=None):
        f = self.state["farm"]
        sample = {"runes":integer(runes,"Measured runes"),"seconds":integer(seconds,"Duration",1,86400),
                  "talisman":talisman or f["talisman"],"consumable":consumable or f["consumable"],"notes":f["notes"] if notes is None else notes}
        buff_multiplier(sample["talisman"],sample["consumable"])
        f["samples"].append(sample)
        f["use_samples"] = True
        return sample

    def farm_rates(self):
        f = self.state["farm"]
        samples = f["samples"] if f["use_samples"] and f["samples"] else [{k:f[k] for k in ("runes","seconds","talisman","consumable")}]
        seconds = sum(s["seconds"] for s in samples)
        measured = Fraction(sum(s["runes"] for s in samples)*60,seconds)
        baseline = sum(Fraction(s["runes"])/buff_multiplier(s["talisman"],s["consumable"]) for s in samples)*60/seconds
        return {"measured":measured,"baseline":baseline,"gold_scarab":baseline*Fraction(6,5),
                "gold_foot":baseline*Fraction(13,10),"scarab_foot":baseline*Fraction(39,25),
                "optimized":baseline*Fraction(42,25),"seconds":seconds,"samples":len(samples)}

    def farm_goal(self):
        f = self.state["farm"]
        if f["goal"]=="free":
            return f["free_goal"],False
        c = self.character()
        if f["goal"]=="character":
            return c["cost"],False
        if f["goal"]=="maximum":
            return self.db.level_cost(self.maximum_farm_level(),MAX_LEVEL),False
        w = self.weapons()
        return w["total"]+(c["cost"] if f["goal"]=="combined" else 0),bool(w["dragon_needed"])

    def maximum_farm_level(self):
        """Use the explicit farm level without inventing character attributes."""
        level=self.state["farm"].get("maximum_current")
        return integer(self.character()["current"] if level is None else level,
                       "Current level",CLASS_DATA[self.state["class_name"]]["level"],MAX_LEVEL)

    def farm_projection(self):
        rates = self.farm_rates()
        if rates["measured"]<=0:
            raise ValueError("Record a positive rune gain before estimating time.")
        goal,incomplete = self.farm_goal()
        remaining = max(0,goal-self.state["runes"])
        efficiency = Fraction(self.state["farm"]["efficiency"],100)
        current=self.maximum_farm_level() if self.state["farm"]["goal"]=="maximum" else self.character()["current"]
        maximum = max(0,self.db.level_cost(current,MAX_LEVEL)-self.state["runes"])
        invested=self.db.level_cost(CLASS_DATA[self.state["class_name"]]["level"],current)
        def duration(cost,rate):
            return int(-(-Fraction(cost*60)//(rate*efficiency)))
        return {**rates,"remaining":remaining,"goal":goal,"incomplete":incomplete,
                "time":duration(remaining,rates["measured"]),"maximum_time":duration(maximum,rates["measured"]),
                "optimized_time":duration(remaining,rates["optimized"]),
                "invested":invested,"invested_time":duration(invested,rates["measured"])}
