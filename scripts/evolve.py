"""Evolve strategy DNA on three US indices for several seeds, select decorrelated champions on a later
validation window, and freeze everything. No test market is loaded here.

Run: python -m scripts.evolve   (about 15 minutes for the default five seeds)
"""
import argparse
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

from regret_lab import genetic
from regret_lab.genetic import (
    GENES,
    describe,
    encode,
    evolve,
    features,
    fitness,
    select_champions,
)
from regret_lab.market import (
    SERIES,
    TEST_ASSETS,
    TRAIN,
    TRAIN_ASSETS,
    VALIDATION,
    load,
    window,
)

SEEDS = (11, 22, 33, 44, 55)
OUTPUT = Path('evaluation/evolution')


def window_digest(rows, first, last):
    return hashlib.sha256(json.dumps(rows[first:last]).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, nargs='+', default=list(SEEDS))
    parser.add_argument('--population', type=int, default=120)
    parser.add_argument('--generations', type=int, default=60)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    assets, train, validation, provenance, train_returns = {}, {}, {}, {}, []
    for name in TRAIN_ASSETS:
        rows, _ = load(name)
        closes = [value for _, value in rows]
        returns, f = features(closes)
        assets[name] = (closes, returns, f)
        train[name], validation[name] = window(rows, *TRAIN), window(rows, *VALIDATION)
        train_returns += [abs(r) for r in returns[train[name][0]:train[name][1]]]
        provenance[name] = {'title': SERIES[name], 'source': 'FRED', 'train_sha256': window_digest(rows, *train[name]),
                            'validation_sha256': window_digest(rows, *validation[name])}
    # The online learners' reward bound comes from training data only: the 99.5th percentile daily move.
    train_returns.sort()
    reward_bound = round(train_returns[int(0.995 * (len(train_returns) - 1))], 4)
    args.output.mkdir(parents=True, exist_ok=True)
    runs = []
    for seed in args.seeds:
        started = time.perf_counter()

        def report(record, seed=seed):
            print(f"seed {seed} gen {record['generation']:>2}  best train {record['train'][0]:6.3f}  "
                  f"its validation {record['validation'][0]:6.3f}  diversity {record['diversity']:.3f}", flush=True)
        history, genomes = evolve(assets, train, validation, seed, args.population, args.generations, on_generation=report)
        champions = [{'id': f'C{i + 1}', 'dna': dna, 'code': encode(dna), 'traits': describe(dna),
                      'train_score': fitness(dna, assets, train), 'validation_score': value}
                     for i, (value, dna) in enumerate(select_champions(genomes, assets, validation))]
        seconds = round(time.perf_counter() - started, 1)
        (args.output / f'seed-{seed}.json').write_text(
            json.dumps({'seed': seed, 'history': history}, separators=(',', ':')) + '\n', encoding='utf-8')
        runs.append({'seed': seed, 'seconds': seconds, 'champions': champions,
                     'best_train': history[-1]['train'][0], 'best_train_validation': history[-1]['validation'][0]})
        for c in champions:
            print(f"  {c['id']} train {c['train_score']:.3f} validation {c['validation_score']:.3f}  {c['traits']}")
    manifest = {'generated_at': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
                'config': {'population': args.population, 'generations': args.generations,
                           'score': f'Sharpe - {genetic.DRAWDOWN_PENALTY} x |max drawdown|, mean over training indices',
                           'costs': {'base_bps': genetic.BASE_COST * 1e4, 'volatility_share': genetic.VOL_COST,
                                     'short_financing_per_year': genetic.SHORT_FINANCING},
                           'diversity_penalty': genetic.DIVERSITY_PENALTY, 'champion_max_abs_correlation': 0.5,
                           'train': list(TRAIN), 'validation': list(VALIDATION), 'test_assets': list(TEST_ASSETS),
                           'reward_bound': reward_bound},
                'genes': list(GENES), 'data': provenance, 'runs': runs}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=1) + '\n', encoding='utf-8')
    print('reward bound', reward_bound)


if __name__ == '__main__':
    main()
