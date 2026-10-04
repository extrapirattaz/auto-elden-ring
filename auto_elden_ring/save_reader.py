"""Read-only PC save prefix reader. Never exposes write-back functionality.

Layout references and MIT attribution are documented in docs/SOURCES.md.
Only bounded, checksum-valid plaintext BND4 slots are accepted.
"""
from collections import Counter
import hashlib
from io import BytesIO
import os
from pathlib import Path
import struct
from classes_data import ATTRIBUTES, CLASS_DATA

CLASSES=("Vagabond","Warrior","Hero","Bandit","Astrologer","Prophet","Confessor","Samurai","Prisoner","Wretch")
SLOT_SIZE=0x280000
STRIDE=SLOT_SIZE+16


def discover(installation=None):
    """Installation files and roaming saves are independent; search both roots."""
    directory=Path(os.environ.get("APPDATA",str(Path.home())))/"EldenRing"
    files=list(directory.glob("*/ER0000.sl2"))+list(directory.glob("*/ER0000.co2"))
    if installation:
        root=Path(installation)
        for folder in (root,root/"Game",root/"save",root/"saves"):
            for pattern in ("*.sl2","*.co2"):
                files.extend(folder.glob(pattern))
    return sorted(set(p.resolve() for p in files if p.is_file()))


def read_saves(paths,db):
    if not 1<=len(paths)<=20:
        raise ValueError("Select between one and twenty PC save files.")
    return [character for path in paths for character in read_save(path,db)]


