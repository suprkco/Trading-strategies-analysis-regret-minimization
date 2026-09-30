"""Hedge on bounded expert rewards; this is not a brokerage simulator."""
import math
import random

EXPERTS = ('cash', 'long', 'momentum', 'contrarian')
BOUND = 0.02


def synthetic_returns(seed=42, rounds=500, scenario='switching'):
    if scenario not in {'up', 'down', 'switching', 'noise'}:
        raise ValueError('Unknown scenario')
    if not 1 <= rounds <= 100_000:
        raise ValueError('rounds must be between 1 and 100000')
    rng = random.Random(seed)
    values = []
    for t in range(rounds):
        drift = {'up': 0.004, 'down': -0.004, 'noise': 0.0,
                 'switching': 0.006 if (t // 50) % 2 == 0 else -0.006}[scenario]
        values.append(drift + rng.uniform(-0.01, 0.01))
    return values


def exposures(history):
    # Only completed rounds are visible; no same-round or future return.
    momentum = float(sum(history[-5:]) > 0) if history else 0.0
    contrarian = 1.0 - momentum if history else 0.0
    return (0.0, 1.0, momentum, contrarian)


def evaluate(returns, eta=None, horizon=None):
    values = list(returns)
    if not values or any(not math.isfinite(r) or abs(r) > BOUND for r in values):
        raise ValueError('Expected nonempty finite returns bounded by +/-0.02')
    horizon = len(values) if horizon is None else horizon
    if horizon < len(values):
        raise ValueError('Declared horizon is shorter than the sequence')
    eta = math.sqrt(8 * math.log(len(EXPERTS)) / horizon) if eta is None else eta
    if not math.isfinite(eta) or not 0 < eta <= 10:
        raise ValueError('eta must be finite and in (0, 10]')
    logs = [0.0] * len(EXPERTS)
    totals = [0.0] * len(EXPERTS)
    cumulative = uniform = 0.0
    trace = []
    history = []
    for t, realized in enumerate(values):
        shift = max(logs)
        weights = [math.exp(w - shift) for w in logs]
        weights = [w / sum(weights) for w in weights]
        positions = exposures(history)
        rewards = [position * realized for position in positions]
        reward = sum(w * g for w, g in zip(weights, rewards))
        cumulative += reward
        uniform += sum(rewards) / len(rewards)
        totals = [s + g for s, g in zip(totals, rewards)]
        trace.append({'round': t + 1, 'return': realized, 'weights': weights,
                      'exposures': positions, 'expert_rewards': rewards,
                      'reward': reward, 'cumulative_reward': cumulative,
                      'regret': max(totals) - cumulative})
        # Normalize rewards in [-B, B] to losses in [0, 1].
        losses = [(BOUND - reward) / (2 * BOUND) for reward in rewards]
        logs = [w - eta * loss for w, loss in zip(logs, losses)]
        history.append(realized)
    best = max(range(len(EXPERTS)), key=totals.__getitem__)
    return {'rounds': len(values), 'horizon': horizon, 'eta': eta,
            'reward_bound': BOUND, 'cumulative_reward': cumulative,
            'uniform_reward': uniform, 'expert_rewards': dict(zip(EXPERTS, totals)),
            'best_fixed_expert': EXPERTS[best], 'regret': totals[best] - cumulative,
            'regret_upper_bound': 2 * BOUND * (math.log(len(EXPERTS)) / eta + eta * len(values) / 8),
            'trace': trace}
