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
EVOLUTION = Path(__file__).resolve().parents[1] / 'evaluation' / 'evolution.json'
_test_cache = {'at': 0.0, 'body': None}
_test_lock = threading.Lock()
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


def test_payload(max_age=12 * 3600):
    """Out-of-sample replay on fresh FRED data, recomputed at most twice a day."""
    from regret_lab.live import replay
    with _test_lock:
        if _test_cache['body'] is None or time.time() - _test_cache['at'] > max_age:
            _test_cache['body'] = json.dumps(replay()).encode()
            _test_cache['at'] = time.time()
        return _test_cache['body']


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
        if url.path == '/api/evolution':
            return self.send(200, EVOLUTION.read_bytes(), 'application/json')
        if url.path == '/api/test':
            try:
                return self.send(200, test_payload(), 'application/json')
            except (OSError, ValueError) as error:
                return self.send(503, json.dumps({'error': f'Market data unavailable: {error}'}).encode(), 'application/json')
        if url.path == '/':
            return self.send(200, (STATIC / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        self.send(404, b'Not found', 'text/plain')

    do_HEAD = do_GET


def main():
    port = int(os.getenv('PORT', '8000'))
    host = os.getenv('HOST', '127.0.0.1')
    print(f'regret lab on http://{host}:{port}')
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == '__main__':
    main()
