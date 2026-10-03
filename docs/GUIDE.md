# User guide — 2.0.2

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
the selected weapon rows with individual current/target upgrades and copies.

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
the indicated batch: runes are deducted and stones added. The same satisfied
requirement cannot be purchased twice.

After buying materials and visiting the blacksmith, confirm Upgrades completed.
Forge fees are deducted, required stones consumed and current upgrades updated.
Surplus stock is preserved. Final +25/+10 steps require separate confirmation
that the ancient dragon stones were obtained.

Ancient prices, ordinary requirements and stock show question marks. Rune totals
exclude their acquisition. Double-click an ordinary unit price to override it
after confirming the standard value is being replaced. Restore prices removes
overrides.

Held runes are user-reported; the application never reads the game. Tracked gain
is wallet growth plus recorded purchases/forge spending since the first balance.
It cannot infer unreported losses.

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
