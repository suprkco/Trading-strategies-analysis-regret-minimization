import math

import pytest

from regret_lab.core import (
    EXPERTS,
    SCENARIOS,
    evaluate,
    fixed_share_parameters,
    segment_oracle,
    synthetic_path,
    synthetic_returns,
)


def test_hand_calculated_round():
    report = evaluate([0.01], eta=1)
    # Long and short cancel out under uniform weights; long earns 0.01 in hindsight.
    assert report['cumulative_reward'] == pytest.approx(0)
    assert report['regret'] == pytest.approx(0.01)
    assert report['trace'][0]['exposures'] == (0, 1, -1, 0, 0)


def test_update_uses_completed_round():
    trace = evaluate([0.01, -0.01], eta=1)['trace']
    assert trace[0]['weights'] == [0.2] * 5
    # Losses after round 1: cash, momentum, reversal 0.5; long 0.25; short 0.75.
    factors = [math.exp(-0.5), math.exp(-0.25), math.exp(-0.75), math.exp(-0.5), math.exp(-0.5)]
    assert trace[1]['weights'] == pytest.approx([f / sum(factors) for f in factors])
    assert trace[1]['exposures'] == (0, 1, -1, 1, -1)


def test_future_suffix_cannot_change_past_decisions():
    prefix = synthetic_returns(3, 20)
    left = evaluate(prefix + [0.02] * 10, horizon=30)['trace']
    right = evaluate(prefix + [-0.02] * 10, horizon=30)['trace']
    assert left[:20] == right[:20]
    assert left[20]['weights'] == right[20]['weights']
    assert left[20]['exposures'] == right[20]['exposures']


@pytest.mark.parametrize('scenario', SCENARIOS)
def test_reproducibility_probability_simplex_and_bound(scenario):
    values = synthetic_returns(42, 500, scenario)
    assert values == synthetic_returns(42, 500, scenario)
    report = evaluate(values)
    assert report['regret'] <= report['regret_upper_bound'] + 1e-12
    for row in report['trace']:
        assert sum(row['weights']) == pytest.approx(1)
        assert all(0 <= w <= 1 for w in row['weights'])
        assert abs(row['reward']) <= 0.02


def test_zero_rewards():
    report = evaluate([0.0] * 100)
    assert report['regret'] == report['cumulative_reward'] == 0
    assert report['trace'][-1]['weights'] == pytest.approx([0.2] * 5)


@pytest.mark.parametrize('values', [[], [float('nan')], [float('inf')], [0.021], [-0.021]])
def test_invalid_rewards(values):
    with pytest.raises(ValueError):
        evaluate(values)


@pytest.mark.parametrize('eta', [0, -1, float('nan'), float('inf')])
def test_invalid_learning_rate(eta):
    with pytest.raises(ValueError):
        evaluate([0], eta)


def test_cli_json_and_invalid_arguments():
    import json
    import subprocess
    import sys
    result = subprocess.run([sys.executable, '-m', 'regret_lab.cli', '--json', '--rounds', '10'], capture_output=True, text=True, check=True)
    assert json.loads(result.stdout)['rounds'] == 10
    bad = subprocess.run([sys.executable, '-m', 'regret_lab.cli', '--rounds', '0'], capture_output=True)
    assert bad.returncode == 2


def test_regime_segments_cover_the_sequence_and_vary_by_seed():
    winners = set()
    for seed in range(12):
        values, segments = synthetic_path(seed, 500)
        assert segments[0][0] == 0 and segments[-1][1] == 500
        assert all(a[1] == b[0] for a, b in zip(segments, segments[1:]))
        winners.add(evaluate(values)['best_fixed_expert'])
    assert len(winners) >= 3


def test_fixed_share_keeps_a_floor_and_alpha_zero_is_hedge():
    values = synthetic_returns(5, 300)
    eta, alpha = fixed_share_parameters(300)
    share = evaluate(values, eta, alpha=alpha)
    assert all(min(r['weights']) >= alpha / len(EXPERTS) - 1e-12 for r in share['trace'])
    assert evaluate(values, eta, alpha=0)['trace'] == evaluate(values, eta)['trace']


def test_fixed_share_tracks_a_changing_best_expert():
    # Long wins the first half, short the second; momentum and reversal stay weak throughout.
    values = [0.01, 0.01, -0.005] * 66 + [-0.01, -0.01, 0.005] * 66
    eta, alpha = fixed_share_parameters(len(values), mean_segment=len(values) // 2)
    hedge, share = evaluate(values), evaluate(values, eta, alpha=alpha)
    assert max(hedge['expert_rewards'].values()) < 0.7
    assert share['cumulative_reward'] > hedge['cumulative_reward'] + 0.5
    assert share['regret'] < 0


def test_segment_oracle_dominates_every_fixed_expert():
    values, segments = synthetic_path(9, 400)
    oracle = segment_oracle(values, segments)
    assert len(oracle) == 400
    assert oracle[-1] >= max(evaluate(values)['expert_rewards'].values()) - 1e-12


@pytest.mark.parametrize('alpha', [-0.1, 1, float('nan')])
def test_invalid_alpha(alpha):
    with pytest.raises(ValueError):
        evaluate([0.0], alpha=alpha)
