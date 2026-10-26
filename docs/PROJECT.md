# Auto Elden Ring — full project overview

🇫🇷 [Lire en français](PROJECT.fr.md)

Auto Elden Ring is an offline planner for Windows, made for Elden Ring players. It tells
you what your character needs next — attributes, levels, weapon upgrades, smithing
stones — and how long rune farming will take to reach a goal. It keeps a dated timeline
for every character and can read your PC save files without changing them.

It works entirely on your computer: no account, no internet connection, no telemetry.

## What it is for

- **Knowing the exact cost before you spend.** The rune price of a level, a weapon
  upgrade or a stone is calculated from the game's cost tables.
- **Planning your next steps.** Choose a target level, a weapon upgrade or a stone stock,
  and see what is affordable and what still has to be farmed.
- **Estimating rune farming.** Measure your own rune rate and get a time estimate to a goal.
- **Keeping a history.** Checkpoints and custom events record a character's progress over time.
- **Importing progress.** Read a PC save file to fill in a character, read-only.

It is a planner and a notebook. It does not play for you, read live game memory, edit
saves, or synchronize between computers.

## Who it is for

Elden Ring players who want to plan builds, weapon upgrades and rune farming, and who
prefer a local, offline tool that they can open next to the game.

## Main features

### Characters and timelines (the journal)

- Create a character with its in-game name and original starting class.
- Keep a timeline per character: **checkpoints** (dated snapshots of the current state)
  and **custom events** (a dated state you enter, with attributes and weapons).
- Browse long histories in pages of up to 100 events.
- Open any checkpoint to see its level, runes, attributes, equipment, weapons, stones and
  the changes since the previous event. A recorded checkpoint never changes afterwards.
- Hold up to 100 characters in the library.

### Importing and refreshing save files

- Import a PC save file (`.sl2` or `.co2`). The reader is read-only: it checks file size,
  modification time and every slot checksum before accepting any data.
- Remember the installation folder or the save file, and remember up to 20 save files.
- Imported data includes the name, starting class, attributes, level, runes held, catalogue
  weapons and their upgrades, armour, talismans, goods, key items and ordinary stones.
- **Rescan game saves** reads the latest saved progress in the background, while keeping
  the window and your goals. Only meaningful changes create timeline events, so repeated
  scans do not duplicate history.
- The application sees progress that the game has written to disk. Unsaved in-game
  progress is not visible.

### Character calculator

- Enter current and target permanent attributes; both levels update automatically.
- See the exact rune cost of the levels between current and target, the amount already
  spent since the starting class level, the cost to reach the maximum level (713), and how
  many levels your held runes can buy.
- Costs come from the supplied integer tables (regulation 1.17.1, 712 level transitions).

### Weapon upgrades

- **By upgrade price:** enter the blacksmith cost of the first upgrade, or paste the price
  of the next upgrade and let the application work back to the base price. Standard,
  somber and special forge fees follow the formulas documented in
  [SOURCES.md](SOURCES.md).
- **Choose weapons:** pick weapons from an illustrated catalogue of 487 entries across 42
  categories, search it, and set each weapon's current upgrade, target upgrade and copy count.
- **Maximum without ancient dragon stones:** plan every upgrade that ordinary stones can reach.
- Owned upgrades from an imported save initialize the selected weapons.

### Smithing stones

- Record your stone stock, or check off purchases.
- Held runes are used only to estimate the farming deficit; they never block a purchase.
- Ancient dragon stones have no invented price or stock count.

### Completing upgrades

Confirm completed upgrades in-game and the application moves the weapons to their targets,
resets ordinary stones and held runes to zero, and records a journal event. Any actual
surplus can be entered again straight away.

### Rune farming

- **One-minute measurement:** start the timer, farm, then enter the runes gained.
- **Full test:** three separate trials (60 s, 60 s and 180 s), each weighted by its duration.
- **Buffs:** compare talismans and consumables used during the test. Silver discovery buffs
  contribute 0 % to rune gains in the model.
