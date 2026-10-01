import math
import random

import pytest

from regret_lab.genetic import (
    GENES,
    WARMUP,
    backtest,
    decode,
    describe,
    evolve,
    features,
    fitness,
    sharpe,
)
from regret_lab.live import replay
from regret_lab.market import parse, window


def synthetic_asset(seed=1, n=WARMUP + 300):
    rng = random.Random(seed)
    closes = [100.0]
    for _ in range(n - 1):
        closes.append(closes[-1] * (1 + rng.gauss(0.0003, 0.01)))
    returns, f = features(closes)
    return closes, returns, f


def test_genome_decodes_inside_declared_ranges():
    for dna in ([0.0] * len(GENES), [1.0] * len(GENES), [0.5] * len(GENES)):
        d = decode(dna)
        assert all(-1 <= w <= 1 for w in d['calm'] + d['stress'])
        assert 0.03 <= d['stop_loss'] <= 0.30 + 1e-12 and 1 <= d['cooldown'] <= 40 and 0 <= d['max_short'] <= 1
    assert describe([0.5] * len(GENES))


def test_features_are_causal():
    closes, _, f = synthetic_asset()
    altered = closes[:400] + [c * 1.5 for c in closes[400:]]
    _, g = features(altered)
    for key in f:
        assert f[key][:400] == g[key][:400], key


def test_backtest_ignores_the_future_and_respects_limits():
    asset = synthetic_asset()
    closes, returns, f = asset
    dna = [random.Random(3).random() for _ in GENES]
    daily, exposure = backtest(dna, asset, WARMUP, 450)
    shocked = [c if t < 400 else c * (2 if t % 2 else 0.5) for t, c in enumerate(closes)]
    r2, f2 = features(shocked)
    _, exposure2 = backtest(dna, (shocked, r2, f2), WARMUP, 450)
    # The exposure held on day t is chosen from closes up to t-1, so day 400's position is unchanged.
    assert exposure[:400 - WARMUP + 1] == exposure2[:400 - WARMUP + 1]
    assert all(-1 <= e <= 1 for e in exposure)
    assert len(daily) == 450 - WARMUP


def test_transaction_costs_are_charged():
    asset = synthetic_asset()
    flat = asset[0], [0.0] * len(asset[1]), asset[2]
    dna = [0.5] * len(GENES)
    dna[GENES.index('bias')] = 1.0
    daily, exposure = backtest(dna, flat, WARMUP, WARMUP + 50)
    assert sum(daily) < 0 and exposure[-1] > 0


def test_evolution_is_reproducible_and_keeps_elites():
    assets = {'A': synthetic_asset(1), 'B': synthetic_asset(2)}
    train = {k: (WARMUP, WARMUP + 150) for k in assets}
    valid = {k: (WARMUP + 150, WARMUP + 300) for k in assets}
    first, genomes = evolve(assets, train, valid, seed=5, population=12, generations=4)
    second, _ = evolve(assets, train, valid, seed=5, population=12, generations=4)
    assert first == second
    best = [r['train'][0] for r in first]
    assert best == sorted(best)
    assert fitness(genomes[0], assets, train) == pytest.approx(best[-1])


def test_sharpe_edge_cases():
    assert sharpe([]) == 0 and sharpe([0.01] * 10) == 0
    assert sharpe([0.01, -0.01] * 50) == pytest.approx(0, abs=1e-9)


def test_fred_parsing_skips_holidays():
    rows = parse('observation_date,X\n2024-01-01,.\n2024-01-02,10.5\n2024-01-03,\n2024-01-04,11\n')
    assert rows == [('2024-01-02', 10.5), ('2024-01-04', 11.0)]
    assert window(rows, '2024-01-03') == (1, 2)
    with pytest.raises(ValueError):
        parse('<html>blocked</html>')


def test_replay_runs_offline_on_given_rows():
    rng = random.Random(4)
    rows, price = [], 100.0
    for i in range(700):
        price *= 1 + rng.gauss(0, 0.01)
        rows.append((f'{2023 + i // 300}-{1 + i % 300 // 25:02d}-{1 + i % 25:02d}', price))
    artifact = {'champions': [{'id': f'C{i}', 'dna': [rng.random() for _ in GENES]} for i in range(3)]}
    result = replay(artifact, rows)
    names = [e['name'] for e in result['experts']]
    assert names == ['C0', 'C1', 'C2', 'buy & hold', 'cash']
    hedge = result['learners']['hedge']
    assert len(hedge['daily']) == len(result['dates']) and all(math.isclose(sum(w), 1) for w in hedge['weights'])
    assert result['dates'][0] >= '2024-01-01'
