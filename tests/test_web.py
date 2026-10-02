import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from regret_lab.core import evaluate, synthetic_returns
from regret_lab.web import Handler, run


@pytest.fixture(scope='module')
def base():
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f'http://127.0.0.1:{server.server_port}'
    server.shutdown()


def test_run_matches_core_evaluation():
    report = run({'scenario': ['down'], 'seed': ['7'], 'rounds': ['120']})
    expected = evaluate(synthetic_returns(7, 120, 'down'))
    assert report['hedge']['regret'] == expected['regret'] and report['hedge']['trace'] == expected['trace']


@pytest.mark.parametrize('query', [{'rounds': ['5000']}, {'rounds': ['abc']}, {'seed': ['-1']}, {'scenario': ['crash']}])
def test_run_rejects_invalid_parameters(query):
    with pytest.raises(ValueError):
        run(query)


def test_http_routes(base):
    assert json.load(urlopen(base + '/health')) == {'status': 'ok'}
    assert b'Evolve strategy DNA' in urlopen(base + '/').read()
    assert json.load(urlopen(base + '/api/run?rounds=50'))['hedge']['rounds'] == 50
    for path, status in [('/api/run?rounds=1', 400), ('/../README.md', 404)]:
        with pytest.raises(HTTPError) as error:
            urlopen(base + path)
        assert error.value.code == status


def test_evolution_artifacts_are_served(base):
    manifest = json.load(urlopen(base + '/api/manifest'))
    assert len(manifest['runs']) == 5 and manifest['config']['test_assets'][0] == 'NIKKEI225'
    seed = manifest['runs'][0]['seed']
    history = json.load(urlopen(f'{base}/api/evolution?seed={seed}'))['history']
    assert len(history) == manifest['config']['generations']
    assert all(len(code) == len(manifest['genes']) for code in history[-1]['dna'])
    assert all(1 <= len(r['champions']) <= 5 for r in manifest['runs'])
    for path in ('/api/evolution?seed=999', '/api/evolution?seed=../manifest'):
        with pytest.raises(HTTPError) as error:
            urlopen(base + path)
        assert error.value.code == 404
    with pytest.raises(HTTPError) as error:
        urlopen(base + '/api/test?seed=1&market=SP500')
    assert error.value.code == 400
