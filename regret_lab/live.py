"""Out-of-sample replay: frozen champions, buy-and-hold and cash on the never-seen test index, combined online."""
import json
import math
from pathlib import Path

from regret_lab.core import combine, fixed_share_parameters
from regret_lab.genetic import backtest, features, sharpe
from regret_lab.market import SERIES, TEST_ASSET, TEST_START, load, window

ARTIFACT = Path(__file__).resolve().parents[1] / 'evaluation' / 'evolution.json'
TEST_BOUND = 0.15  # daily reward bound for the online learners; larger moves are clipped and counted
DECLARED_HORIZON = 756  # three trading years, declared before the test; the window keeps growing daily
TEST_MEAN_SEGMENT = 63  # one quarter: Fixed Share's assumed regime length on daily data


def max_drawdown(daily):
    equity = peak = 1.0
    worst = 0.0
    for r in daily:
        equity *= 1 + r
        peak = max(peak, equity)
        worst = min(worst, equity / peak - 1)
    return worst


def replay(artifact=None, rows=None):
    artifact = artifact or json.loads(ARTIFACT.read_text(encoding='utf-8'))
    rows = rows if rows is not None else load(TEST_ASSET)[0]
    closes = [value for _, value in rows]
    returns, f = features(closes)
    start, end = window(rows, TEST_START)
    asset = (closes, returns, f)
    names, series, positions = [], [], []
    for champion in artifact['champions']:
        daily, exposure = backtest(champion['dna'], asset, start, end)
        names.append(champion['id'])
        series.append(daily)
        positions.append(exposure)
    names += ['buy & hold', 'cash']
    series += [returns[start:end], [0.0] * (end - start)]
    positions += [[1.0] * (end - start), [0.0] * (end - start)]
    clipped = sum(abs(r) > TEST_BOUND for s in series for r in s)
    matrix = [[max(-TEST_BOUND, min(TEST_BOUND, s[t])) for s in series] for t in range(end - start)]
    horizon = max(DECLARED_HORIZON, len(matrix))
    hedge = combine(matrix, TEST_BOUND, horizon=horizon)
    eta, alpha = fixed_share_parameters(horizon, TEST_MEAN_SEGMENT, len(names))
    share = combine(matrix, TEST_BOUND, eta, horizon, alpha)
    learners = {}
    for key, result in (('hedge', hedge), ('fixed_share', share)):
        daily = [row['reward'] for row in result['trace']]
        learners[key] = {'daily': daily, 'weights': [row['weights'] for row in result['trace']],
                         'regret': result['regret'], 'regret_upper_bound': result['regret_upper_bound'],
                         'eta': result['eta'], 'alpha': result['alpha'], 'sharpe': sharpe(daily),
                         'total_return': math.prod(1 + r for r in daily) - 1, 'max_drawdown': max_drawdown(daily)}
    experts = [{'name': n, 'daily': s, 'exposure': p, 'sharpe': sharpe(s),
                'total_return': math.prod(1 + r for r in s) - 1, 'max_drawdown': max_drawdown(s)}
               for n, s, p in zip(names, series, positions)]
    return {'asset': TEST_ASSET, 'title': SERIES[TEST_ASSET], 'source': 'FRED',
            'dates': [day for day, _ in rows[start:end]], 'closes': closes[start:end],
            'experts': experts, 'learners': learners, 'reward_bound': TEST_BOUND, 'clipped_rewards': clipped,
            'declared_horizon': DECLARED_HORIZON, 'best_fixed_expert': names[hedge['best_index']]}
