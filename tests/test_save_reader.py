"""Synthetic binary fixtures exercise the real bounded reader and import flow."""
from copy import deepcopy
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
from classes_data import CLASS_DATA, ATTRIBUTES
from auto_elden_ring.core import Database
from auto_elden_ring.save_reader import read_save,SLOT_SIZE,STRIDE
from auto_elden_ring.profiles import Profiles
from auto_elden_ring.history import import_characters
from auto_elden_ring.planner import default_state


def fixture(gear=False):
    maps=struct.pack("<II",0x80000001,1000006)+bytes(13)
    maps+=struct.pack("<II",0xb0000001,0x40000000|10100)
    if gear:
        maps+=struct.pack("<II",0x90000001,0x100249f0)+bytes(8)
    maps+=bytes((0x1400-(3 if gear else 2))*8)
    player=bytearray(432)
    stats=CLASS_DATA["Warrior"]["stats"]
    struct.pack_into("<8I",player,0x34,*[stats[k] for k in ATTRIBUTES])
    struct.pack_into("<2I",player,0x60,8,12345)
    name="Fixture".encode("utf-16-le")
    player[0x94:0x94+len(name)]=name
    player[0xb7]=1
    inventory=struct.pack("<I",6 if gear else 5)+struct.pack("<3I",0x80000001,1,1)+struct.pack("<3I",0xb0000001,7,2)
    inventory+=struct.pack("<3I",0xb0000000|10200,3,3)+struct.pack("<3I",0xa0000000|1000,1,4)
    inventory+=struct.pack("<3I",0xb0000000|1800,8,5)
    if gear:
        inventory+=struct.pack("<3I",0x90000001,2,6)
    inventory+=bytes((0xa80-(6 if gear else 5))*12)
    keys=struct.pack("<I",1)+struct.pack("<3I",0xb0000000|8951,1,7)+bytes((0x180-1)*12) if gear else bytes(4+0x180*12)
    after_inventory=keys+bytes(8+116+140+24)+struct.pack("<I",0)+bytes(156+12+303)
    after_inventory+=struct.pack("<I",1)+struct.pack("<3I",0xb0000000|10101,12,6)+bytes((0x780-1)*12)
    equipment=bytearray(88)
    if gear:
        struct.pack_into("<I",equipment,1*4,1000006)
        struct.pack_into("<I",equipment,12*4,0x100249f0)
    prefix=struct.pack("<I",210)+bytes(28)+maps+player+bytes(13*16+88+28)+equipment+bytes(88)+inventory+after_inventory
    slot=prefix+bytes(SLOT_SIZE-len(prefix))
    empty=bytes(SLOT_SIZE)
    return b"BND4"+bytes(0x300-4)+hashlib.md5(slot).digest()+slot+(hashlib.md5(empty).digest()+empty)*9


class SaveImport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=Database()
        cls.binary=fixture()

    def test_read_stats_class_runes_upgrades_and_stones_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"ER0000.sl2"
            path.write_bytes(self.binary)
            before=hashlib.sha256(path.read_bytes()).digest()
            result=read_save(path,self.db)
            self.assertEqual(len(result),1)
            char=result[0]
            self.assertEqual((char["name"],char["class_name"],char["level"],char["runes"]),("Fixture","Warrior",8,12345))
            self.assertEqual(char["stock"]["normal:1"],7)
            self.assertEqual(char["stock"]["normal:2"],12)
            self.assertEqual(char["stock"]["somber:9"],3)
            self.assertEqual(char["unknown_items"],0)
            self.assertEqual(char["weapons"],[{"name":"Dagger","current":6,"quantity":1}])
            self.assertEqual(hashlib.sha256(path.read_bytes()).digest(),before)

    def test_armor_key_items_equipment_and_snapshot_counts(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"ER0000.sl2"
            path.write_bytes(fixture(gear=True))
            digest=hashlib.sha256(path.read_bytes()).digest()
            char=read_save(path,self.db)[0]
            self.assertEqual(char["armor"],[{"id":0x100249f0,"quantity":2}])
            self.assertIn({"id":0x40000000|8951,"quantity":1},char["items"])
            self.assertEqual(char["equipment"][0]["name"],"Dagger")
            self.assertEqual(char["equipment"][0]["current"],6)
            self.assertEqual(char["equipment"][1]["id"],0x100249f0)
            profiles=Profiles(self.db)
            ident=import_characters(profiles,[char],default_state())[0]
            state=profiles.select(ident)
            self.assertEqual(state["inventory_armor"],char["armor"])
            self.assertEqual(state["equipment"],char["equipment"])
            self.assertEqual(profiles.active["checkpoints"][0]["state"]["inventory_items"],char["items"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).digest(),digest)

    def test_corrupt_checksum_and_truncation_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"ER0000.sl2"
            damaged=bytearray(self.binary)
            damaged[0x390]^=1
            path.write_bytes(damaged)
            with self.assertRaisesRegex(ValueError,"checksum"):
                read_save(path,self.db)
            path.write_bytes(b"BND4")
            with self.assertRaisesRegex(ValueError,"size"):
                read_save(path,self.db)

    def test_import_deduplicates_and_preserves_target(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"ER0000.sl2"
            path.write_bytes(self.binary)
            chars=read_save(path,self.db)
            profiles=Profiles(self.db)
            ids=import_characters(profiles,chars,default_state())
            state=profiles.select(ids[0])
            self.assertEqual(state["journey_name"],state["character_name"])
            self.assertEqual(len(profiles.active["checkpoints"]),1)
            state["stats_target"]["vigor"]=60
            state["runes"]=100
            profiles.sync(state)
            import_characters(profiles,chars,state)
            self.assertEqual(len(profiles.active["checkpoints"]),1)
            self.assertEqual(profiles.active["state"]["runes"],12345)
            newer=deepcopy(chars)
            newer[0].update(runes=15000,fingerprint="changed")
            import_characters(profiles,newer,state)
            self.assertEqual(len(profiles.active["checkpoints"]),2)
            self.assertEqual(profiles.active["state"]["stats_target"]["vigor"],60)
            self.assertTrue(profiles.active["checkpoints"][-1]["changes"])

    def test_failed_batch_import_is_atomic(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"ER0000.sl2"
            path.write_bytes(self.binary)
            chars=read_save(path,self.db)
            bad=deepcopy(chars[0])
            bad.update(slot=1,name="Invalid fixture")
            bad["stats"]["vigor"]=100
            profiles=Profiles(self.db)
            original=deepcopy(profiles.data)
            with self.assertRaises(ValueError):
                import_characters(profiles,chars+[bad],default_state())
            self.assertEqual(profiles.data,original)
