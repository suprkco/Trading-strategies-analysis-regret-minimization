# Method and assumptions

This independently implemented exponential-weighting (Hedge) experiment follows the classical expert-advice framework. Background: Arora, Hazan and Kale, [The Multiplicative Weights Update Method: a Meta-Algorithm and Applications](https://theoryofcomputing.org/articles/v008a006/), Theory of Computing 8 (2012), 121-164. No upstream code was copied.

Expert rewards g lie in [-B,B], B=0.02. Transform them to losses l=(B-g)/(2B) in [0,1]. Before each observation, normalize weights proportional to exp(-eta * cumulative_loss). The learner's reward is the weighted average of expert rewards; update only after scoring.

The exponential-potential argument with Hoeffding's lemma gives loss regret <= ln(K)/eta + eta*T/8. Multiplying by 2B converts to reward units. The default eta=sqrt(8*ln(K)/T) minimizes this expression for a known horizon. It guarantees neither positive rewards nor financial profitability. Full feedback and bounded rewards are essential assumptions.

The uniform baseline averages the same causal expert rewards. The best fixed expert is selected retrospectively for scoring only. Positions are advice, not orders. The linear mixture and sum of rewards do not model reinvested wealth or fees. A trading interpretation would require explicit holdings, cash and turnover accounting.

The synthetic experts are cash (0), long (+1), short (-1), one-day momentum (sign of the last return) and one-day reversal (its opposite). The `regimes` generator draws segments of 40-120 rounds, each trending (AR coefficient +0.6), mean-reverting (-0.6), bull (drift +0.004) or bear (-0.004), with uniform noise in [-0.01, 0.01], clipped to +/-B. Each kind favours a different expert, so the best fixed expert varies by seed. The older fixtures (up, down, noise, alternating drift every 50 rounds) are kept for comparison. None of these is a fitted market model.

## Fixed Share

Fixed Share (Herbster and Warmuth, [Tracking the Best Expert](https://doi.org/10.1023/A:1007424614876), Machine Learning 32, 1998) applies the Hedge update and then mixes a share alpha of weight back to uniform: w <- (1-alpha) w + alpha/K. No expert's weight can collapse, so the learner can follow a best expert that changes. With m expected switches over T rounds, alpha = m/(T-1) and eta = sqrt(8((m+1) ln K + (T-1) H(alpha))/T), where H is the binary entropy, follow the standard tracking bound. Here m = T / declared mean segment length; nothing is fitted to outcomes. The segment oracle on the page switches to each generated segment's best expert in hindsight. It is a reference, not a policy.

## Genetic search and held-out test

See the README for the genome, operators and protocol. Fitness is the mean annualised Sharpe of net daily returns across three training indices, which rewards consistency over one lucky market. Champions are the five best validation scores in the final generation. The out-of-sample replay (`regret_lab/live.py`) runs the frozen champions, buy & hold and cash on the test index, clips daily rewards to +/-15% (counted, zero so far), and combines them with Hedge (eta from a declared 756-day horizon) and Fixed Share (declared 63-day regime length). The regret bound printed for the test is valid but loose at this reward scale.
