# Five-minute interview walkthrough

1. Run python -m regret_lab.cli. Explain why hindsight is allowed for scoring the comparator but not for choosing actions.
2. Run with --scenario down. Explain why cash wins and the learner loses during adaptation.
3. Trace weights, causal exposures, outcome, scoring and update in core.py.
4. Show the test where changing future returns leaves previous decisions unchanged for a fixed horizon.
5. Distinguish additive reward from wealth, fixed regret from switching regret, and full information from bandit feedback.

Present this as a classical algorithm implemented and tested on synthetic data. It is not an original algorithm or a profitable trading system. Explain the old accounting flaw as motivation for explicit invariants. Reproduce and understand the experiment before presenting it.
