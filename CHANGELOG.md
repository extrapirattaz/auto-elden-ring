# Changelog

## 4.0.1 — 2026-10-04

- Added an editable current level for the level-713 farming objective.
- Removed its duplicate maximum-level duration card.
- Added runes invested since the starting class and their equivalent farming time.
- Kept investment separate from held runes and left character attributes unchanged.
- Added numerical boundary, legacy-state and real-widget regression checks.

## 4.0.0 — 2026-10-04

- Fixed stale native scroll backgrounds and semantic palette propagation.
- Batched language, palette and reading-mode repainting without reopening pages.
- Moved Elden landscape art into the full window background.
- Renamed Windows XP, restricted it to one blue/grey palette and square geometry.
- Animated opt-in RGB smoothly; no strobe flashes are implemented.
- Replaced the journal with initially empty character cards and a true timeline.
- Unified character/journey names, fixed starting classes and added custom events.
- Added read-only checksum-validated PC save import and deduplicated change events.
- Imported stats, runes, catalogue weapons/upgrades and held/storage stones.
- Preserved selected save slots, higher targets and other owned weapon copies.
- Added automatic weapon-upgrade events and immutable detailed snapshots.
- Removed save/open-build actions; retained atomic local progress/migration.
- Added named farm spots and character/weapon time estimates.
- Added an always-on-top compact companion with editable runes and inactive-page release.
- Added save-reader, atomic-import, timeline, appearance and compact-flow checks.

## 3.0.0 — 2026-10-03

- Restored native Windows caption, move, maximize, resize and close handling;
  colored the caption through DWM without removing native window styles.
- Cached pages, updated controls in place, bounded catalogue image caching,
  rendered only visible cards and compressed icons to WebP.
- Fixed callback ownership during popup/page destruction and debounced autosave.
- Disabled CTk's withdraw/update/reveal titlebar cycle after reproducing and
  fixing a native Tk access violation during resize and popup destruction.
- Added four visual styles with independent palettes, including generated Elden
  landscape art, XP square controls/toolbars and static rainbow text.
- Added bundled OpenDyslexic reading mode and optional local MP3/WAV playback.
- Made purchase acknowledgement independent of runes; satisfied rows stay checked.
- Made upgrade acknowledgement update weapon levels and reset all stock/runes.
- Added independent character/journey profiles and immutable dated checkpoints.
- Clarified inverse next-upgrade input and kept selected-weapon editing bounded.
- Added schema-2 migration, schema-3 build files and atomic profile libraries.
- Added lifecycle, profile, checklist, presentation and performance verification.

## 2.0.2 — 2026-10-03

- Added an integrated Windows title bar with dragging, minimize/maximize/close
  controls and native resizing, keeping the caption inside the selected theme.

## 2.0.1 — 2026-10-03

- Preserved elapsed duration in the entry field when an ordinary farming test
  is stopped early, so recording cannot restore the previous 60-second value.
- Improved the German golden-horn label.

## 2.0.0 — 2026-10-03

- Rebuilt the desktop around five calm, rounded screens and three themes.
- Blended the Windows title bar on supported Windows versions.
- Derived current/target character levels from permanent attributes.
- Removed the separate tracking-origin field and shopping-cart workflow.
- Added a categorized multi-selection gallery with 487 bundled icons.
- Added six interface languages and complete localized weapon-name coverage.
- Combined manual price, inverse next-upgrade quotes and exact catalogue planning.
- Added shared inventory, missing-stone checklists and explicit purchase/upgrade
  accounting that preserves surplus stock.
- Added local autosave, versioned build projects and resume prompts.
- Added timer reset, sequential 60/60/180-second tests, weighted averages and
  per-sample buff normalization with baseline/optimized projections.
- Added conditional free-goal input and percentage labels.
- Replaced development documentation with English documentation.
- Removed obsolete helper scripts; retained the unchanged supplied cost table.

## 1.0.0 — 2026-10-03

Initial offline Python/Tk release: exact level tables, catalogue upgrades,
inverse math, multi-weapon costs, measured farming and project persistence.

Version-1 release archives are preserved. Schema-1 projects remain usable
with the corresponding version-1 executable.
