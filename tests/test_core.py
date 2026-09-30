import math

import pytest

from regret_lab.core import evaluate, synthetic_returns


def test_hand_calculated_round():
    report = evaluate([0.01], eta=1)
    assert report['cumulative_reward'] == pytest.approx(0.0025)
    assert report['regret'] == pytest.approx(0.0075)
    assert report['trace'][0]['exposures'] == (0, 1, 0, 0)


def test_update_uses_completed_round():
    trace = evaluate([0.01, -0.01], eta=1)['trace']
    assert trace[0]['weights'] == [0.25] * 4
    assert trace[1]['weights'][1] == pytest.approx(math.exp(0.25) / (3 + math.exp(0.25)))


def test_future_suffix_cannot_change_past_decisions():
    prefix = synthetic_returns(3, 20)
    left = evaluate(prefix + [0.02] * 10, horizon=30)['trace']
    right = evaluate(prefix + [-0.02] * 10, horizon=30)['trace']
    assert left[:20] == right[:20]
    assert left[20]['weights'] == right[20]['weights']
    assert left[20]['exposures'] == right[20]['exposures']


@pytest.mark.parametrize('scenario', ['up', 'down', 'switching', 'noise'])
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
    assert report['trace'][-1]['weights'] == [0.25] * 4


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
