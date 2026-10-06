# Changelog

## 6.1.0 — 2026-10-06

- Remove the Rainbow style, RGB animation, decorative backgrounds and background controls.
- Limit Modern to Porcelain White and Charcoal Black; keep one Classic Windows XP palette.
- Rename the fantasy presentation Gothic and its original palette Antique Gold; preserve its layout and three static color choices.
- Migrate retired preferences without losing characters, goals, inventory or checkpoints.
- Remember imported save paths and the selected installation folder locally.
- Rescan remembered PC saves asynchronously on startup and through a persistent Rescan game saves button.
- Refresh current progression without reopening the main window, replacing calculator pages or cancelling farm timers.
- Retry transient save reads in a bounded background worker and retain the previous snapshot on failure.
- Add timeline events for changed stats, runes, inventory or equipment; ignore opaque-only slot changes and repeated scans.
- Preserve manual profiles, selected characters and planned targets during rescans.
- Refresh English documentation, screenshots, matching x64 artifacts and per-version GitHub publishing instructions.

## 6.0.1 — 2026-10-05

- Replace imitation dropdown lists with native Tk menus throughout the application.
- Apply menu selections after native tracking ends; support ordinary click, keyboard and Escape behavior.
- Keep the same visible native window during language, style, palette and reading-mode changes.
- Remove top-level WM_SETREDRAW visibility changes and unnecessary sidebar repacking.
- Batch changed widget properties and defer hidden-page font metrics until the page becomes active.
- Stop redrawing hidden timeline text and reduce RGB polling while the main window is hidden.
- Organize UI/localization modules by responsibility, format Python consistently and add maintenance comments.
- Reset local development profiles; verify public archives exclude personal profiles, saves and paths.
- Add exact per-version GitHub release notes and manual publishing instructions.
- Keep source, x64 EXE and Windows ZIP paired with hashes and packaged verification.

## 1.0.1 — 2026-10-05 (historical maintenance)

- Provide a sanitized successor to the original 1.0.0 calculator for public sharing.
- Remove a personal example-path comment and unused configuration.
- Move original formula compatibility references into the historical test folder.
- Format the maintained Python source and provide an English usage guide.
- Preserve original calculator behavior and rebuild the matching x64 EXE and both ZIPs.
- Keep the original 1.0.0 archive local-only; publish 1.0.1 instead.

## 6.0.0 — 2026-10-04

- Open maximized with character selection inside the main window.
- Replace secondary application windows with owned navigation panels and Back actions.
- Keep one native window for normal workflows; compact mode temporarily substitutes its borderless companion.
- Replace floating dropdown windows with in-window lists dismissed on move, resize, navigation, outside click or focus loss.
- Retain calculator widget identities during palette, style and language changes.
- Remove per-label/per-scroll background compositing; use fixed artwork behind readable opaque panels.
- Add a persistent custom PNG/JPEG/WebP background preference for Elden Ring style only.
- Import armor, talismans, goods, held key items and equipped weapon/armor/talisman slots read-only.
- Add equipped-only checkpoint overview plus separate Weapons, Armor, Items and Bell Bearings views.
- Show larger offline item icons, counts, weapon upgrades, goals and inventory changes.
- Keep handed-in bell bearing status explicitly unverified rather than guessing an absent inventory item means locked shops.
- Preserve old profiles through schema migration; public archives contain no private profiles or saves.
- Compress and deduplicate new icon assets; load only visible inventory pages with bounded image caches.
- Add binary save fixtures and real-widget navigation, startup, menu, background and persistence regression checks.

## 5.0.0 — 2026-10-04

- Added an explicit startup character chooser with an empty initial library.
- Added keep/replace decisions for manual profiles, transactional import and cancellation.
- Discover PC saves from installation folders plus roaming accounts; import all detected characters.
- Added blue ownership badges with upgrade/copy counts to the weapon selector.
- Replaced checkpoint text dumps with attribute cards, tabs and paginated weapon icons.
- Added wheel-local scrollable dropdowns in every style.
- Added distinct generated Elden Night, Moonlight and Ember backgrounds.
- Composited transparent text/containers on artwork and removed black crop padding.
- Kept RGB surfaces fixed; animate cached native text at a maximum of 15 updates/s.
- Added an experimental RGB notice without strobe flashes.
- Replaced MCI with lazy SDL streaming for MP3/WAV/FLAC/OGG and true pause/resume.
- Removed the redundant music Stop action; audio resources are released on track/profile changes.
- Added a borderless mini companion, monitor-edge snapping, stone checklist and timer/results.
- Added decoder fixtures, packaged audio checks and profile/mini/menu regression tests.

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
