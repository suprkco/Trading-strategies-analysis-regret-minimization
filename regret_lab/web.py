"""Standard-library web server: the browser animates traces computed by regret_lab.core."""
import hashlib
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from regret_lab.core import EXPERTS, evaluate, synthetic_returns

STATIC = Path(__file__).with_name('static')
MAX_WEB_ROUNDS = 2000
SCENARIOS = ('switching', 'up', 'down', 'noise')


def run(query):
    """Validate query parameters and return the same report as the CLI's --json output."""
    def integer(name, default, low, high):
        raw = query.get(name, [str(default)])[0]
        if not raw.lstrip('-').isdigit() or not low <= int(raw) <= high:
            raise ValueError(f'{name} must be an integer between {low} and {high}')
        return int(raw)
    scenario = query.get('scenario', ['switching'])[0]
    if scenario not in SCENARIOS:
        raise ValueError('Unknown scenario')
    seed = integer('seed', 42, 0, 1_000_000)
    rounds = integer('rounds', 500, 10, MAX_WEB_ROUNDS)
    values = synthetic_returns(seed, rounds, scenario)
    return {'data': 'synthetic; no market observations', 'seed': seed, 'scenario': scenario,
            'experts': list(EXPERTS),
            'input_sha256': hashlib.sha256(json.dumps(values).encode()).hexdigest(), **evaluate(values)}


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
