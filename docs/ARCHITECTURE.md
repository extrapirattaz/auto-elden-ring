# Source layout and maintenance

The current source is English, formatted with Black (100 columns), and organized
by responsibility. Formatting is a development operation, not a runtime feature.

| Location | Responsibility |
| --- | --- |
| main.py | Application entry point and packaged verification commands |
| classes_data.py / elden_ring_costs.json | Starting classes and authoritative supplied cost tables |
| auto_elden_ring/core.py | Integer level/weapon costs, inverse costs and stone requirements |
| auto_elden_ring/planner.py | Shared character, weapon, budget, stock and farming state |
| auto_elden_ring/ui.py | Main window, retained calculator pages and settings controls |
| auto_elden_ring/presentation.py | Semantic themes, backgrounds, journal/import UI and animation lifecycle |
| auto_elden_ring/journey_ui.py | Profile chooser, inventory details, native-menu ownership and compact companion |
| auto_elden_ring/dropdown.py | Native Tk menu selection with deferred application callbacks |
| auto_elden_ring/panels.py | Navigation panels owned by the main window |
| auto_elden_ring/windows.py | Caption/font/monitor helpers and retained-widget layout transactions |
| auto_elden_ring/gallery.py | Virtualized illustrated weapon selection and bounded image cache |
| auto_elden_ring/save_reader.py | Bounded, checksum-validated, read-only PC save parsing |
| auto_elden_ring/profiles.py / history.py / storage.py | Atomic persistence, migration, import transactions and immutable snapshots |
| auto_elden_ring/i18n.py / style_text.py / journey_text.py | Stable identifiers and six-language text catalogues |
| auto_elden_ring/styles.py / audio.py | Lightweight appearance data and lazy optional audio |
| assets/ | Offline icons, fonts, translations, backgrounds and provenance/licences |
| tests/ | Calculation boundaries, fixtures and real-widget/native-menu workflows |
| scripts/ | Release building, screenshots, benchmarks, archive audit and explicit local reset |
| docs/ | User guide, evidence, architecture and per-version GitHub publishing copy |
| releases/<version>/ | Matched local EXE, source/Windows ZIPs, manifests and reports; not committed |

Use `python -m unittest discover -s tests -v` for the required suite. Native-input
tests require an interactive Windows desktop and operate only on their own app.
Use `python -m pip install -r requirements-dev.txt` then
`python -m black --check auto_elden_ring tests scripts main.py classes_data.py`
to check formatting. Black is absent from requirements.txt and the runtime build.

Appearance changes retain controls and the native window. Only changed properties
are configured. Native menus own their normal selection/cancellation behavior;
application callbacks run after posting ends. Root visibility is never suspended
with WM_SETREDRAW. RGB animates text on the active page at up to 15 Hz and polls
more slowly while the main window is hidden. Modern/XP colors have no animation.
Hidden pages keep their controls, but update font metrics only when shown. The
sidebar layout changes only when entering or leaving XP's horizontal toolbar.

Historical releases are independent snapshots, not folders to merge into current
source. Each source ZIP is hashed against its own manifest and paired EXE. Existing
public historical snapshots remain unchanged; cleaning their implementation
retroactively would invalidate that pairing. The initial 1.0.0 archive contained
a personal example-path comment, so the sanitized 1.0.1 successor was rebuilt.
The original is kept in the ignored, local-only archive and excluded from uploads.
Per-version descriptions explain the behavior that each historical build actually
contains. The current refactor is delivered as 6.0.1, with its own matched artifacts.

Local state lives outside the source under `%LOCALAPPDATA%/AutoEldenRing`.
`python scripts/reset_local_data.py --confirm` explicitly removes known app-state
files. It does not delete game saves, audio, custom images or arbitrary files.
Tests use temporary directories; the application never resets future users on launch.
