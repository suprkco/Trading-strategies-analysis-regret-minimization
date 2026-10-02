# Method and assumptions

This independently implemented exponential-weighting (Hedge) experiment follows the classical expert-advice framework. Background: Arora, Hazan and Kale, [The Multiplicative Weights Update Method: a Meta-Algorithm and Applications](https://theoryofcomputing.org/articles/v008a006/), Theory of Computing 8 (2012), 121-164. No upstream code was copied.

Expert rewards g lie in [-B,B], B=0.02. Transform them to losses l=(B-g)/(2B) in [0,1]. Before each observation, normalize weights proportional to exp(-eta * cumulative_loss). The learner's reward is the weighted average of expert rewards; update only after scoring.

The exponential-potential argument with Hoeffding's lemma gives loss regret <= ln(K)/eta + eta*T/8. Multiplying by 2B converts to reward units. The default eta=sqrt(8*ln(K)/T) minimizes this expression for a known horizon. It guarantees neither positive rewards nor financial profitability. Full feedback and bounded rewards are essential assumptions.

The uniform baseline averages the same causal expert rewards. The best fixed expert is selected retrospectively for scoring only. Positions are advice, not orders. The linear mixture and sum of rewards do not model reinvested wealth or fees. A trading interpretation would require explicit holdings, cash and turnover accounting.

The synthetic experts are cash (0), long (+1), short (-1), one-day momentum (sign of the last return) and one-day reversal (its opposite). The `regimes` generator draws segments of 40-120 rounds, each trending (AR coefficient +0.6), mean-reverting (-0.6), bull (drift +0.004) or bear (-0.004), with uniform noise in [-0.01, 0.01], clipped to +/-B. Each kind favours a different expert, so the best fixed expert varies by seed. The older fixtures (up, down, noise, alternating drift every 50 rounds) are kept for comparison. None of these is a fitted market model.

## Fixed Share

Fixed Share (Herbster and Warmuth, [Tracking the Best Expert](https://doi.org/10.1023/A:1007424614876), Machine Learning 32, 1998) applies the Hedge update and then mixes a share alpha of weight back to uniform: w <- (1-alpha) w + alpha/K. No expert's weight can collapse, so the learner can follow a best expert that changes. With m expected switches over T rounds, alpha = m/(T-1) and eta = sqrt(8((m+1) ln K + (T-1) H(alpha))/T), where H is the binary entropy, follow the standard tracking bound. Here m = T / declared mean segment length; nothing is fitted to outcomes. The segment oracle on the page switches to each generated segment's best expert in hindsight. It is a reference, not a policy.

## Genetic search and held-out test

The genome, operators, costs and protocol are tabulated in the README. Three choices deserve justification.

- **Score = Sharpe - 2 x |max drawdown|.** Sharpe alone rewards smooth curves that hide a crash; the drawdown term makes tail losses visible to selection. The weight 2 was fixed before running and not searched.
- **Diversity.** Tournament selection uses the score minus 0.5 x the highest correlation (weekly training returns) with any of the five fittest individuals, so near-copies of a leader breed less. Champions are then chosen greedily on validation with a cap of 0.5 on absolute pairwise correlation. Online combination only helps when experts fail at different times.
- **Volatility-dependent costs.** FRED has no volume, so a volume-based impact model (such as Almgren-Chriss) cannot be calibrated. Instead, each unit of exposure traded costs 2 bp plus 10% of the 20-day daily volatility, which makes trading in turbulence expensive. Short exposure pays 3% a year.

The out-of-sample replay (`regret_lab/live.py`) runs each seed's frozen champions, buy & hold and cash on every declared test market. It clips daily rewards to the training data's 99.5th percentile absolute move (6.3%) and counts the clipped values. It combines the experts with Hedge (eta from a declared 756-day horizon) and Fixed Share (declared 63-day regime length). Per market, differences in Sharpe are averaged over the five seeds with a Student-t 95% interval. Five seeds make the intervals wide. A difference whose interval crosses zero is reported as noise, not as a finding.
