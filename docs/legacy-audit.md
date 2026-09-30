# Historical prototype audit

The original src/ code is retained unchanged and is not used by regret_lab. Do not use its outputs for performance claims. Legacy dependency pins are preserved in src/requirements-legacy.txt for provenance, not recommended installation.

Observed in the original source:

- Joueur.acheter and vendre change cash by price alone rather than price times quantity; no affordability/inventory checks.
- Initialization generates Strategie 0/1 while selection expects Strategie 1/2.
- strategie2 is a placeholder with a signature inconsistent with its call.
- Market reset fails to reset current price; advancement repeats the initial observation and misaligns state.
- The displayed company can change without replacing the downloaded series.
- Data depends on wall-clock dates and a remote service; randomness is unseeded.
- No explicit regret metric, comparator, reproducible evaluation or tests existed.

The new package is an isolated online-learning experiment, not a repaired version of the old trading engine. New results must never be attributed to the legacy simulator.
