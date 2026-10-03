# Verification — 3.0.0

The release builder runs 45 tests of exact costs, inverse profiles, all supplied
catalogue passages, shared inventory, atomic storage, schema-2 migration, budgets,
weighted farming, profile isolation and immutable checkpoints.

Real widgets verify six languages, four styles, the reading font, cached page
identity, checklist acknowledgement with zero runes, upgrade resets, individual
weapon editing, 12 catalogue open/scroll/close cycles, bounded image caching,
and 30 resize/move/popup-close cycles while a farming timer is active.
The sequential 60/60/180 workflow uses simulated deadlines with real callbacks.
No five-minute in-game farming session is claimed.

The packaged EXE runs separate calculation/resource and GUI smoke checks,
including every page/language, catalogue images, all four styles and reading mode.
VERIFICATION_EXE.json and VERIFICATION_UI.json record those results.
RELEASE_MANIFEST.json and SHA256SUMS.txt establish source/EXE correspondence.
Screenshots show the rendered application. The native caption is retained;
movement, resize and close no longer use custom frame/style surgery.
CustomTkinter's native-header withdraw/update/reveal sequence is disabled.
A reproducible access violation under queued resize/popup-close events was
eliminated by this change; the same stress test passes with an active timer.

## Measured source performance

Measured in separate processes on the same Windows host and pinned Python
environment, against the archived 2.0.2 source. Values are single-run measurements,
not promises for other hardware. See PERFORMANCE.json and benchmark_ui.py.

| Measurement | 2.0.2 | 3.0.0 |
| --- | ---: | ---: |
| Startup including imports | 0.789 s | 0.631 s |
| First catalogue paint | 24.694 s | 0.144 s |
| Working memory with catalogue | 216.03 MiB | 56.16 MiB |
| Private memory with catalogue | 194.36 MiB | 35.11 MiB |
| Loaded catalogue image cache | 487 | 18 visible; limit 64 |
| CPU time in a 3-second idle sample | 0.0 s | 0.0312 s |

Catalogue assets decreased from 12,425,852 to 2,265,200 bytes. Single-file EXE extraction
and antivirus scanning are outside these source startup measurements.

Native MCI open/play/pause/close passed using a generated silent WAV. Audible
output and MP3 decoder variations were not tested. Files are never uploaded.

## Limits

- No gameplay automation or game-process integration.
- No simultaneous Elden Ring or minimum-spec hardware test.
- Native lifecycle stress tests do not measure every GPU/compositor configuration.
- No independent in-game validation of every supplied tariff.
- No native-speaker review of all localized/editorial names.
- No unrestricted game-media redistribution license is asserted.
- Buff comparisons depend on rounding and uptime.
- OpenDyslexic is an optional reading preference, not a claimed clinical benefit.
- Native caption coloring depends on Windows support; native controls remain usable.
- Schema-1 builds require version 1; schemas 2 and 3 are accepted here.

## Reproduce

~~~powershell
python -m unittest discover -s tests -v
python main.py --self-test --report verification.json
python main.py --ui-smoke --report verification-ui.json
python scripts/benchmark_ui.py --report performance.json
~~~

The self-test and GUI switches also work in the standalone executable.
