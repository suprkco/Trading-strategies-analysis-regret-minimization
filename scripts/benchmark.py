"""Fixed, untuned synthetic development scenarios; not financial validation."""
import hashlib
import json
import platform
import statistics
from datetime import datetime, timezone
from pathlib import Path

from regret_lab.core import evaluate, synthetic_returns


def main():
    records = []
    for scenario in ['up', 'down', 'switching', 'noise']:
        runs = []
        for seed in range(20):
            values = synthetic_returns(seed, 500, scenario)
            report = evaluate(values)
            report.pop('trace')
            runs.append({'seed': seed, 'input_sha256': hashlib.sha256(json.dumps(values).encode()).hexdigest(), **report})
        records.append({'scenario': scenario, 'runs': runs,
                        'mean_reward': statistics.mean(r['cumulative_reward'] for r in runs),
                        'mean_uniform_reward': statistics.mean(r['uniform_reward'] for r in runs),
                        'mean_regret': statistics.mean(r['regret'] for r in runs),
                        'std_regret': statistics.stdev(r['regret'] for r in runs)})
    artifact = {'generated_at': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
                'scope': 'Synthetic development scenarios; seeds 0-19; 500 rounds; no tuning or financial backtest.',
                'records': records}
    Path('evaluation').mkdir(exist_ok=True)
    Path('evaluation/results.json').write_text(json.dumps(artifact, indent=2) + '\n', encoding='utf-8')
    for row in records:
        print(f"{row['scenario']:<12} reward={row['mean_reward']:.6f} uniform={row['mean_uniform_reward']:.6f} regret={row['mean_regret']:.6f} sd={row['std_regret']:.6f}")


if __name__ == '__main__':
    main()
