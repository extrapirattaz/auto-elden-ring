# User guide â€” 4.0.1

## Start with a character

Open Journal, then New character. Enter the character's in-game name and original
starting class. There is one name for both the character and its journey.
The starting class cannot be changed later. No sample character or timeline
event is added automatically. Click a character card to open its timeline.
Manual calculators also work before creating a profile.

Add event offers two paths:

- Save current progress snapshots the selected character's current calculator
  state, settings, stock, goals and weapons.
- Custom event lets you enter permanent attributes and record acquired or
  upgraded weapons with their upgrade/copy counts. It derives the level from
  the attributes and leaves the current calculator state unchanged.

Dates default to the computer's current local time. An optional custom date
uses DD/MM/YYYY HH:MM. Events are sorted by date; click View checkpoint for
attributes, owned weapons, planning targets and changes. Later edits cannot
alter an older snapshot. Show older/newer events pages through histories in groups of at most 100 events.

## Import and refresh a game save

Use Import game save in Journal or Settings. The installed executable and the
save are stored separately: typical PC saves are in
%APPDATA%/EldenRing/account-folder/ER0000.sl2. Selecting the installation folder
checks for saves there, then the roaming directory. If several exist, select
the intended .sl2/.co2 file explicitly.

The app reads the latest saved state in a background worker. It never modifies
the game file, attaches to a game process, repairs a checksum or injects input.
Plaintext PC BND4 saves must pass slot MD5 checks, section bounds and
class/attribute/level checks. Unsupported, damaged or changing files produce an
error rather than a guessed character.

Each non-empty supported slot becomes a profile with one initial event.
Names, original classes, permanent stats, levels, held runes, owned catalogue
weapons/upgrades and ordinary smithing stones are imported. Weapons and stones
include inventory and storage; withdraw stored items when needed in the game.
Ancient dragon stones retain question marks in the ordinary purchase planner.
Armor, talismans, ammunition, consumables and other items are not a complete item
encyclopedia here. Entries the weapon catalogue cannot resolve are counted.

Choose the intended character card. Refresh from save keeps that selected slot,
updates current values, preserves higher goals and named farm spots, and adds a
change event only when the saved slot changed. No live polling runs while playing.
You can edit held runes manually, or refresh from the saved file.
Renaming/reusing a slot with the same class cannot reliably identify a new journey;
the reader matches the save path, slot and class. A replaced class creates a new
profile and preserves the old one.

## Character levels

Enter permanent attributes without equipment or temporary bonuses. Original
class stats set minimum values, with a maximum of 99. Level equals the attribute
sum minus 79. Current and target levels update from valid input.
Calculate levels records held runes and shows remaining cost, spending since the
starting class level, cost to 713, affordable levels and leftover runes.
Lower target attributes show a rebirth notice; redistribution is not charged as
new level growth. Choose a saved farm spot for an approximate farming duration.

## Weapons

Manual mode asks for normal/somber, blacksmith price for +0 to +1, current upgrade,
target and copies. Defaults are +24 normal and +10 somber.
Use next-upgrade price replaces the base price with the quote for the current
upgrade's next step, such as +9 to +10. The standard formula is inverted first.
Catalogue tariffs take priority for known exceptions.

Choose weapons opens illustrated cards grouped by category. Click to select,
click again to deselect. Search accepts localized or English names.
Owned imported weapons start at their lowest owned upgrade. Choose each selected
weapon in the editor to set its current upgrade, target and copies independently.
Maximum without dragon stones sets +24 normal/+9 somber without reducing a
higher existing upgrade. Totals separate forge fees and missing-stone purchases.
The affordable result raises a shared target using stock and budget; it does
not optimize which weapon should receive priority.

## Materials and acknowledgements

Enter owned counts in the stone calculator or choose I have none.
Stock is shared across planned weapons, so a stone is not allocated twice.
Missing stones lists amounts and purchase costs. Mark Purchased after buying
the indicated batch in game. Stock increases, and the row remains visibly checked.
Held runes never block or charge a purchase acknowledgement.

After visiting the blacksmith, confirm Upgrades completed. Current upgrades
become their targets, other owned copies are preserved, and ALL recorded ordinary
stones, held runes and purchase checks reset to zero. This includes surplus stock;
enter actual leftovers again. A created character receives an automatic event.
An unnamed manual weapon remains recorded as its manual upgrade state; the app
cannot invent a catalogue identity from a price alone.

Ancient stones have no unit price or ordinary stock requirement. Rune totals
include the blacksmith's final fee but exclude a fictitious dragon-stone purchase.
Double-click an ordinary unit price to override it after confirmation.

## Farm measurements and spots

Record rune gain only, excluding an existing balance. Start one minute runs
60 seconds; Reset restores 60 seconds. A stopped test uses elapsed duration.
Full test runs separately started 60, 60 and 180-second trials. After each trial
enter gain/notes, record it, then start the next. Rates are weighted by duration.
Each sample retains buffs selected at timer start.

Gold Scarab is +20%, gold-pickled fowl foot +30%, golden horn tender +40%.
Scarab multiplies one consumable; foot and horn are mutually exclusive.
Silver discovery buffs add 0% runes. Comparisons normalize each sample using
its own multiplier. Per-enemy rounding and buff uptime affect actual results.

Save this farming spot names the current measurement/sample set for this
character. Selecting a spot restores its rates and buffs. The farm page supports
character, weapons, combined, level 713 or free objectives; a free amount appears
only for a free objective. Held runes are deducted once. Efficiency adjusts time.
For the level-713 objective, enter your current level (prefilled from the
character). Its goal duration appears once. Two additional cards show runes
already invested since the starting class and the equivalent time at the chosen
farm rate and efficiency. This is an estimate using today's method, not a record
of past play time. Held runes do not reduce the invested amount. Entering a farm
level does not change character attributes; older saved measurements use the
character level until a level is entered.
Character and weapon pages can also select saved spots for their own goals.

## Appearance, music and small mode

Modern uses rounded panels. Elden Ring uses a full fantasy landscape background,
serif text and dark palettes. Windows XP uses square controls, blue accents and
grey surfaces with one palette. RGB animates colors smoothly; it has no strobe.
Reading mode applies larger OpenDyslexic text and a calm cream palette, then
restores the selected style when disabled. Changes retain existing page widgets
and batch presentation updates without reopening the main window.

Choose a local MP3/WAV to play, restart, pause or stop music. Closing the app
closes its playback device. Files stay local; playback does not start automatically.

Small companion is always on top and provides character/weapon/farm views and
editable held runes. It hides the main window, closes extra popups and releases
inactive cached pages. A running timer on the current farm page is retained.
Open full application returns to the selected view. It is an ordinary desktop
window, not an injected game overlay; exclusive fullscreen may cover it.

## Local progress

Profiles and timelines autosave to
%LOCALAPPDATA%/AutoEldenRing/profiles-v3.json. Back up this file for all history.
No save/open-build buttons are present. Existing version-3 libraries and previous
schema-2/3 state files are migrated. Version-1 projects require version 1.
An invalid local library is reported in Settings.
