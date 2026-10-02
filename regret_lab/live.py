"""Out-of-sample replay: each seed's frozen champions, buy & hold and cash on declared test markets,
combined online by Hedge and Fixed Share."""
import json
import math
import statistics
from pathlib import Path

from regret_lab.core import combine, fixed_share_parameters
from regret_lab.genetic import backtest, features, max_drawdown, sharpe
from regret_lab.market import (
    PREVIOUSLY_SEEN,
    SERIES,
    TEST_ASSETS,
    TEST_START,
    load,
    window,
)

EVOLUTION = Path(__file__).resolve().parents[1] / 'evaluation' / 'evolution'
DECLARED_HORIZON = 756  # three trading years, declared before the test; the window keeps growing daily
TEST_MEAN_SEGMENT = 63  # one quarter: Fixed Share's assumed regime length on daily data
WARMUP_FROM = '2022-01-01'
T_95 = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571, 7: 2.447, 8: 2.365, 9: 2.306, 10: 2.262}


def manifest():
    return json.loads((EVOLUTION / 'manifest.json').read_text(encoding='utf-8'))


def metrics(daily):
    return {'sharpe': sharpe(daily), 'total_return': math.prod(1 + r for r in daily) - 1,
            'max_drawdown': max_drawdown(daily)}


def prepare(market, rows=None):
    rows = rows if rows is not None else load(market)[0]
    # Indicators look back at most 250 trading days; two years of warm-up leaves identical values and a
    # fraction of the work on long histories such as the Nikkei's since 1949.
    rows = [row for row in rows if row[0] >= WARMUP_FROM]
    closes = [value for _, value in rows]
    returns, f = features(closes)
    start, end = window(rows, TEST_START)
    return {'rows': rows, 'asset': (closes, returns, f), 'start': start, 'end': end}


def replay(run, market, prepared, bound, detail=True):
    closes, returns, _ = prepared['asset']
    start, end = prepared['start'], prepared['end']
    names, series, positions = [], [], []
    for champion in run['champions']:
        daily, exposure = backtest(champion['dna'], prepared['asset'], start, end)
        names.append(champion['id'])
        series.append(daily)
        positions.append(exposure)
    names += ['buy & hold', 'cash']
    series += [returns[start:end], [0.0] * (end - start)]
    positions += [[1.0] * (end - start), [0.0] * (end - start)]
    clipped = sum(abs(r) > bound for s in series for r in s)
    matrix = [[max(-bound, min(bound, s[t])) for s in series] for t in range(end - start)]
    horizon = max(DECLARED_HORIZON, len(matrix))
    hedge = combine(matrix, bound, horizon=horizon)
    eta, alpha = fixed_share_parameters(horizon, TEST_MEAN_SEGMENT, len(names))
    share = combine(matrix, bound, eta, horizon, alpha)
    learners = {}
    for key, result in (('hedge', hedge), ('fixed_share', share)):
        daily = [row['reward'] for row in result['trace']]
        learners[key] = {**metrics(daily), 'eta': result['eta'], 'alpha': result['alpha'], 'regret': result['regret']}
        if detail:
            learners[key].update(daily=daily, weights=[row['weights'] for row in result['trace']])
    experts = [{'name': n, **metrics(s), **({'daily': s, 'exposure': p} if detail else {})}
               for n, s, p in zip(names, series, positions)]
    out = {'market': market, 'title': SERIES[market], 'seed': run['seed'], 'previously_seen': PREVIOUSLY_SEEN.get(market),
           'start': prepared['rows'][start][0], 'end': prepared['rows'][end - 1][0], 'days': end - start,
           'experts': experts, 'learners': learners, 'reward_bound': bound, 'clipped_rewards': clipped,
           'best_fixed_expert': names[hedge['best_index']]}
    if detail:
        out.update(dates=[day for day, _ in prepared['rows'][start:end]], closes=closes[start:end],
                   champions=run['champions'])
    return out


def interval(values):
    """Mean and 95% t-interval half-width across seeds."""
    if len(values) < 2:
        return {'mean': values[0] if values else 0.0, 'half_width': None, 'n': len(values)}
    return {'mean': statistics.mean(values), 'n': len(values),
            'half_width': T_95.get(len(values), 1.96) * statistics.stdev(values) / math.sqrt(len(values))}


def summary(prepared_markets, info=None):
    info = info or manifest()
    bound = info['config']['reward_bound']
    cells, markets = [], []
    for market in TEST_ASSETS:
        if market not in prepared_markets:
            continue
        rows = []
        for run in info['runs']:
            r = replay(run, market, prepared_markets[market], bound, detail=False)
            champs = r['experts'][:-2]
            bh = r['experts'][-2]
            rows.append({'seed': run['seed'], 'market': market, 'hedge': r['learners']['hedge']['sharpe'],
                         'fixed_share': r['learners']['fixed_share']['sharpe'], 'buy_hold': bh['sharpe'],
                         'best_champion': max(c['sharpe'] for c in champs),
                         'mean_champion': statistics.mean(c['sharpe'] for c in champs),
                         'champions_beating_buy_hold': sum(c['sharpe'] > bh['sharpe'] for c in champs),
                         'champions': len(champs), 'clipped': r['clipped_rewards']})
        cells += rows
        markets.append({'market': market, 'title': SERIES[market], 'previously_seen': PREVIOUSLY_SEEN.get(market),
                        'start': r['start'], 'end': r['end'], 'days': r['days'], 'buy_hold': rows[0]['buy_hold'],
                        'hedge_minus_buy_hold': interval([c['hedge'] - c['buy_hold'] for c in rows]),
                        'fixed_share_minus_buy_hold': interval([c['fixed_share'] - c['buy_hold'] for c in rows]),
                        'hedge_minus_mean_champion': interval([c['hedge'] - c['mean_champion'] for c in rows]),
                        'mean_champion_minus_buy_hold': interval([c['mean_champion'] - c['buy_hold'] for c in rows])})
    return {'cells': cells, 'markets': markets, 'seeds': [run['seed'] for run in info['runs']],
            'reward_bound': bound, 'metric': 'annualised Sharpe ratio of net daily returns'}
