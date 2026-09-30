# Method and assumptions

This independently implemented exponential-weighting (Hedge) experiment follows the classical expert-advice framework. Background: Arora, Hazan and Kale, [The Multiplicative Weights Update Method: a Meta-Algorithm and Applications](https://theoryofcomputing.org/articles/v008a006/), Theory of Computing 8 (2012), 121-164. No upstream code was copied.

Expert rewards g lie in [-B,B], B=0.02. Transform them to losses l=(B-g)/(2B) in [0,1]. Before each observation, normalize weights proportional to exp(-eta * cumulative_loss). The learner's reward is the weighted average of expert rewards; update only after scoring.

The exponential-potential argument with Hoeffding's lemma gives loss regret <= ln(K)/eta + eta*T/8. Multiplying by 2B converts to reward units. The default eta=sqrt(8*ln(K)/T) minimizes this expression for a known horizon. It guarantees neither positive rewards nor financial profitability. Full feedback and bounded rewards are essential assumptions.

The uniform baseline averages the same causal expert rewards. The best fixed expert is selected retrospectively for scoring only. Positions are advice, not orders. The linear mixture and sum of rewards do not model reinvested wealth or fees. A trading interpretation would require explicit holdings, cash and turnover accounting.

The generator adds uniform noise in [-0.01,0.01] to drift 0, +/-0.004, or alternating +/-0.006 every 50 rounds. These scenarios are public development fixtures, not a fitted market model.