def read_slot(data,db,index):
    stream=BytesIO(data)
    def take(count):
        value=stream.read(count)
        if len(value)!=count:
            raise ValueError("Truncated save section.")
        return value
    def u32():
        return struct.unpack("<I",take(4))[0]
    version=u32()
    if version==0:
        return None
    if not 1<=version<=1000:
        raise ValueError("Unsupported save version.")
    take(28)
    handles={}
    for _ in range(0x13fe if version<=81 else 0x1400):
        handle,item=u32(),u32()
        if handle:
            handles[handle]=item
        # Physical weapon/armor records carry instance metadata; goods and
        # accessories use the short record, regardless of their handle prefix.
        if handle and item not in (0,0xffffffff):
            kind=item&0xf0000000
            if kind==0:
                take(13)
            elif kind==0x10000000:
                take(8)
    player=take(432)
    stats=dict(zip(ATTRIBUTES,struct.unpack_from("<8I",player,0x34)))
    level,runes=struct.unpack_from("<2I",player,0x60)
    archetype=player[0xb7]
    if archetype>=len(CLASSES):
        raise ValueError("Unknown starting class; modified saves are not supported.")
    class_name=CLASSES[archetype]
    if level!=sum(stats.values())-79 or not 1<=level<=713:
        raise ValueError("Invalid level/attribute consistency.")
    if any(not CLASS_DATA[class_name]["stats"][key]<=value<=99 for key,value in stats.items()):
        raise ValueError("Invalid permanent attributes.")
    name=player[0x94:0xb4].decode("utf-16-le").split("\0",1)[0]
    if not name.strip():
        raise ValueError("Missing character name.")
    take(13*16+88+28)
    equipped_ids=struct.unpack("<22I",take(88))
    equipped_handles=struct.unpack("<22I",take(88))
    count=u32()
    if count>0xa80:
        raise ValueError("Invalid inventory count.")
    entries=[struct.unpack("<3I",take(12)) for _ in range(0xa80)]
    key_count=u32()
    if key_count>0x180:
        raise ValueError("Invalid key inventory count.")
    entries.extend(struct.unpack("<3I",take(12)) for _ in range(0x180))
    take(8)  # Held inventory counters.
    take(116+140+24)  # Spells, quick items/pouch and gestures.
    projectiles=u32()
    if projectiles>200000:
        raise ValueError("Unsupported projectile section.")
    take(projectiles*8+156+12+303)  # Projectiles, equipment, Physick and face.
    storage_count=u32()
    if storage_count>0x780:
        raise ValueError("Invalid storage count.")
    entries.extend(struct.unpack("<3I",take(12)) for _ in range(0x780))
    ids={entry["id"]:name for category in db.raw["weapons_by_category"].values() for name,entry in category.items()}
    weapons=Counter()
    armor=Counter()
    items=Counter()
    stock={f"normal:{tier}":0 for tier in range(1,9)}
    stock.update({f"somber:{tier}":0 for tier in range(1,10)})
    goods={10100+t-1:f"normal:{t}" for t in range(1,9)}
    goods.update({10160+t-1:f"somber:{t}" for t in range(1,9)})
    goods[10200]="somber:9"
    unknown=0
    for handle,quantity,_ in entries:
        if not quantity or handle in (0,0xffffffff):
            continue
        if quantity>999999:
            raise ValueError("Invalid inventory quantity.")
        item=handles.get(handle)
        # Stackable goods and talismans can use directly encoded IDs without
        # an instance-map entry. A missing weapon handle must not be guessed.
        if item is None and handle&0xf0000000 in (0xa0000000,0xb0000000):
            item=(handle&0x0fffffff)|(0x40000000 if handle&0xf0000000==0xb0000000 else 0x20000000)
        if item is None:
            unknown+=1
            continue
        base=item&0x0fffffff
        category=item&0xf0000000
        if category==0:
            weapon_id=base-base%10000
            upgrade=base%100
            weapon_name=ids.get(weapon_id)
            if weapon_name and upgrade<=db.weapons[weapon_name].maximum:
                weapons[weapon_name,upgrade]+=quantity
            else:
                items[item]+=quantity
                unknown+=1
        elif category==0x10000000:
            armor[item]+=quantity
        elif category in (0x20000000,0x40000000,0x80000000):
            items[item]+=quantity
            if category==0x40000000 and base in goods:
                stock[goods[base]]+=quantity
    equipment=[]
    # Skip unknown fields, ammo and Great Rune; retain six weapon, four armor
    # and four talisman slots. Handles take precedence over the duplicate IDs.
    for slot in (*range(6),*range(12,16),*range(17,21)):
        item=handles.get(equipped_handles[slot],equipped_ids[slot])
        if item in (0,0xffffffff):
            continue
        record={"slot":slot,"id":item,"quantity":1}
        if item&0xf0000000==0:
            base=item&0x0fffffff
            weapon_name=ids.get(base-base%10000)
            if weapon_name and base%100<=db.weapons[weapon_name].maximum:
                record.update(name=weapon_name,current=base%100)
        equipment.append(record)
    return {"slot":index,"name":name,"class_name":class_name,"level":level,"runes":runes,
            "stats":stats,"stock":stock,"equipment":equipment,
            "armor":[{"id":i,"quantity":q} for i,q in sorted(armor.items())],
            "items":[{"id":i,"quantity":q} for i,q in sorted(items.items())],"weapons":[{"name":name,"current":upgrade,"quantity":quantity}
             for (name,upgrade),quantity in sorted(weapons.items())],"unknown_items":unknown}


def read_save(path,db):
    path=Path(path)
    before=path.stat()
    if not 0x300+10*STRIDE<=before.st_size<=40*1024*1024:
        raise ValueError("Unsupported save size. Select an original PC .sl2/.co2 file.")
    data=path.read_bytes()
    after=path.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
        raise ValueError("The game changed the save during reading. Retry after its save completes.")
    if data[:4]!=b"BND4":
        raise ValueError("Only plaintext PC BND4 saves are supported.")
    result=[]
    for index in range(10):
        offset=0x300+index*STRIDE
        checksum=data[offset:offset+16]
        slot=data[offset+16:offset+STRIDE]
        if not any(checksum) and not any(slot[:4]):
            continue
        if hashlib.md5(slot).digest()!=checksum:
            raise ValueError(f"Slot {index+1}: checksum mismatch or unsupported encrypted save.")
        character=read_slot(slot,db,index)
        if character:
            character.update(source=str(path.resolve()),fingerprint=hashlib.sha256(slot).hexdigest())
            result.append(character)
    if not result:
        raise ValueError("No supported active characters found.")
    return result
