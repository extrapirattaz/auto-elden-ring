# Auto Elden Ring — project overview (version 7.0.0)

Auto Elden Ring is an offline Windows planner for Elden Ring. It calculates what a
character needs next (attributes, levels, weapon upgrades, smithing stones) and how
long rune farming will take, keeps a dated timeline for each character, and imports
progress from your PC save files without ever modifying them.

The application never connects to the internet, has no account, collects no data and
stores everything on your computer.

## Who it is for

- Players who want to know the exact rune cost of their next level or weapon upgrade
  before spending anything.
- Players who farm runes and want a measured rate and a time estimate for a goal.
- Players who want a dated history of their characters, from checkpoints to imported saves.

It is a planner and a notebook. It does not play the game, read live game memory,
change save files or synchronize between computers.

## Requirements

- Windows 10 or 11, 64-bit.
- To run the executable: nothing else.
- To run from source: Python 3.14 (64-bit) and the packages in `requirements.txt`.
  Installing them needs internet access; using the application does not.

## Installation and first launch

1. Download `Auto-Elden-Ring-7.0.0-win-x64.exe` from the GitHub release page and check
   its SHA-256 against `SHA256SUMS.txt`.
2. Run it. The window opens maximized on the character chooser.
3. Create a character with its in-game name and original starting class, or import a
   save file. A fresh installation contains no demo profile and no sample event.

From source, run `START_AUTO_ELDEN_RING.bat`, or run `python main.py` after installing
`requirements.txt`.

## Languages

English (default), French, Czech, German, Spanish and Japanese. The language is chosen
in Settings and changes the whole interface immediately, without closing the window.
Weapon and item names are provided in all six languages. Translations other than the
English text have not been reviewed by native speakers; see `docs/SOURCES.md`.

## Visual styles

Version 7.0.0 has two styles. Each has one fixed palette. Both use solid colours and no
decorative background.

| Style | Look | Typography | Palette |
| --- | --- | --- | --- |
| **Readable** (default) | Black text on white, visible borders, blue accent | Segoe UI | background `#F5F6F8`, cards `#FFFFFF`, text `#0F1419`, accent `#1E40AF` |
| **Ledger** | Dark travel journal, ruled cards, quiet selectors, brass accent | Constantia headings, Bahnschrift interface | background `#121210`, cards `#1B1A17`, text `#E8DCC0`, accent `#B08D4E` |

Both styles keep text and borders at or above WCAG AA contrast. Measured contrast:
Readable text on cards 18.5 : 1, secondary text 7.6 : 1, button text on accent 8.7 : 1;
Ledger text on cards 12.8 : 1, secondary text 5.8 : 1, button text on accent 6.0 : 1.

**Reading mode** (Settings) is independent of the style. It switches to the bundled
OpenDyslexic font, enlarges the text and uses a quiet cream palette. Turning it off
restores the chosen style.

Earlier versions had more styles (Gothic and Windows XP) and several palettes. They were
removed in 7.0.0; saved preferences migrated to one of the two current styles, and the
earlier versions remain available as tags and on the `legacy/6.x` branch.

## Characters and the journal

The **journal** lists your characters. Each character has its own timeline.

- **Create a character** with its in-game name and starting class. The name is also the
  journey name, and the starting class cannot be changed afterwards.
- **Checkpoints** are dated snapshots of the character's current state: attributes,
  runes held, weapons, stones and farming settings. A checkpoint is a fixed record;
  later edits never change it.
- **Custom events** record a dated state you enter yourself: permanent attributes and
  the weapons acquired or upgraded. The level is derived from the attributes.
- **Timeline pages** show at most 100 events at a time; older and newer pages are one click away.
- **View checkpoint** opens the recorded level, runes, attributes, equipment, weapons,
  stones and the changes since the previous event.
- The library holds up to **100 characters** and each character's timeline is saved
  automatically.

## Importing and refreshing game saves

- **Import game save** reads a PC save file (`.sl2` or `.co2`). The reader is read-only,
  checks the file size, the modification time and every slot checksum before accepting
  any data, and never writes to the save.
- You choose the installation folder once (the save is found in the roaming folder), or
  select the file directly. Up to **20 save files** can be remembered.
- Imported data includes the character name, starting class, attributes, level, runes,
  catalogue weapons and their upgrades, armour, talismans, goods, key items and ordinary
  stones.
- **Rescan game saves** (on startup or at any time) reads the latest disk save in a
  background worker. The current window and your goals are kept. Only meaningful changes
  create timeline events, so repeated scans do not duplicate history. An autosave that is
  still being written is retried briefly; on failure the previous snapshot stays available.
- The reader uses saved progress. Progress that the game has not yet written to disk is
  not visible to the application.

## Character calculator

- Enter current and target permanent attributes. Both levels update automatically.
- The calculator shows the exact rune cost of the levels between current and target,
  the cost already paid since the starting class level, the cost to reach level 713
  (all attributes at 99), and how many levels the held runes can buy.
- Level costs come from the supplied integer cost tables in `elden_ring_costs.json`
  (regulation 1.17.1: 712 level transitions).

## Weapon upgrades

- **By upgrade price:** enter the blacksmith cost of the first upgrade (+0 → +1), or
  paste the price of the next upgrade and let the application invert it to the base
  price. Standard, somber and special forge fees follow the formulas documented in
  `docs/SOURCES.md`.
- **Choose weapons:** pick weapons from the illustrated catalogue (487 entries across 42
  categories). The catalogue is virtualized and keeps a bounded image cache, so opening
  it stays responsive. Each selected weapon keeps its own current upgrade, target
  upgrade and copy count.
- **Maximum without ancient dragon stones:** plans every upgrade reachable with ordinary
  stones only, and reports what remains to farm.
