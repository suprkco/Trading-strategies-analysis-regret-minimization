"""Fixed, untuned synthetic development scenarios; not financial validation."""
import hashlib
import json
import platform
import statistics
from datetime import datetime, timezone
from pathlib import Path

from regret_lab.core import (
    SCENARIOS,
    evaluate,
    fixed_share_parameters,
    synthetic_returns,
)


def main():
    records = []
    share_eta, share_alpha = fixed_share_parameters(500)
    for scenario in SCENARIOS:
        runs = []
        for seed in range(20):
            values = synthetic_returns(seed, 500, scenario)
            report = evaluate(values)
            report.pop('trace')
            share = evaluate(values, share_eta, alpha=share_alpha)
            runs.append({'seed': seed, 'input_sha256': hashlib.sha256(json.dumps(values).encode()).hexdigest(), **report,
                         'fixed_share_reward': share['cumulative_reward'], 'fixed_share_regret': share['regret']})
        records.append({'scenario': scenario, 'runs': runs,
                        'mean_reward': statistics.mean(r['cumulative_reward'] for r in runs),
                        'mean_uniform_reward': statistics.mean(r['uniform_reward'] for r in runs),
                        'mean_regret': statistics.mean(r['regret'] for r in runs),
                        'std_regret': statistics.stdev(r['regret'] for r in runs),
                        'mean_fixed_share_reward': statistics.mean(r['fixed_share_reward'] for r in runs),
                        'mean_fixed_share_regret': statistics.mean(r['fixed_share_regret'] for r in runs),
                        'fixed_share_beats_hedge': sum(r['fixed_share_reward'] > r['cumulative_reward'] for r in runs),
                        'best_expert_counts': {e: sum(r['best_fixed_expert'] == e for r in runs) for e in report['expert_rewards']}})
    artifact = {'generated_at': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
                'scope': 'Synthetic development scenarios; seeds 0-19; 500 rounds; no tuning or financial backtest.',
                'fixed_share': {'eta': share_eta, 'alpha': share_alpha, 'declared_mean_segment': 80},
                'records': records}
    Path('evaluation').mkdir(exist_ok=True)
    Path('evaluation/results.json').write_text(json.dumps(artifact, indent=2) + '\n', encoding='utf-8')
    for row in records:
        print(f"{row['scenario']:<10} hedge={row['mean_reward']:.4f} share={row['mean_fixed_share_reward']:.4f} uniform={row['mean_uniform_reward']:.4f} "
              f"regret={row['mean_regret']:.4f} sd={row['std_regret']:.4f} share_regret={row['mean_fixed_share_regret']:.4f} "
              f"share>hedge={row['fixed_share_beats_hedge']}/20 best={row['best_expert_counts']}")


if __name__ == '__main__':
    main()
