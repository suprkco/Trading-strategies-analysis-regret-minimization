"""Standard-library web server: the browser animates traces computed by regret_lab.core."""
import hashlib
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from regret_lab.core import (
    EXPERTS,
    MEAN_SEGMENT,
    SCENARIOS,
    evaluate,
    fixed_share_parameters,
    segment_oracle,
    synthetic_path,
)

STATIC = Path(__file__).with_name('static')
EVOLUTION = Path(__file__).resolve().parents[1] / 'evaluation' / 'evolution'
MARKET_MAX_AGE = 12 * 3600
_markets = {'at': 0.0, 'prepared': None, 'summary': None, 'tests': {}}
_market_lock = threading.Lock()
MAX_WEB_ROUNDS = 2000


def run(query):
    """Validate query parameters and return the same report as the CLI's --json output."""
    def integer(name, default, low, high):
        raw = query.get(name, [str(default)])[0]
        if not raw.lstrip('-').isdigit() or not low <= int(raw) <= high:
            raise ValueError(f'{name} must be an integer between {low} and {high}')
        return int(raw)
    scenario = query.get('scenario', ['regimes'])[0]
    if scenario not in SCENARIOS:
        raise ValueError('Unknown scenario')
    seed = integer('seed', 42, 0, 1_000_000)
    rounds = integer('rounds', 500, 10, MAX_WEB_ROUNDS)
    values, segments = synthetic_path(seed, rounds, scenario)
    eta, alpha = fixed_share_parameters(rounds)
    share = evaluate(values, eta, alpha=alpha)
    share['trace'] = [{k: row[k] for k in ('weights', 'cumulative_reward', 'regret')} for row in share['trace']]
    return {'data': 'synthetic; no market observations', 'seed': seed, 'scenario': scenario,
            'experts': list(EXPERTS), 'segments': segments, 'declared_mean_segment': MEAN_SEGMENT,
            'input_sha256': hashlib.sha256(json.dumps(values).encode()).hexdigest(),
            'hedge': evaluate(values), 'fixed_share': share, 'segment_oracle': segment_oracle(values, segments)}


def market_state():
    """Fresh FRED data for every declared test market, prepared and summarised at most twice a day."""
    from regret_lab.live import prepare, summary
    from regret_lab.market import TEST_ASSETS
    with _market_lock:
        if _markets['prepared'] is None or time.time() - _markets['at'] > MARKET_MAX_AGE:
            prepared = {market: prepare(market) for market in TEST_ASSETS}
            _markets.update(at=time.time(), prepared=prepared, tests={},
                            summary=json.dumps(summary(prepared)).encode())
        return _markets


def test_payload(query):
    from regret_lab.live import manifest, replay
    from regret_lab.market import TEST_ASSETS
    info = manifest()
    seeds = {run['seed']: run for run in info['runs']}
    market = query.get('market', [TEST_ASSETS[0]])[0]
    seed = query.get('seed', [str(info['runs'][0]['seed'])])[0]
    if market not in TEST_ASSETS or not seed.isdigit() or int(seed) not in seeds:
        raise ValueError('Unknown market or seed')
    state = market_state()
    key = (market, int(seed))
    if key not in state['tests']:
        result = replay(seeds[int(seed)], market, state['prepared'][market], info['config']['reward_bound'])
        state['tests'][key] = json.dumps(result).encode()
    return state['tests'][key]


def warm():
    try:
        market_state()
    except (OSError, ValueError) as error:
        print(f'market warm-up failed: {error}')


class Handler(BaseHTTPRequestHandler):
    server_version = 'regret-lab'

    def send(self, status, body, content_type):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/health':
            return self.send(200, b'{"status":"ok"}', 'application/json')
        if url.path == '/api/run':
            try:
                body = json.dumps(run(parse_qs(url.query))).encode()
            except ValueError as error:
                return self.send(400, json.dumps({'error': str(error)}).encode(), 'application/json')
            return self.send(200, body, 'application/json')
        if url.path == '/api/manifest':
            return self.send(200, (EVOLUTION / 'manifest.json').read_bytes(), 'application/json')
        if url.path == '/api/evolution':
            seed = parse_qs(url.query).get('seed', [''])[0]
            path = EVOLUTION / f'seed-{seed}.json'
            if not seed.isdigit() or not path.exists():
                return self.send(404, b'{"error":"Unknown seed"}', 'application/json')
            return self.send(200, path.read_bytes(), 'application/json')
        if url.path in ('/api/test', '/api/summary'):
            try:
                body = test_payload(parse_qs(url.query)) if url.path == '/api/test' else market_state()['summary']
                return self.send(200, body, 'application/json')
            except ValueError as error:
                return self.send(400, json.dumps({'error': str(error)}).encode(), 'application/json')
            except OSError as error:
                return self.send(503, json.dumps({'error': f'Market data unavailable: {error}'}).encode(), 'application/json')
        if url.path == '/':
            return self.send(200, (STATIC / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        self.send(404, b'Not found', 'text/plain')

    do_HEAD = do_GET


def main():
    port = int(os.getenv('PORT', '8000'))
    host = os.getenv('HOST', '127.0.0.1')
    print(f'regret lab on http://{host}:{port}')
    if os.getenv('WARM_MARKETS', '1') == '1':
        threading.Thread(target=warm, daemon=True).start()
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == '__main__':
    main()
