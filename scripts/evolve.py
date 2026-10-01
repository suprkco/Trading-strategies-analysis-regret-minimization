"""Evolve strategy DNA on three US indices, select champions on a later validation window, freeze them.

The test index (Nikkei 225) is never loaded here. Run: python -m scripts.evolve
"""
import argparse
import hashlib
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

from regret_lab.genetic import GENES, describe, evolve, features, fitness
from regret_lab.market import SERIES, TRAIN, TRAIN_ASSETS, VALIDATION, load, window


def window_digest(rows, first, last):
    return hashlib.sha256(json.dumps(rows[first:last]).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--population', type=int, default=120)
    parser.add_argument('--generations', type=int, default=60)
    parser.add_argument('--champions', type=int, default=5)
    parser.add_argument('--output', type=Path, default=Path('evaluation/evolution.json'))
    args = parser.parse_args()
    assets, train, validation, provenance = {}, {}, {}, {}
    for name in TRAIN_ASSETS:
        rows, _ = load(name)
        closes = [value for _, value in rows]
        returns, f = features(closes)
        assets[name] = (closes, returns, f)
        train[name], validation[name] = window(rows, *TRAIN), window(rows, *VALIDATION)
        provenance[name] = {'title': SERIES[name], 'source': 'FRED', 'train': list(TRAIN), 'validation': list(VALIDATION),
                            'train_sha256': window_digest(rows, *train[name]),
                            'validation_sha256': window_digest(rows, *validation[name])}
    started = time.perf_counter()

    def report(record):
        print(f"gen {record['generation']:>2}  best train {record['train'][0]:6.3f}  "
              f"median {record['train'][len(record['train']) // 2]:6.3f}  "
              f"best-train's validation {record['validation'][0]:6.3f}  diversity {record['diversity']:.3f}")
    history, genomes = evolve(assets, train, validation, args.seed, args.population, args.generations, on_generation=report)
    final = history[-1]
    # Champions: best validation Sharpe in the final population, then frozen before any test data exists here.
    order = sorted(range(len(final['dna'])), key=lambda i: -final['validation'][i])
    champions, seen = [], set()
    for i in order:
        key = tuple(final['dna'][i])
        if key not in seen:
            seen.add(key)
            dna = genomes[i]
            champions.append({'id': f'C{len(champions) + 1}', 'dna': dna, 'traits': describe(dna),
                              'train_sharpe': fitness(dna, assets, train), 'validation_sharpe': final['validation'][i]})
        if len(champions) == args.champions:
            break
    artifact = {'generated_at': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
                'seconds': round(time.perf_counter() - started, 1),
                'config': {'seed': args.seed, 'population': args.population, 'generations': args.generations,
                           'fitness': 'mean annualised Sharpe of net daily returns across training indices',
                           'transaction_cost_bps': 5},
                'genes': list(GENES), 'data': provenance, 'history': history, 'champions': champions}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, separators=(',', ':')) + '\n', encoding='utf-8')
    for c in champions:
        print(f"{c['id']}  train {c['train_sharpe']:.3f}  validation {c['validation_sharpe']:.3f}  {c['traits']}")


if __name__ == '__main__':
    main()
