"""Hedge and Fixed Share on bounded expert rewards; this is not a brokerage simulator."""
import math
import random

EXPERTS = ('cash', 'long', 'short', 'momentum', 'reversal')
BOUND = 0.02
SCENARIOS = ('regimes', 'switching', 'up', 'down', 'noise')
# Regime kind -> (autocorrelation phi, drift). Each kind favours a different expert.
REGIMES = {'trending': (0.6, 0.0), 'mean-reverting': (-0.6, 0.0), 'bull': (0.0, 0.004), 'bear': (0.0, -0.004)}
MEAN_SEGMENT = 80  # declared expected regime length for 'regimes'; used to set Fixed Share, never fitted


def synthetic_path(seed=42, rounds=500, scenario='regimes'):
    """Return bounded returns and the generating segments [(start, end, kind)]."""
    if scenario not in SCENARIOS:
        raise ValueError('Unknown scenario')
    if not 1 <= rounds <= 100_000:
        raise ValueError('rounds must be between 1 and 100000')
    rng = random.Random(seed)
    if scenario != 'regimes':
        values = []
        for t in range(rounds):
            drift = {'up': 0.004, 'down': -0.004, 'noise': 0.0,
                     'switching': 0.006 if (t // 50) % 2 == 0 else -0.006}[scenario]
            values.append(drift + rng.uniform(-0.01, 0.01))
        if scenario == 'switching':
            segments = [(s, min(s + 50, rounds), 'bull' if (s // 50) % 2 == 0 else 'bear') for s in range(0, rounds, 50)]
        else:
            segments = [(0, rounds, {'up': 'bull', 'down': 'bear', 'noise': 'noise'}[scenario])]
        return values, segments
    values, segments, previous = [], [], 0.0
    while len(values) < rounds:
        kind = rng.choice(list(REGIMES))
        phi, drift = REGIMES[kind]
        start, length = len(values), rng.randint(40, 120)
        for _ in range(min(length, rounds - start)):
            previous = max(-BOUND, min(BOUND, phi * previous + drift + rng.uniform(-0.01, 0.01)))
            values.append(previous)
        segments.append((start, len(values), kind))
    return values, segments


def synthetic_returns(seed=42, rounds=500, scenario='regimes'):
    return synthetic_path(seed, rounds, scenario)[0]


def exposures(history):
    # Only completed rounds are visible; no same-round or future return.
    if not history:
        return (0.0, 1.0, -1.0, 0.0, 0.0)
    last = (history[-1] > 0) - (history[-1] < 0)
    return (0.0, 1.0, -1.0, float(last), float(-last))


def fixed_share_parameters(horizon, mean_segment=MEAN_SEGMENT, experts=len(EXPERTS)):
    """Tracking tuning for about horizon/mean_segment switches (Herbster and Warmuth, 1998)."""
    if horizon < 2:
        raise ValueError('Fixed Share needs a horizon of at least 2 rounds')
    switches = max(1, round(horizon / mean_segment))
    alpha = min(0.5, switches / (horizon - 1))
    entropy = -alpha * math.log(alpha) - (1 - alpha) * math.log(1 - alpha)
    eta = math.sqrt(8 * ((switches + 1) * math.log(experts) + (horizon - 1) * entropy) / horizon)
    return eta, alpha


def combine(expert_rewards, bound, eta=None, horizon=None, alpha=0.0):
    """Hedge (alpha=0) or Fixed Share over any full-information reward matrix [round][expert] in [-bound, bound]."""
    rows = [list(r) for r in expert_rewards]
    k = len(rows[0]) if rows else 0
    if not rows or k < 2 or any(len(r) != k for r in rows):
        raise ValueError('Expected a nonempty rectangular reward matrix with at least two experts')
    if any(not math.isfinite(g) or abs(g) > bound for r in rows for g in r):
        raise ValueError(f'Expected finite rewards bounded by +/-{bound}')
    horizon = len(rows) if horizon is None else horizon
    if horizon < len(rows):
        raise ValueError('Declared horizon is shorter than the sequence')
    eta = math.sqrt(8 * math.log(k) / horizon) if eta is None else eta
    if not math.isfinite(eta) or not 0 < eta <= 10:
        raise ValueError('eta must be finite and in (0, 10]')
    if not math.isfinite(alpha) or not 0 <= alpha < 1:
        raise ValueError('alpha must be in [0, 1)')
    weights = [1 / k] * k
    totals = [0.0] * k
    cumulative = uniform = 0.0
    trace = []
    for t, rewards in enumerate(rows):
        reward = sum(w * g for w, g in zip(weights, rewards))
        cumulative += reward
        uniform += sum(rewards) / k
        totals = [s + g for s, g in zip(totals, rewards)]
        trace.append({'round': t + 1, 'weights': weights, 'expert_rewards': rewards, 'reward': reward,
                      'cumulative_reward': cumulative, 'regret': max(totals) - cumulative})
        # Normalize rewards in [-B, B] to losses in [0, 1]; shifting by the minimum keeps exp() stable.
        losses = [(bound - g) / (2 * bound) for g in rewards]
        low = min(losses)
        weights = [w * math.exp(-eta * (loss - low)) for w, loss in zip(weights, losses)]
        total = sum(weights)
        weights = [(1 - alpha) * w / total + alpha / k for w in weights]
    best = max(range(k), key=totals.__getitem__)
    return {'rounds': len(rows), 'horizon': horizon, 'eta': eta, 'alpha': alpha, 'reward_bound': bound,
            'cumulative_reward': cumulative, 'uniform_reward': uniform, 'totals': totals, 'best_index': best,
            'regret': totals[best] - cumulative,
            'regret_upper_bound': 2 * bound * (math.log(k) / eta + eta * len(rows) / 8), 'trace': trace}


def evaluate(returns, eta=None, horizon=None, alpha=0.0):
    """Synthetic lab: the five rule experts on a bounded return sequence, combined by Hedge or Fixed Share."""
    values = list(returns)
    if not values or any(not math.isfinite(r) or abs(r) > BOUND for r in values):
        raise ValueError('Expected nonempty finite returns bounded by +/-0.02')
    history, matrix, positions = [], [], []
    for realized in values:
        positions.append(exposures(history))
        matrix.append([position * realized for position in positions[-1]])
        history.append(realized)
    result = combine(matrix, BOUND, eta, horizon, alpha)
    for row, realized, position in zip(result['trace'], values, positions):
        row['return'], row['exposures'] = realized, position
    totals = result.pop('totals')
    best = result.pop('best_index')
    return {**result, 'expert_rewards': dict(zip(EXPERTS, totals)), 'best_fixed_expert': EXPERTS[best]}


def segment_oracle(returns, segments):
    """Hindsight comparator that switches to each segment's best expert: an upper reference, not a policy."""
    trace = evaluate(returns)['trace']
    total, path = 0.0, []
    for start, end, _ in segments:
        sums = [sum(trace[t]['expert_rewards'][k] for t in range(start, end)) for k in range(len(EXPERTS))]
        best = max(range(len(EXPERTS)), key=sums.__getitem__)
        for t in range(start, end):
            total += trace[t]['expert_rewards'][best]
            path.append(total)
    return path
