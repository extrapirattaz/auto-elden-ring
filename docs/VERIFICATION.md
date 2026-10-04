# Verification â€” 5.0.0

The release builder runs 73 tests covering exact rune costs, every supplied
catalogue passage, inverse math, shared stock, budgets, atomic storage, migrations,
weighted farming and real Tk workflows.

New save fixtures verify original class, permanent stats, runes, upgrades,
instance references, directly encoded goods, held/storage stones, checksums,
truncation, unchanged-file hashes, deduplicated refresh and atomic batch failure.
Real widgets verify the initially empty journal, fixed class, custom event stats
and weapons, auto-upgrade events, preservation of other owned copies, selected-slot
refresh, named farm spots, compact wallet updates, inactive-page release, page
identity through language/palette changes, all semantic palette surfaces,
stable reading-font sizes and RGB start/stop.

Earlier widget tests retain six-language/four-style page coverage, zero-wallet
purchase acknowledgement, upgrade resets, individual weapon editing, repeated
catalogue open/scroll/close cycles, bounded caching and 30 native resize/move/
popup-close cycles during a farm timer. Timed 60/60/180 trials use simulated
deadlines with real callbacks rather than a claimed in-game farming session.

One local PC save containing four characters was read and imported twice.
The file's SHA-256 and modification timestamp remained identical, current
character values populated planners and unchanged refresh added no events.
No names, account identifiers, save paths or save contents are shipped.
This verifies the reader's workflow, not a side-by-side gameplay inventory audit.

The EXE runs calculation/resource and GUI smoke checks, including six languages,
four styles, fonts, images, empty/event timelines, named spots and the compact
wallet. VERIFICATION_EXE.json and VERIFICATION_UI.json record those results. A synthetic PC save also runs through the packaged reader; VERIFICATION_SAVE.json records deduplication, unchanged-file checks and held/storage stone totals.
RELEASE_MANIFEST.json hashes the precise source snapshot and all three artifacts.
Screenshots show actual rendered application windows with synthetic demo data.

Version 4.0.1 introduced checks for the level-713 input, a single goal duration, starting-class investment, its farm-time equivalent, wallet separation, efficiency, boundary levels and legacy measurements. Version 5.0.0 remeasured startup, catalogue and presentation modes on the same host.

## Performance

Single source-process samples on this Windows host, with the pinned Python
environment. PERFORMANCE.json retains earlier comparison data.

| Measurement | 2.0.2 | 3.0.0 | 4.0.0 | 5.0.0 |
| --- | ---: | ---: | ---: | ---: |
| Startup including imports | 0.789 s | 0.631 s | 0.726 s | 0.689 s |
| First catalogue paint | 24.694 s | 0.144 s | 0.159 s | 0.159 s |
| Working memory with catalogue | 216.03 MiB | 56.16 MiB | 57.72 MiB | 55.50 MiB |
| Private memory with catalogue | 194.36 MiB | 35.11 MiB | 36.25 MiB | 35.77 MiB |
| CPU in a 3-second idle sample | 0 s | 0.0312 s | 0.0312 s | 0.0469 s |

Only visible cards are drawn; the image cache is capped at 64. Catalogue assets
remain 2,265,200 bytes. RGB is opt-in and draws native text at most 15 times per second
with a three-second hue cycle and fixed surfaces; it pauses drawing while the main window is hidden.
Background art is static and resize rendering is debounced. Save parsing runs
in one background worker. The compact view releases inactive cached pages and remains visible independently of the hidden main window. The 4.0.0 source sample measured 1.0469 CPU seconds in three seconds with RGB animation. The 5.0.0 sample measured 0.0312 seconds with six modern pages, 0.1875 seconds with animated RGB text, and 0.0625 seconds in compact mode with RGB drawing paused. RGB is more expensive than the static styles; these are single host samples, not hardware guarantees.
Measurements do not include one-file extraction or antivirus scanning.

Native caption/resize/close handling is retained. CustomTkinter's disruptive
withdraw/update/reveal caption sequence remains disabled. Theme/language/reading
updates suspend native repaint, mutate retained controls, then repaint children.
Native inner scroll-frame backgrounds now follow semantic colors as well. Artwork is reused during window movement, remains aligned to the scroll viewport and is replaced only after new image layers are ready.
These checks do not prove the absence of compositor artifacts on every GPU.

Six generated silence fixtures exercise WAV PCM16, WAV float32, MP3 constant/variable bitrate with metadata, FLAC and OGG. Tests verify decoder loading, pause/resume without rewind, Unicode paths, resource release and recovery after an invalid stream. The packaged EXE repeats decoding with SDL's dummy device and reports VERIFICATION_AUDIO.json. Silence/device-state checks do not prove audible output or compatibility with every malformed/music file.

## Limits

- No input automation, memory injection, save editing or live game polling.
- Reader coverage is checksum-valid plaintext PC BND4 .sl2/.co2 structure.
  Actual local slot versions 210 and 250 were verified; all save versions,
  modified saves, console formats and future changes are not guaranteed.
- Only supported catalogue weapons and ordinary stones feed the calculators.
  Other inventory categories are not an exhaustive collectible tracker.
- A save slot is matched by file path, slot and original class. Reusing the same
  slot with the same class cannot reliably identify an entirely new journey.
- No simultaneous Elden Ring/minimum-spec PC test or universal GPU guarantee.
- No independent in-game audit of every supplied tariff or native-speaker review
  of every editorial weapon translation.
- OpenDyslexic is a reading preference, not a clinical effectiveness claim.
- Buff rates and future farming times remain estimates.
- No unrestricted game-media redistribution license is asserted.

## Reproduce

~~~powershell
python -m unittest discover -s tests -v
python main.py --self-test --report verification.json
python main.py --ui-smoke --report verification-ui.json
python scripts/benchmark_ui.py --report performance.json
python scripts/verify_save_readonly.py --save YOUR_SAVE.sl2 --report save-check.json
~~~

The self-test and GUI switches also work in the standalone EXE.


## Version 5 profile and UI checks

New real-widget cases verify empty startup selection and modal ownership,
explicit character activation, keep/replace decisions, replacement rollback,
installation/roaming discovery, catalogue ownership and checkpoint icons,
wheel capture without parent movement, compact zero-wallet stone checks,
compact timer/result capture, native-text RGB with fixed surfaces, per-palette
artwork replacement and restoration of plain surfaces.

Normal app screenshots use synthetic Demo Tarnished data only. Generated
background sources/prompts are documented in GENERATED_BACKGROUNDS.md. The
window background and transparent labels/containers share crops from the same
scene, with a fixed readability tint; cards remain opaque by design.
