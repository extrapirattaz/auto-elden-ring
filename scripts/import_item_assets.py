"""Import pinned non-weapon item metadata and small offline icons."""
from concurrent.futures import ThreadPoolExecutor
import hashlib,io,json,re,urllib.request
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Auto-Elden-Ring'}),timeout=30) as r:
        return r.read()

def main():
    pinned=json.loads((ROOT/'assets/catalogue_manifest.json').read_text())['repositories']
    repo='oisis/EldenRing-SaveForge'; commit=pinned[repo]
    base=f'https://raw.githubusercontent.com/{repo}/{commit}/'
    catalog={}; sources=[]
    files=('head','chest','arms','legs','talismans','tools','key_items','bolstering_materials','crafting_materials','ashes','ashes_of_war','sorceries','incantations','cookbooks','whetblades','info','arrows_and_bolts')
    for name in files:
        url=base+'backend/db/data/'+name+'.go'
        raw=fetch(url);sources.append({'url':url,'sha256':hashlib.sha256(raw).hexdigest()})
        for ident,label,icon in re.findall(r'0x([0-9A-Fa-f]+):\s*\{Name:\s*"([^"]+)"[^\n]*?IconPath:\s*"([^"]+)"',raw.decode()):
            number=int(ident,16)
            if number>>28 in (1,2,4):
                catalog[str(number)]={'name':label,'category':'armor' if number>>28==1 else 'items','icon':f'assets/items/{number}.webp','names':{'en':label},'source_icon':base+'frontend/public/'+icon}
    # Official base-game strings provide exact IDs for all five official locales.
    for lang,folder in (('en','engus'),('fr','frafr'),('de','deude'),('es','spaes'),('ja','jpnjp')):
        url=f'https://raw.githubusercontent.com/elden-ring-data/msg/{pinned["elden-ring-data/msg"]}/{folder}/item.msgbnd.dcx.json'
        raw=fetch(url); tables=json.loads(raw); sources.append({'url':url,'sha256':hashlib.sha256(raw).hexdigest()})
        for ident,item in catalog.items():
            typ={1:'ProtectorName.fmg',2:'AccessoryName.fmg',4:'GoodsName.fmg'}[int(ident)>>28]
            table=next((t for k,t in tables.items() if k.endswith(typ)),{})
            localized=table.get(str(int(ident)&0x0fffffff))
            if localized:
                item['names'][lang]=localized
    dest=ROOT/'assets/items';dest.mkdir(exist_ok=True)
    def icon(pair):
        ident,item=pair; path=ROOT/item['icon']
        try:
            raw=fetch(item['source_icon'])
            with Image.open(io.BytesIO(raw)) as source:
                image=source.convert('RGBA');image.thumbnail((96,96),Image.Resampling.LANCZOS)
                output=io.BytesIO();image.save(output,'WEBP',quality=80,method=6)
                encoded=output.getvalue();digest=hashlib.sha256(encoded).hexdigest()
                path=dest/(digest[:32]+'.webp');item['icon']='assets/items/'+path.name
                if not path.exists():
                    path.write_bytes(encoded)
            item.update(source_sha256=hashlib.sha256(raw).hexdigest(),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        except Exception as error:
            item['icon']=''; item['icon_error']=str(error)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(icon,catalog.items()))
    (ROOT/'assets/item_catalogue.json').write_text(json.dumps({'repository':repo,'commit':commit,'sources':sources,'items':catalog},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Items:',len(catalog),'icons:',sum(bool(i['icon']) for i in catalog.values()))

if __name__=='__main__':
    main()
