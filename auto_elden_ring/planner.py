"""Shared character, weapon, material and farming workflows.

The UI only edits this state. Purchases and completed upgrades are explicit
transactions, so reopening a screen never spends runes or consumes materials.
"""
from copy import deepcopy
from fractions import Fraction
from classes_data import CLASS_DATA, ATTRIBUTES
from .core import (integer, stats_level, generic_weapon, inverse_base,
                   shopping_plan, STONE_PRICES, MAX_LEVEL)

LANGUAGES = ("en","fr","cs","de","es","ja")
THEMES = ("calm","elden","slate")
TALISMANS = {"none":100,"gold":120,"silver":100}
CONSUMABLES = {"none":100,"gold_foot":130,"silver_foot":100,"gold_horn":140,"silver_horn":100}


def default_state():
    stats = deepcopy(CLASS_DATA["Vagabond"]["stats"])
    return {"language":"en","theme":"calm","class_name":"Vagabond",
            "stats_current":deepcopy(stats),"stats_target":deepcopy(stats),"runes":0,
            "wallet_baseline":None,"runes_spent":0,"weapon_mode":"manual",
            "manual":{"name":"","kind":"normal","base":130,"input_mode":"base",
                      "observed":130,"current":0,"target":24,"quantity":1},
            "selected":[],"stock":{k:0 for k in STONE_PRICES if not k.endswith("dragon")},
            "prices":{},"farm":{"runes":0,"seconds":60,"efficiency":100,"talisman":"none",
              "consumable":"none","notes":"","goal":"combined","free_goal":100000,"samples":[],"use_samples":False}}


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
        for common in range(1,25):
            candidate = [{**i,"target":max(i["current"],min(common,24 if i["weapon"].maximum==25 else 9 if i["weapon"].maximum==10 else 0))} for i in items]
            cost = self.weapons(candidate)["total"]
            if cost>self.state["runes"]:
                break
            best,paid = candidate,cost
        return best,self.state["runes"]-paid

    def toggle_weapon(self,name):
        selection = self.state["selected"]
        existing = next((i for i in selection if i["name"]==name),None)
        if existing:
            selection.remove(existing)
        else:
            w = self.db.weapons[name]
            selection.append({"name":name,"current":0,"target":24 if w.maximum==25 else 9 if w.maximum==10 else 0,"quantity":1})

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
        if row["cost"]>self.state["runes"]:
            raise ValueError("Not enough held runes for this purchase.")
        self.state["stock"][key] = self.state["stock"].get(key,0)+row["missing"]
        self.state["runes"] -= row["cost"]
        self.state["runes_spent"] += row["cost"]
        return row["missing"],row["cost"]

    def complete_upgrades(self,dragon_confirmed=False):
        plan = self.weapons()
        if any(r["missing"] for r in plan["stones"] if not r["key"].endswith("dragon")):
            raise ValueError("Buy or record the missing smithing stones first.")
        if plan["dragon_needed"] and not dragon_confirmed:
            raise ValueError("Confirm that the required ancient dragon stones were obtained separately.")
        if plan["forge"]>self.state["runes"]:
            raise ValueError("Not enough held runes for the blacksmith.")
        for row in plan["stones"]:
            if not row["key"].endswith("dragon"):
                self.state["stock"][row["key"]] -= row["required"]
        self.state["runes"] -= plan["forge"]
        self.state["runes_spent"] += plan["forge"]
        if self.state["weapon_mode"]=="manual":
            m = self.state["manual"]
            # Preserve the recovered base when the observed next passage expires.
            m["base"] = self.manual_weapon().base
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
            return c["maximum_cost"],False
        w = self.weapons()
        return w["total"]+(c["cost"] if f["goal"]=="combined" else 0),bool(w["dragon_needed"])

    def farm_projection(self):
        rates = self.farm_rates()
        if rates["measured"]<=0:
            raise ValueError("Record a positive rune gain before estimating time.")
        goal,incomplete = self.farm_goal()
        remaining = max(0,goal-self.state["runes"])
        efficiency = Fraction(self.state["farm"]["efficiency"],100)
        maximum = max(0,self.character()["maximum_cost"]-self.state["runes"])
        def duration(cost,rate):
            return int(-(-Fraction(cost*60)//(rate*efficiency)))
        return {**rates,"remaining":remaining,"goal":goal,"incomplete":incomplete,
                "time":duration(remaining,rates["measured"]),"maximum_time":duration(maximum,rates["measured"]),
                "optimized_time":duration(remaining,rates["optimized"])}
