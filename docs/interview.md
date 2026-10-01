# Five-minute interview walkthrough

1. Open the live page. Let the evolution play: training Sharpe climbs towards 2 while the same genome's validation Sharpe stays near zero. Name it: overfitting of a 36-gene search space.
2. Point at the DNA heatmap converging, then at the champions: chosen on validation, frozen, never tuned again.
3. Scroll to the Nikkei 225 test. Say the result plainly: no champion beat buy & hold. Hedge beat every champion without knowing which would work, but it learned slowly at this reward scale.
4. Switch to the synthetic tab, press New seed a few times: the best expert changes, and Fixed Share follows it where Hedge cannot. Explain alpha as "never fully forget anyone".
5. Show `combine` in core.py (one loop, alpha = 0 is Hedge) and the causality tests that change future prices and check that past positions do not move.

Present this as classical algorithms implemented, tested and evaluated with a held-out protocol. It is not an original algorithm or a profitable trading system. The negative test result is the point: the protocol caught what the training curve hid.
