# User guide - 6.0.1

## Start with a character

The main window opens maximized. Choose New Character, Import Save Game or an
existing character. Change Character returns to this chooser inside the main
window; Back returns from nested views.

Open Journal, then New character. Enter the character's in-game name and original
starting class. There is one name for both the character and its journey.
The starting class cannot be changed later. No sample character or timeline
event is added automatically. Click a character card to open its timeline.
Choose a character before entering the calculators.

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
checks for saves there, then the roaming directory. All detected supported characters are imported. You can also select an intended
.sl2/.co2 file explicitly.

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
Equipment in the sidebar opens the current profile summary. Checkpoint details
open the corresponding immutable snapshot in that same main window. The default
Equipped tab shows equipment slots, not every acquired or upgraded weapon.
Weapons, Armor and Items show inventory plus storage counts; weapon copies are
grouped by upgrade. At most 24 cards are rendered per page, with 84-pixel icons.
Unknown item IDs remain visible. Some DLC and Czech item names currently fall
back to English; all six interface languages and weapon name tables remain.

Bell Bearings shows smithing/somber miner bearings held in the inventory.
A question mark means not held: it does not prove the bearing was never given
to Twin Maiden Husks. Shop delivery flags are not parsed. Character portrait
rendering is not supported; the profile uses an initial avatar.

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

Choose a local MP3/WAV/FLAC/OGG to play or pause; Play resumes a paused track. Closing the app
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


## Profile selection and import decisions

Every normal startup asks you to choose a character. A fresh installation lists
no characters and offers New Character and Import Save Game. Existing profiles
show their name, original class and level. Selecting one restores its goals,
weapon selections, stock and farming measurements. The name in the sidebar
opens this chooser again. The chooser uses an initial badge, not an extracted
game portrait.

Import Installation Folder checks that folder, its Game/save/saves subfolders,
and the standard roaming EldenRing account folders. Installation files and saves
normally live separately. All characters in the detected PC saves are imported;
Select .sl2/.co2 also accepts a specific file. Detection does not promise support
for unknown future binary layouts. Reads remain bounded and checksum validated.

When manual characters exist, import asks whether to keep them and add game
characters, or replace only manual profiles. Previously imported characters and
matching goals are preserved. Replacement is transactional: an invalid import
leaves the library intact. Canceling a pending import dialog stops its application
without changing profiles. Refresh from Save keeps profiles without asking again.

Blue checks in the catalogue mean owned weapons, with saved upgrades and copy
counts. Selection checks identify weapons chosen for your goal. Not in saved
inventory refers to this supported catalogue and the latest imported/manual
snapshot. The catalogue does not inspect live game memory.

Checkpoint details display attribute cards and Equipped / Weapons / Armor /
Items / Bell Bearings / Changes / Goal tabs. Weapon cards include their bundled icons, upgrades and copies. Large
inventories are paginated at 24 cards to keep memory and native widgets bounded.

## Compact tools and music

The mini companion has no native minimize/maximize/resize caption. Drag its
character heading; releasing it near a monitor edge snaps to that monitor's
usable area, including monitors with negative desktop coordinates. Open Full
Application restores the main window.

Weapons shows the total, remaining runes and a scrollable stone checklist.
I have all missing stones acknowledges possession regardless of the wallet.
Individual checks update the same profile inventory as the main calculator.
Ancient dragon stones stay outside the purchase checklist.

Farm provides Start, Stop, Reset, runes held and measured runes. Entering updated
held runes during/after a test prefills the gain relative to the starting wallet;
you can edit the measured gain. Record Result stores it as a farming sample.
An already running main-window timer continues in compact mode. Opening a
compact view does not change your goals or spend runes.

Music streams MP3, WAV, FLAC and OGG using bundled SDL decoders, initialized only
when Play is pressed. Play resumes the same track after Pause. Choosing another
file or changing character releases the previous stream. There is no music Stop
button. Corrupt streams or unavailable audio devices display an error and release
resources; another file can then be selected.

RGB keeps backgrounds fixed and animates cached native text with a three-second
hue cycle, at most 15 updates/s. Its styled beta notice explains the playful troll
mode. It is optional and contains no strobe flashes. All dropdown menus capture
wheel input inside their list rather than scrolling the parent page.


## Window behavior and personal backgrounds

Forms, imports, weapon selection and snapshot details are owned panels inside
the main window. Back closes the current panel. Selecting a calculator closes
transient panels. The native operating-system file chooser is used only when
selecting a file or directory. Compact mode hides the main window and presents
its single small companion.

Dropdowns are child controls, never independent desktop windows. Scrolling a
list leaves the calculator scroll position unchanged. Moving/resizing the main
window, navigating away, clicking outside, Escape or switching applications
closes a list without changing its selection. Only a click or Enter commits.

Elden Ring Settings offers Choose Background and Restore Default. PNG, JPEG
and WebP are supported. The chosen path is stored per character; if the file
is missing later, generated theme artwork is used. Personal files are not copied
into release artifacts. Content panels have opaque palette backgrounds to avoid
Tk transparency artifacts during scrolling. Artwork is updated for resizing or
palette/background changes, never for scrolling.
