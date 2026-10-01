"""Daily index closes from FRED, cached locally and never committed (index data is provider-licensed)."""
import csv
import hashlib
import io
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen

FRED_URL = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id={}'
SERIES = {'NASDAQCOM': 'NASDAQ Composite', 'SP500': 'S&P 500', 'DJIA': 'Dow Jones Industrial Average',
          'NIKKEI225': 'Nikkei 225'}
TRAIN_ASSETS = ('NASDAQCOM', 'SP500', 'DJIA')
TEST_ASSET = 'NIKKEI225'
# Chronological windows; the test asset is never loaded by the evolution script.
TRAIN = ('2016-10-01', '2021-12-31')
VALIDATION = ('2022-01-01', '2023-12-31')
TEST_START = '2024-01-01'
CACHE = Path(os.getenv('DATA_CACHE', Path(__file__).resolve().parents[1] / '.cache'))


def parse(text):
    rows = list(csv.reader(io.StringIO(text)))
    if not rows or rows[0][0] != 'observation_date':
        raise ValueError('Unexpected FRED response')
    # FRED marks market holidays with '.' or an empty value.
    return [(day, float(value)) for day, value in rows[1:] if value not in ('', '.')]


def load(series, max_age_hours=12):
    if series not in SERIES:
        raise ValueError('Unknown series')
    path = CACHE / f'{series}.csv'
    if not path.exists() or time.time() - path.stat().st_mtime > max_age_hours * 3600:
        # FRED's edge rejects some custom user agents; the standard library default is accepted.
        request = Request(FRED_URL.format(series), headers={'Accept': 'text/csv'})
        with urlopen(request, timeout=30) as response:
            text = response.read().decode('utf-8')
        parse(text)
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    text = path.read_text(encoding='utf-8')
    return parse(text), hashlib.sha256(text.encode()).hexdigest()


def window(rows, start, end=None):
    """Index range [first, last) of rows inside the dates; earlier rows remain available as warm-up."""
    first = next(i for i, (day, _) in enumerate(rows) if day >= start)
    last = len(rows) if end is None else max(i for i, (day, _) in enumerate(rows) if day <= end) + 1
    return first, last