- **Farming spots:** save a named spot with its measured rate and reuse it to estimate the
  time to a goal from the character and weapon pages.
- Projections depend on route, downtime, rounding and buff uptime; they are estimates.

### Equipment view

For a character or a checkpoint, the equipment view shows the six weapon slots, the four
armour slots and the four talisman slots, separately from every acquired weapon. Inventory
and storage counts are combined. Item names and small icons are bundled, so the view works offline.

### Small companion window

A compact, always-on-top, borderless window with your current objectives: levels, upgrades
and farming, plus an editable rune count. Drag it anywhere; it snaps to the screen edges.
Return to the full window at any time.

### Interface and accessibility

- Two visual styles, each with one fixed palette (see below).
- Six languages: English (default), French, Czech, German, Spanish and Japanese, switched
  instantly in Settings.
- **Reading mode** for dyslexic readers: the bundled OpenDyslexic font, larger text and a
  cream palette. Turning it off restores your style.
- Native Windows menus and dialogs, keyboard navigation included.
- Local background music (MP3, WAV, FLAC or OGG) from a file you choose, with play, pause and stop.

## Visual styles

| Style | Look | Typography | Colours |
| --- | --- | --- | --- |
| **Readable** (default) | Black text on white, visible borders, blue accent | Segoe UI | Background `#F5F6F8`, cards `#FFFFFF`, text `#0F1419`, accent `#1E40AF` |
| **Ledger** | Dark travel journal, ruled cards, brass accent | Constantia headings, Bahnschrift interface | Background `#121210`, cards `#1B1A17`, text `#E8DCC0`, accent `#B08D4E` |

Both styles keep text and borders at or above WCAG AA contrast. Measured: Readable text on
cards 18.5 : 1, Ledger text on cards 12.8 : 1, button text on the accent 8.7 : 1 and 6.0 : 1.

Earlier versions also had Gothic and Windows XP styles and several palettes. They were
retired in version 7.0.0. Saved preferences moved to one of the two current styles, and
the earlier versions remain available as tags and on the `legacy/6.x` branch.

## Your data and privacy

- Everything is saved on your computer, in `%LOCALAPPDATA%/AutoEldenRing/profiles-v3.json`.
  Back up this file to keep your complete history.
- Saves are written atomically, so a crash cannot leave a half-written library.
- Save files are only read, never copied into the application's data or into releases.
- Older saved formats are upgraded automatically; characters, goals, inventory and
  timelines are kept.
- There is no network code, no telemetry and no account.

## Requirements

- Windows 10 or 11, 64-bit. The executable needs nothing else.
- To run from source: Python 3.14 (64-bit) and the packages in `requirements.txt`.

## Limits

- Windows only.
- Reading mode can clip a few short button labels, because button widths are fixed.
- Some translations use generic plural forms, such as "level(s)"; the non-English
  translations have not been reviewed by native speakers.
- The cost tables are the supplied data; individual entries have not been checked in-game.
- Farming projections are estimates, not guarantees.
- The application does not read live game memory or progress that the game has not saved.

## Legal notice

Auto Elden Ring is an unofficial fan tool. It is not affiliated with, endorsed by or
sponsored by FromSoftware, Bandai Namco Entertainment or any of their partners.
*Elden Ring*, its names and its game media belong to their owners. The source code is
released under the [MIT License](../LICENSE); that licence does not cover game media. Icon
and name provenance is documented in [SOURCES.md](SOURCES.md).

## Documentation

- [User guide](GUIDE.md) — each screen and workflow, in English.
- [Data sources](SOURCES.md) — origin of the cost table, icons and names.
- [Changelog](../CHANGELOG.md) — every version.
- [Releases](https://github.com/extrapirattaz/auto-elden-ring/releases) — downloads and checksums.
