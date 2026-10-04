# Data provenance and assumptions

## Supplied database

elden_ring_costs.json is unchanged. Its SHA-256 is
3118f1c03fffaf832fdb453d6697d5da8b03007357333f2a2bec52f9b1e3a123.
It declares regulation 1.17.1, 487 weapon entries and 712 level transitions.
Tests verify structure, totals, every upgrade passage and exceptional tariffs.
Every entry has not been independently verified in-game.

Starting attributes are recorded in classes_data.py. Permanent attribute sum
minus 79 yields level, with maximum 713 at all attributes 99.

Standard normal forge fees multiply base cost by (5 + current upgrade) / 5.
Somber fees use (2 + current upgrade) / 2 until +9, then 6 × base for +10.
Rational arithmetic and ties-to-even rounding follow the supplied helper model.
Known catalogue weapons use exact tables instead of assuming this profile.

Normal stone prices are 200, 400, 600, 900, 1200, 1500, 2400 and 3600.
Somber prices are 2000, 3000, 4000, 6000, 9000, 12000, 16000, 20000 and 25000.
Normal tiers require 2/4/6 stones; somber steps each require one. The final step
requires an ancient dragon stone with no ordinary purchase price.

## Catalogue media and localized names

- Icons: [EldenRing-SaveForge](https://github.com/oisis/EldenRing-SaveForge),
  matched by parameter ID. All 487 are bundled as resized PNGs.
- Base-game names: [extracted game messages](https://github.com/elden-ring-data/msg).
- English/Japanese DLC names:
  [Impalers Archive](https://github.com/ividyon/Impalers-Archive).

assets/catalogue_manifest.json records pinned commits, source URLs and icon
hashes. The import supplied 377 base names per imported locale and 479
English/Japanese names after DLC imports. complete_weapon_names.py supplements
missing names and supplies editorial Czech translations.

French/German/Spanish supplemental names and missing Japanese strings are
editorial, not independently verified official terminology. Czech is editorial,
not an official game localization. All six tables contain 487 names. Proper
names may remain identical. Saved projects use stable English identifiers.

Game icons and original localized strings belong to their respective rights
holders. Public repository availability does not establish a standalone
redistribution license. Provenance records are not ownership or permission claims.

## Farming projections

The model uses 1.20 for Gold Scarab, 1.30 for gold-pickled fowl foot and 1.40
for golden horn tender. Talisman × one consumable gives 1.56 or 1.68.
Silver discovery buffs use 1.00 for runes. Dividing a total cannot precisely
undo individual-enemy rounding.

The scarab/horn +68% combination is also described in
[this gameplay guide](https://gameranx.com/features/id/503563/article/shadow-of-the-erdtree-6-steps-to-farm-100000-runes-per-minute/).
Future earnings depend on route, rewards, buffs and downtime. Measurements
are weighted by duration, not averaged equally.

## Software

Python/Tk, [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter),
[Pillow](https://python-pillow.org/) and [PyInstaller](https://pyinstaller.org/)
provide the desktop and packaged runtime. Versions are pinned in the two
requirements files.


## Version-3 presentation assets

Catalogue PNGs were resized to at most 136px and encoded as WebP quality 84.
The manifest retains source URLs, source SHA-256 hashes and processed hashes.
The Elden-style landscape is original AI-generated fantasy artwork, created
for this project through the imagegen skill; it is not an official game screenshot
or logo. Runtime file: assets/elden-landscape.webp.

[OpenDyslexic](https://github.com/antijingoist/opendyslexic) Regular and Bold
are bundled from commit 1824da5c0e41dc3e13ffc7f3a636dcaf695d61b7.
The SIL Open Font License is included in assets/fonts/OFL.txt. Fonts are loaded
privately for this process, without installing a system font. The reading mode
offers a preference; no medical effectiveness claim is made.


## Version-4 read-only save reader

The bounded PC prefix reader in save_reader.py is implemented locally, without
shipping or invoking a save editor. It has no write-back, repair, process-memory
or game-input API. Binary layout research used these primary projects:

- [Hapfel's Elden Ring Save Parser](https://github.com/Hapfel1/elden-ring-save-parser-lib),
  commit dcb01ed74d7cbad83ed1e756fb2cdef2dd73780b. MIT attribution is included at
  assets/licenses/save-parser-MIT.txt. The complete parser is not bundled.
- [SaveForge header specification](https://github.com/oisis/EldenRing-SaveForge/blob/main/spec/01-header.md),
  [GA item records](https://github.com/oisis/EldenRing-SaveForge/blob/main/spec/03-gaitem-map.md),
  [player data](https://github.com/oisis/EldenRing-SaveForge/blob/main/spec/04-player-game-data.md),
  [inventory](https://github.com/oisis/EldenRing-SaveForge/blob/main/spec/07-inventory.md)
  and [storage](https://github.com/oisis/EldenRing-SaveForge/blob/main/spec/10-storage.md).
  Consulted on 2026-10-03. These are references, not bundled editor components.
- [Ariescyn item ID reference](https://github.com/Ariescyn/EldenRing-Save-Manager/blob/main/ALL_ITEM_IDS.md)
  for ordinary stone goods IDs. Weapon IDs resolve against the supplied catalogue.

The reader checks BND4, bounded file/sections, ten slot MD5 checksums, class
minimums and level = attribute sum - 79. It reads variable weapon/armor instance
records, permanent player data and both held/storage common inventories.
Goods can resolve directly from their handle when no instance map entry exists.
Affinity variants use the same catalogue base weapon while retaining upgrades;
affinity and Ash of War are not tracked by this planner.
The local real-save check covered slot versions 210 and 250. Console/encrypted
formats and modified/new layouts have no support guarantee.
