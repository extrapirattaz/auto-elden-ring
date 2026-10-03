# Verification — 2.0.2

The builder runs 34 tests covering exact levels, all catalogue passages,
inverse profiles, shared inventory, atomic persistence, purchase/upgrade
transactions, budgets and buff-normalized weighted sample rates.

Real widgets exercise attributes, inverse input, catalogue rendering and every
language/theme combination. The complete 60/60/180 workflow uses simulated
deadlines with actual callbacks. This verifies timing logic, not a five-minute
in-game farming session.

The EXE self-check verifies embedded costs and catalogue counts.
VERIFICATION_EXE.json records its result and database hash.
VERIFICATION_UI.json records a separate packaged GUI/resource smoke check.
Screenshots are captures of the actual application.
RELEASE_MANIFEST.json and SHA256SUMS.txt establish artifact correspondence.

## Limits

- No gameplay automation or game-process integration.
- No independent in-game validation of all regulation entries.
- No native-speaker review of all localizations.
- No assertion of unrestricted game-media redistribution rights.
- Buff comparisons are projections affected by rounding and uptime.
- The Windows caption is integrated into the theme; native resizing is retained.
- Schema-1 projects require version 1; this release uses schema 2.

## Reproduce

~~~powershell
python -m unittest discover -s tests -v
python main.py --self-test --report verification.json
python main.py --ui-smoke --report verification-ui.json
~~~

The same report switches work with the standalone executable.
