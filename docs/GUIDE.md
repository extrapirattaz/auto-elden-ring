# User guide — 3.0.0

## Character

Choose the original starting class. Enter permanent attributes without equipment
or temporary bonuses. The class sets minimum values; attributes are capped at 99.
Level equals the sum of attributes minus 79.

Levels update while valid attributes are entered. Calculate levels refreshes
costs after recording held runes. Spending covers the starting-class level
through the calculated current level. The budget result states actual levels,
levels gained and remaining runes. Lower target attributes display a rebirth
notice; redistribution itself is not charged as level growth.

## Weapons

Manual price asks for normal/somber, blacksmith price for +0 → +1, current
upgrade, target and optional copies. Defaults are +24 normal and +10 somber.
Use next-upgrade price changes the input to the quote for the next step:
enter current +9 and the +9 → +10 quote, for example. The standard profile
is inverted before remaining costs are calculated.

Choose weapons opens category headings and illustrated cards. Click to select,
click again to deselect. Search accepts English and localized names. Done opens
the selected weapon overview. Choose a weapon in the editor to set its individual
current/target upgrades and copies; the other selected weapons retain their values.

Maximum without dragon stones sets +24 normal and +9 somber without reducing
already higher upgrades. Totals separate forge fees and missing-stone purchases.
The affordable result uses shared stock and wallet, progressively raising a
common target capped at +24/+9. It does not optimize which weapon to prioritize.

Manual formulas assume a standard profile. Catalogue weapons retain supplied
exact tariffs, including Soldier's Crossbow, Pulley Crossbow and Jar Cannon.

## Materials and progress

The planner assumes all relevant miner's bell bearings are available at the
Twin Maiden Husks. Enter owned counts or select I have none. Stock is shared:
one stone cannot be allocated twice.

Missing stones lists quantities and costs. Confirm Purchased after acquiring
the indicated batch: stones are added and the row stays checked in green.
No wallet value is required. This records what you did in the game; it does not
simulate a rune transaction. The same satisfied requirement cannot be purchased twice.

After buying materials and visiting the blacksmith, confirm Upgrades completed.
Current upgrades become their targets and ALL recorded ordinary stock, held
runes and purchase checks reset to zero, including surplus materials. Actual
leftovers can be entered again. This acknowledgement is accepted even if the
planning wallet or materials were insufficient. The app trusts your confirmation.

Ancient prices, ordinary requirements and stock show question marks. Rune totals
exclude their acquisition. Double-click an ordinary unit price to override it
after confirming the standard value is being replaced. Restore prices removes
overrides.

Held runes are user-reported and only calculate the remaining farming deficit;
the application never reads the game.

## Rune farming

Record rune gain only, excluding pre-existing runes. A zero starting balance is
convenient but not required. Start one minute runs 60 seconds. Reset cancels and
restores one minute. A stopped ordinary test uses its elapsed duration.

Full test clears earlier measurements and runs separately started 60, 60 and
180-second tests. After each finish enter gain and notes, record the result, then
start the next test. The final rate is total runes divided by 300 seconds,
expressed per minute. Each sample keeps buffs selected at timer start.

Gold Scarab is +20%, gold-pickled fowl foot +30%, golden horn tender +40%.
Scarab multiplies a single consumable; foot and horn are mutually exclusive.
Silver discovery items add 0% runes. Each sample is normalized using its own
multiplier before aggregation. Projections compare no buffs, scarab, foot,
scarab + foot and scarab + horn. Enemy rounding and buff uptime make these
projections estimates rather than exact future earnings.

Choose character, weapons, combined, level 713 or free objective. The free input
appears only for free objectives. Held runes are deducted once. Efficiency adjusts
time estimates. Editing gain/duration switches from sample averages to the
entered single measurement; recording enables sample averages again.

## Settings, save and resume

Choose six languages and three themes. This release has no Windows XP imitation.
The Windows title bar is integrated into the selected theme. Drag its empty
area to move the window, double-click to maximize/restore, and use the right
controls to minimize, maximize or close. Native resize borders remain available.
Save build writes goals, current/target attributes, weapons, wallet, stock,
overrides, farm samples, language and theme into a JSON project.

Open build prompts for current runes and whether to keep saved current attributes.
Otherwise the character screen opens for editing. The stock calculator then asks
for current owned stones.

Autosave lives at %LOCALAPPDATA%\AutoEldenRing\session-v2.json, outside the source
and download folders. Failed loads start a new session and show the error in
Settings. Version-1 projects remain tied to version 1.


## Visual styles and reading mode

Style changes button geometry, font, navigation layout and decoration. Modern
uses rounded panels; Elden Ring uses serif text, gold accents, icons and bundled
fantasy landscape art; XP nostalgia uses square buttons and a horizontal toolbar;
Rainbow uses static multicolored headings/navigation. Each style has three color
palettes. No animation loop runs in the background.

Reading mode temporarily applies larger OpenDyslexic text and a cream palette.
The selected style/palette remain saved and return when reading mode is disabled.
Music is optional: choose a local MP3/WAV, play/restart, pause or stop. Closing
the app closes its own playback device. Playback does not start automatically.

## Characters and journal

Open Journal or the character button, then New character. Enter a character
name, journey name and original class. Profiles have independent attributes,
weapons, stock, runes and checkpoints. Switching saves the valid current state
and stops the active timer/music before changing context.

To record progress, enter a checkpoint note and an ISO date/time, or Use now.
Save checkpoint creates an immutable snapshot, sorted by date. View checkpoint
shows the saved class, attributes, level and weapon upgrades. Later edits do
not change earlier snapshots. Names/journey labels can be renamed.

The library saves locally to %LOCALAPPDATA%/AutoEldenRing/profiles-v3.json.
Back up this file for all profiles and checkpoint history. Save project exports
one current build state, rather than the entire library. Schema-2 builds import
with default profile/style preferences; new exports use schema 3.
