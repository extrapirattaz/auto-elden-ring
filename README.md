# Auto Elden Ring

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Latest release](https://img.shields.io/github/v/release/extrapirattaz/auto-elden-ring)](https://github.com/extrapirattaz/auto-elden-ring/releases/latest)
![Platform](https://img.shields.io/badge/platform-Windows%20x64-lightgrey)
![Python](https://img.shields.io/badge/python-3.14-blue)

**An offline planner for Elden Ring.** It calculates the exact rune cost of your next
level, weapon upgrade or stone, estimates how long rune farming will take to reach a goal,
keeps a dated timeline for each character, and reads your PC save files without changing them.

🇫🇷 [Lire en français](README.fr.md) · 📖 [Full project overview](docs/PROJECT.md) · ⬇️ [Download](https://github.com/extrapirattaz/auto-elden-ring/releases/latest)

## What it does

- **Exact costs.** Level, weapon-upgrade and stone costs from the game's tables, including
  the price of the next upgrade from a shop quote.
- **Planning.** Set a target and see what is affordable and what still has to be farmed.
- **Rune farming.** Measure your own rate, save farming spots, and compare talismans and buffs.
- **Character timelines.** Checkpoints and custom events keep a dated history per character.
- **Save import.** Read a `.sl2` or `.co2` file, read-only, and refresh it at any time.
- **Companion window.** A small always-on-top window with your current objectives.

The full list of features is in [docs/PROJECT.md](docs/PROJECT.md).

## Two styles

Auto Elden Ring ships with two visual styles. Pick one in **Settings**.

### Readable — the default

Black text on white, visible borders and a single blue accent. It is built for quick reading
next to the game, with the highest contrast of the two styles.

![Readable style: character page](docs/screenshots/readable-character.png)

### Ledger — the dark travel journal

A dark style with serif headings, ruled cards and a brass accent, for a calmer look in low light.

![Ledger style: character page](docs/screenshots/ledger-character.png)

### Rune farming

The farm page measures your runes per minute and estimates the time to your goal.

![Readable style: rune farming page](docs/screenshots/readable-farm.png)

## Download and run

- **Without Python:** download `Auto-Elden-Ring-<version>-win-x64.exe` from the
  [Releases page](https://github.com/extrapirattaz/auto-elden-ring/releases). Compare it with
  the SHA-256 in `SHA256SUMS.txt` before you run it.
- **From source:** install Python 3.14 (64-bit), then run `START_AUTO_ELDEN_RING.bat`, or run
  `python main.py` after `python -m pip install -r requirements.txt`.

Requires Windows 10 or 11, 64-bit. Installing the dependencies needs internet access; using the application does not.

Six languages are available: English (default), French, Czech, German, Spanish and Japanese.
The interface also has a reading mode for dyslexic readers.

## Your data

Everything stays on your computer. Progress is saved in
`%LOCALAPPDATA%/AutoEldenRing/profiles-v3.json`; back up that file to keep your history.
The application has no network access, no telemetry and no account.

## Versions

- Each release is a tag (`v1.0.1` to `v7.0.0`) with its Windows executable and checksums.
  Release notes are in [CHANGELOG.md](CHANGELOG.md).
- `main` holds the current version (7.0.0).
- `legacy/6.x` keeps the last version with the Gothic and Windows XP styles, for anyone who
  preferred them.

## Documentation

- [Full project overview](docs/PROJECT.md) · [Présentation complète (français)](docs/PROJECT.fr.md)
- [User guide](docs/GUIDE.md) — each screen and workflow.
- [Data sources](docs/SOURCES.md) — where the cost tables, icons and names come from.
- [Changelog](CHANGELOG.md) — every version.

## Disclaimer

Auto Elden Ring is an unofficial fan tool. It is not affiliated with, endorsed by or
sponsored by FromSoftware, Bandai Namco Entertainment or any of their partners. *Elden Ring*
and all related names and game media belong to their owners.

## License

Released under the [MIT License](LICENSE). Copyright (c) 2026 extrapirattaz.
The MIT License covers the source code in this repository; game media keep their own
rights — see [docs/SOURCES.md](docs/SOURCES.md).