- Imported owned upgrades initialize the selected weapons.

## Smithing stones

- Record the stock you hold, or check off purchases from the shop. Held runes only
  decide the farming deficit; they never block a purchase record.
- Normal stone prices are 200 to 3600 runes per tier; somber stone prices are 2000 to
  25000. Ancient dragon stones have no invented purchase price or stock count.

## Completing upgrades

Confirming completed upgrades in-game does three things: weapon levels move to their
targets, ordinary stones and held runes reset to zero, and a journal event is recorded
for a created character. You can then enter any actual surplus again.

## Rune farming

- **One-minute measurement:** start the timer, perform the route in-game, then enter the
  runes gained.
- **Full test:** separate 60-second, 60-second and 180-second trials. Each sample is
  weighted by its duration to produce a measured rate.
- **Buffs:** choose the talisman and consumable used during the test to compare their
  effect. Silver discovery buffs contribute 0% to rune gains in the model.
- **Farming spots:** save a named spot with its measured rate and reuse it from the
  character and weapon planners to estimate the time to a goal.
- Projections depend on route, downtime, rounding and buff uptime. They are estimates,
  not guarantees.

## Equipment view

For a character or checkpoint, the equipment view separates the six weapon slots, the
four armour slots and the four talisman slots from all acquired weapons. Inventory and
storage counts are combined. Item names and small icons are bundled offline. Unresolved
item identifiers stay visible, and some recent item names fall back to English.

## Small companion window

An always-on-top, borderless window showing the character's current objectives: levels,
upgrades and farming, with an editable rune count. It can be dragged and snaps to the
screen edges within 28 pixels. Inactive full-size pages are released while it is open;
return to the full application at any time.

## Settings

- Visual style (Readable or Ledger), language, reading mode.
- Background music from a local MP3, WAV, FLAC or OGG file, with play, pause and stop.
  The file stays on your computer; closing the application stops playback.
- Opening the small companion and importing a save file.

## Data storage and privacy

- Profiles and timelines are saved atomically to
  `%LOCALAPPDATA%/AutoEldenRing/profiles-v3.json`. Back up this file to keep your full history.
- Earlier save formats are migrated automatically without losing characters, goals,
  inventory or timelines.
- `python scripts/reset_local_data.py --confirm` removes only the application's own
  state. It never deletes game saves, music or custom images.
- Save files are read, never copied into the application's data or into releases.
- There is no network code, no telemetry and no account.

## Quality and verification

- **94 unit tests** cover the cost tables and their boundaries, the planner, the save
  reader and sync, profile migrations, and widget workflows in the real window. Native
  menu tests need an interactive Windows desktop.
- **Packaged checks** run inside each built executable: self-check of the data, GUI smoke
  test across all languages and styles, audio decoder, save-reader fixture, and startup
  rescan.
- Formatting is checked with Black at 100 columns.

## Build and release

`BUILD_RELEASE.ps1` runs on Windows x64 with Python 3.14. It runs the tests, builds the
single-file executable with PyInstaller, runs the packaged checks, and writes a
version-matched source archive, Windows archive, executable and checksums into a sibling
`Release/<version>` folder. Existing releases are never overwritten, and the version in
`auto_elden_ring/__init__.py` names every artifact.

## Known limits

- Windows only. The interface is built on Tkinter with CustomTkinter widgets.
- Reading mode may clip some short button labels, because button widths are fixed.
- Plural forms in some translations are generic (for example "level(s)"); editorial
  translations have not been reviewed by native speakers.
- Game data is the supplied table; individual entries have not been checked in-game.
- Farming projections are estimates.
- The application does not read live game memory or unsaved progress.
- The planner assumes the relevant bell bearings are available.

## Legal notice

Auto Elden Ring is an unofficial fan tool. It is not affiliated with, endorsed by or
sponsored by FromSoftware, Bandai Namco Entertainment or any of their partners.
*Elden Ring*, its names and its game media belong to their owners. The source code is
released under the MIT License; that licence does not extend to game media. Icon and
name provenance is recorded in [SOURCES.md](SOURCES.md).

## Project layout

| Path | Responsibility |
| --- | --- |
| `main.py` | Entry point and packaged verification commands |
| `auto_elden_ring/core.py` | Exact level and weapon costs, inverse costs, stone requirements |
| `auto_elden_ring/planner.py` | Character, weapon, budget, stock and farming state |
| `auto_elden_ring/ui.py`, `presentation.py`, `journey_ui.py` | Windows, pages, timelines and the small companion |
| `auto_elden_ring/styles.py` | The two styles, their palettes and contrast helpers |
| `auto_elden_ring/save_reader.py`, `save_sync.py`, `history.py` | Read-only save parsing, rescans and history import |
| `auto_elden_ring/profiles.py`, `storage.py` | Atomic persistence, migrations and snapshots |
| `auto_elden_ring/i18n.py`, `style_text.py`, `journey_text.py` | Six-language interface text |
| `classes_data.py`, `elden_ring_costs.json` | Starting classes and the supplied cost table |
| `assets/` | Icons, fonts, translations, provenance and licences |
| `tests/` | Calculation boundaries, save fixtures and widget workflows |
| `scripts/` | Release builder and the explicit local-data reset |
| `docs/` | User guide, architecture, verification and data sources |

## Further reading

- [User guide](GUIDE.md) — every screen and workflow.
- [Architecture](ARCHITECTURE.md) — how the code is organized and maintained.
- [Verification](VERIFICATION.md) — what was tested and how.
- [Data sources](SOURCES.md) — provenance of the cost table, icons and names.
- [Changelog](../CHANGELOG.md) — every version.
