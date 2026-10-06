# Verification - 6.1.0

The release builder runs 90 tests: exact integer level/weapon costs, every
supplied catalogue passage, inverse math, shared stock/budgets, atomic state,
six complete translations, save parsing and real Windows/Tk workflows.
The supplied cost JSON remains unchanged (Smithing Stone [4] costs 900 runes).

## Current regression coverage

- Native settings menus: real mouse clicks, keyboard selection, Escape and
  wheel isolation. The same visible root HWND and control instances survive
  language, palette, style and reading-mode changes.
- Three static styles: Modern has two palettes, Windows XP one, Gothic three.
  No RGB scheduler, decorative image renderer or background settings remain.
  Retired preferences migrate without losing progress. Scrolling/movement
  keep opaque, correctly colored native/CTk surfaces.
- Persisted save paths and installation folder survive restart. Linked custom
  directories can acquire another save file. Fresh apps require an initial
  explicit import before any game scan.
- Startup scans keep the same character chooser and manual scans keep calculator
  pages, goals and the active character. Multi-attribute updates do not trigger
  partial-state recalculation. Imports and scans do not overlap.
- Three bounded worker reads recover from transient writes; a rejected read
  preserves the previous library and enables retry. File hashes/mtime do not
  change. Identical scans and opaque-only slot changes add no events; rune,
  attribute, inventory and equipment changes create meaningful snapshots.
- Journal/profile independence, fixed starting class, checkpoint icons,
  owned weapon upgrades/counts, equipped-only overview, paginated inventory,
  zero-wallet stone checklists, upgrade acknowledgement and farm estimates.
- Compact companion, timer/sample handling, inactive-page resource release,
  native resize/movement and ordinary window close.

## Packaged checks

The builder repeats embedded-resource/calculation checks, six-language GUI smoke
checks, audio decoder checks and a checksum-valid synthetic save import using
the compiled executable. VERIFICATION_RESCAN.json additionally exercises startup
from a remembered save and a manual rescan during a running farm timer. It checks
retained windows/pages/goals, deduplicated history and unchanged save bytes/mtime.
Reports contain anonymous counts and booleans, never game names or save paths.

Independent native verification checks AMD64, all artifact/source hashes,
identical EXEs inside the Windows ZIP, extracted-source self-test, one visible
maximized startup window, 40 move/resize cycles and normal WM_CLOSE exit.
A real local PC save is checked read-only where available; the report gives
anonymous character counts only. This is not a gameplay-side inventory audit.

## Measurements

Single source-process samples on this Windows host, with Python 3.14 x64.
PERFORMANCE.json retains explicitly versioned older measurements; historical
RGB/background results describe those old builds, not the current styles.

| Measurement | 6.0.1 | 6.1.0 |
| --- | ---: | ---: |
| Startup including imports | 0.826 s | 0.723 s |
| First catalogue paint | 0.164 s | 0.149 s |
| Catalogue working/private memory | 57.16 / 35.93 MiB | 58.89 / 36.39 MiB |
| CPU in a 3-second catalogue idle sample | 0 s | 0 s |
| Median palette/reading transition, six pages cached | 0.5469 s | 0.4984 s |
| Maximum measured transition | 0.6641 s | 0.6015 s |

Both current runs retain native visibility/identity and report zero callback
errors. The removed four decorative WebP files total 978,434 bytes. No new
runtime dependency was added. Catalogue image caches remain bounded (64 weapons),
with only visible cards decoded. The 2,950 non-weapon records share 1,915 small
icons, totaling 7,251,220 bytes. Startup rescan uses one worker and sends locations,
not the entire checkpoint library, to that worker. All style colors are static.

These measurements exclude EXE extraction/antivirus and are individual samples,
not universal memory, timing or compositor guarantees. Concurrent Elden Ring
play and minimum-spec hardware were not tested on this host.

## Save-reader and other limits

The reader accepts bounded checksum-valid plaintext PC BND4 .sl2/.co2 files.
Actual local slot versions 210 and 250 were checked in earlier and current native
reader workflows. Future layouts, modified/console/encrypted saves are not
promised. File-size/mtime comparisons and ten slot MD5 checks detect concurrent
writes. Rescans read the latest completed disk save, never live game memory;
unsaved progress cannot appear until the game writes it. There is no save
editing, game-input automation or memory injection.

Save-slot identity uses path, slot and original class. Reusing the same slot
with the same class cannot reliably distinguish a new journey. Owned bell
bearings are shown; absent inventory does not establish whether a bearing was
already handed in. Costs use the supplied tables; not every tariff/translated
weapon name was audited in-game by an independent reviewer. Farming durations
remain estimates from measured rates, and OpenDyslexic is a reading preference.

Audio uses lazy pygame-ce/SDL_mixer streaming. Six generated silent fixtures
exercise PCM16/float32 WAV, constant/variable bitrate MP3, FLAC and OGG,
pause/resume, Unicode paths, release and recovery after invalid files. Packaged
checks use the SDL dummy device; audible output and every malformed file are
not verified. Music stays local.

## Reproduce

```powershell
python -m unittest discover -s tests -v
python -m black --check auto_elden_ring tests scripts main.py classes_data.py
python main.py --self-test --report verification.json
python main.py --ui-smoke --report verification-ui.json
python main.py --rescan-check YOUR_SAVE.sl2 --report verification-rescan.json
python scripts/benchmark_ui.py --report performance.json
python scripts/benchmark_appearance.py --report appearance.json
```

All acceptance switches also work in the Windows EXE. Rescan-check uses an
isolated temporary profile library and never resets the user's real profiles.
Source/EXE/Windows ZIP are paired by RELEASE_MANIFEST.json and SHA256SUMS.txt.
Screenshot fixtures contain synthetic demo data only. Public historical archives
are audited independently; original 1.0.0 stays local-only and is replaced for
publication by the sanitized 1.0.1 source/EXE pair.
