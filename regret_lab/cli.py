import argparse
import hashlib
import json
from pathlib import Path

from regret_lab.core import evaluate, synthetic_returns


def main():
    parser = argparse.ArgumentParser(description='Hedge / synthetic online-learning laboratory')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--rounds', type=int, default=500)
    parser.add_argument('--scenario', choices=['up', 'down', 'switching', 'noise'], default='switching')
    parser.add_argument('--eta', type=float)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        values = synthetic_returns(args.seed, args.rounds, args.scenario)
        result = evaluate(values, args.eta)
    except ValueError as error:
        parser.error(str(error))
    report = {'data': 'synthetic; no market observations', 'seed': args.seed,
              'scenario': args.scenario,
              'input_sha256': hashlib.sha256(json.dumps(values).encode()).hexdigest(), **result}
    encoded = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + '\n', encoding='utf-8')
    if args.json:
        print(encoded)
    else:
        print(f"regret / {args.scenario} / seed {args.seed} / {args.rounds} rounds")
        print('Synthetic rewards. Additive score, not compounded investment return.\n')
        print(f"{'POLICY':<20} {'CUMULATIVE REWARD':>20}")
        for name, value in [('hedge', result['cumulative_reward']), ('uniform', result['uniform_reward']), *result['expert_rewards'].items()]:
            print(f'{name:<20} {value:>20.6f}')
        print(f"\nBest fixed expert: {result['best_fixed_expert']} (hindsight comparator)")
        print(f"External regret:   {result['regret']:.6f}")
        print(f"Analytical bound:  {result['regret_upper_bound']:.6f}")
        print('Full information | no costs, slippage, leverage or order execution')


if __name__ == '__main__':
    main()
