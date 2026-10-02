"""Strategy DNA, causal backtests and a genetic algorithm. Selection pressure, not hand tuning, picks strategies."""
import math
import random

# Each gene is stored in [0, 1] so crossover and mutation are uniform; decode() maps it to its meaning.
SIGNALS = ('momentum_short', 'momentum_long', 'ma_cross', 'rsi', 'bollinger', 'breakout', 'volatility', 'drawdown')
PERIODS = {'momentum_short': (5, 10, 20), 'momentum_long': (60, 120, 250), 'ma_fast': (5, 10, 20, 50),
           'ma_slow': (100, 150, 200), 'rsi': (7, 14, 28), 'bollinger': (10, 20, 50), 'breakout': (20, 55, 120)}
GENES = ([f'calm_{s}' for s in SIGNALS] + [f'stress_{s}' for s in SIGNALS] + [f'period_{p}' for p in PERIODS] +
         ['bias', 'gain', 'dead_zone', 'max_short', 'stress_threshold', 'vol_target', 'vol_target_mix',
          'smoothing', 'stop_loss', 'cooldown'])
WARMUP = 260
BASE_COST = 0.0002       # 2 bp per unit of exposure traded
VOL_COST = 0.1           # plus 10% of the recent daily volatility per unit traded
SHORT_FINANCING = 0.03   # 3% a year on short exposure
DRAWDOWN_PENALTY = 2.0   # score = Sharpe - 2 x |max drawdown|
DIVERSITY_PENALTY = 0.5  # selection score loses 0.5 x correlation with the closest fitter leader
DIVERSITY_LEADERS = 5
ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'


def decode(dna):
    g = dict(zip(GENES, dna))

    def pick(name):
        options = PERIODS[name]
        return options[min(len(options) - 1, int(g[f'period_{name}'] * len(options)))]
    return {'calm': [2 * g[f'calm_{s}'] - 1 for s in SIGNALS], 'stress': [2 * g[f'stress_{s}'] - 1 for s in SIGNALS],
            'periods': {name: pick(name) for name in PERIODS},
            'bias': 2 * g['bias'] - 1, 'gain': 0.5 + 4.5 * g['gain'], 'dead_zone': 0.4 * g['dead_zone'],
            'max_short': g['max_short'], 'stress_threshold': 0.8 + 1.2 * g['stress_threshold'],
            'vol_target': 0.05 + 0.25 * g['vol_target'], 'vol_target_mix': g['vol_target_mix'],
            'smoothing': 0.05 + 0.95 * g['smoothing'], 'stop_loss': 0.03 + 0.27 * g['stop_loss'],
            'cooldown': 1 + int(39 * g['cooldown'])}


def features(closes):
    """Causal indicators: value at t uses closes[0..t] only. Computed once per asset for every period option."""
    n = len(closes)
    returns = [0.0] + [closes[t] / closes[t - 1] - 1 for t in range(1, n)]

    def rolling_std(window):
        out = [0.0] * n
        for t in range(window, n):
            chunk = returns[t - window + 1:t + 1]
            mean = sum(chunk) / window
            out[t] = math.sqrt(sum((r - mean) ** 2 for r in chunk) / window)
        return out

    def sma(window):
        out, running = [0.0] * n, 0.0
        for t in range(n):
            running += closes[t] - (closes[t - window] if t >= window else 0)
            out[t] = running / window if t >= window - 1 else closes[t]
        return out

    vol20, vol10, vol60 = rolling_std(20), rolling_std(10), rolling_std(60)
    f = {'vol20': vol20, 'vol_ratio': [vol10[t] / vol60[t] if vol60[t] else 1.0 for t in range(n)]}
    for p in PERIODS['momentum_short'] + PERIODS['momentum_long']:
        f[('momentum', p)] = [math.tanh((closes[t] / closes[t - p] - 1) / (max(vol20[t], 1e-4) * math.sqrt(p)))
                              if t >= p else 0.0 for t in range(n)]
    averages = {p: sma(p) for p in PERIODS['ma_fast'] + PERIODS['ma_slow'] + PERIODS['bollinger']}
    for fast in PERIODS['ma_fast']:
        for slow in PERIODS['ma_slow']:
            f[('ma', fast, slow)] = [math.tanh(10 * (averages[fast][t] / averages[slow][t] - 1)) for t in range(n)]
    for p in PERIODS['rsi']:
        out = [0.0] * n
        for t in range(p, n):
            gains = sum(max(r, 0) for r in returns[t - p + 1:t + 1])
            losses = sum(max(-r, 0) for r in returns[t - p + 1:t + 1])
            out[t] = (gains - losses) / (gains + losses) if gains + losses else 0.0
        f[('rsi', p)] = out
    for p in PERIODS['bollinger']:
        out = [0.0] * n
        for t in range(p, n):
            chunk = closes[t - p + 1:t + 1]
            sd = math.sqrt(sum((c - averages[p][t]) ** 2 for c in chunk) / p)
            out[t] = math.tanh((closes[t] - averages[p][t]) / sd / 2) if sd else 0.0
        f[('bollinger', p)] = out
    for p in PERIODS['breakout']:
        out = [0.0] * n
        for t in range(p, n):
            low, high = min(closes[t - p + 1:t + 1]), max(closes[t - p + 1:t + 1])
            out[t] = 2 * (closes[t] - low) / (high - low) - 1 if high > low else 0.0
        f[('breakout', p)] = out
    f['volatility'] = [math.tanh(r - 1) for r in f['vol_ratio']]
    f['drawdown'] = [math.tanh(5 * (closes[t] / max(closes[max(0, t - 249):t + 1]) - 1)) for t in range(n)]
    return returns, f


def backtest(dna, asset, start, end):
    """Daily net returns for t in [start, end): exposure is decided at close t-1 and earns return t.

    Costs: BASE_COST plus VOL_COST times recent daily volatility per unit traded (trading is dearer in
    turbulence), and SHORT_FINANCING per year on short exposure.
    """
    closes, returns, f = asset
    d = decode(dna)
    p = d['periods']
    columns = [f[('momentum', p['momentum_short'])], f[('momentum', p['momentum_long'])],
               f[('ma', p['ma_fast'], p['ma_slow'])], f[('rsi', p['rsi'])], f[('bollinger', p['bollinger'])],
               f[('breakout', p['breakout'])], f['volatility'], f['drawdown']]
    exposure, equity, peak, frozen, out, exposures = 0.0, 1.0, 1.0, 0, [], []
    for t in range(max(start, WARMUP), end):
        s = t - 1
        weights = d['stress'] if f['vol_ratio'][s] > d['stress_threshold'] else d['calm']
        score = d['bias'] + sum(w * col[s] for w, col in zip(weights, columns))
        target = math.tanh(d['gain'] * score)
        target = 0.0 if abs(target) < d['dead_zone'] else max(-d['max_short'], target)
        annual_vol = f['vol20'][s] * math.sqrt(252)
        if annual_vol > 0:
            scaled = max(-1.0, min(1.0, target * d['vol_target'] / annual_vol))
            target += d['vol_target_mix'] * (scaled - target)
        if frozen:
            target, frozen = 0.0, frozen - 1
        new = exposure + d['smoothing'] * (target - exposure)
        cost = (BASE_COST + VOL_COST * f['vol20'][s]) * abs(new - exposure) + SHORT_FINANCING / 252 * max(0.0, -new)
        net = new * returns[t] - cost
        exposure = new
        equity *= 1 + net
        peak = max(peak, equity)
        if equity < peak * (1 - d['stop_loss']) and not frozen:
            frozen, peak = d['cooldown'], equity
        out.append(net)
        exposures.append(exposure)
    return out, exposures


def sharpe(daily):
    if len(daily) < 2:
        return 0.0
    mean = sum(daily) / len(daily)
    sd = math.sqrt(sum((r - mean) ** 2 for r in daily) / (len(daily) - 1))
    return mean / sd * math.sqrt(252) if sd > 1e-12 else 0.0


def max_drawdown(daily):
    equity = peak = 1.0
    worst = 0.0
    for r in daily:
        equity *= 1 + r
        peak = max(peak, equity)
        worst = min(worst, equity / peak - 1)
    return worst


def score(daily):
    """Sharpe minus a drawdown penalty: a smooth curve that hides a crash should not win."""
    return sharpe(daily) + DRAWDOWN_PENALTY * max_drawdown(daily)


def evaluate_genome(dna, assets, windows):
    """Mean score across assets, plus weekly returns (all assets concatenated) for correlation checks."""
    total, weekly = 0.0, []
    for name in assets:
        daily = backtest(dna, assets[name], *windows[name])[0]
        total += score(daily)
        weekly += [sum(daily[i:i + 5]) for i in range(0, len(daily) - 4, 5)]
    return total / len(assets), weekly


def fitness(dna, assets, windows):
    return evaluate_genome(dna, assets, windows)[0]


def standardize(values):
    mean = sum(values) / len(values)
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
    return [(v - mean) / sd for v in values] if sd > 1e-12 else [0.0] * len(values)


def correlation(a, b):
    """Pearson correlation of two already standardized vectors."""
    return sum(x * y for x, y in zip(a, b)) / len(a)


def reflect(value):
    """Mutation bounces off the [0, 1] walls instead of piling up on them."""
    value = abs(value) % 2
    return 2 - value if value > 1 else value


def encode(dna):
    return ''.join(ALPHABET[min(63, int(g * 64))] for g in dna)


def evolve(assets, train, validation, seed=7, population=120, generations=60, elite=4, immigrants=4,
           tournament=3, mutation_rate=0.12, mutation_scale=0.15, on_generation=None):
    """Tournament selection on a diversity-adjusted score, uniform crossover, reflected Gaussian mutation,
    elitism on the raw score and random immigrants."""
    rng = random.Random(seed)
    pool = [[rng.random() for _ in GENES] for _ in range(population)]
    history = []
    for generation in range(generations):
        evaluated = [(*evaluate_genome(dna, assets, train), dna) for dna in pool]
        evaluated.sort(key=lambda x: -x[0])
        leaders = [standardize(weekly) for _, weekly, _ in evaluated[:DIVERSITY_LEADERS]]
        adjusted = []
        for rank, (raw, weekly, dna) in enumerate(evaluated):
            z = standardize(weekly)
            # Penalise resembling a fitter leader: the population should not collapse onto one bet.
            above = leaders[:min(rank, DIVERSITY_LEADERS)]
            penalty = max((correlation(z, leader) for leader in above), default=0.0)
            adjusted.append((raw - DIVERSITY_PENALTY * max(0.0, penalty), dna))
        validation_scores = [fitness(dna, assets, validation) for _, _, dna in evaluated]
        genomes = [dna for _, _, dna in evaluated]
        record = {'generation': generation, 'train': [round(raw, 4) for raw, _, _ in evaluated],
                  'validation': [round(v, 4) for v in validation_scores],
                  'dna': [encode(dna) for dna in genomes],
                  'diversity': round(sum(spread(genomes, i) for i in range(len(GENES))) / len(GENES), 4)}
        history.append(record)
        if on_generation:
            on_generation(record)
        if generation == generations - 1:
            return history, genomes

        def pick():
            return max(rng.sample(adjusted, tournament), key=lambda x: x[0])[1]
        children = [dna[:] for dna in genomes[:elite]]
        children += [[rng.random() for _ in GENES] for _ in range(immigrants)]
        while len(children) < population:
            mother, father = pick(), pick()
            child = [m if rng.random() < 0.5 else f for m, f in zip(mother, father)]
            child = [reflect(g + rng.gauss(0, mutation_scale)) if rng.random() < mutation_rate else g for g in child]
            children.append(child)
        pool = children


def spread(genomes, index):
    values = [dna[index] for dna in genomes]
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def select_champions(genomes, assets, validation, count=5, max_correlation=0.5):
    """Greedy: best validation score first, then the best whose weekly validation returns stay below
    max_correlation in absolute value with every champion already chosen."""
    scored = sorted(((*evaluate_genome(dna, assets, validation), dna) for dna in genomes), key=lambda x: -x[0])
    chosen = []
    for value, weekly, dna in scored:
        z = standardize(weekly)
        if all(abs(correlation(z, other)) < max_correlation for _, other, _ in chosen):
            chosen.append((value, z, dna))
        if len(chosen) == count:
            break
    return [(value, dna) for value, _, dna in chosen]


def describe(dna):
    """Short human reading of a genome's dominant traits."""
    d = decode(dna)
    calm = sorted(zip(SIGNALS, d['calm']), key=lambda x: -abs(x[1]))[:2]
    traits = [f"{'+' if w > 0 else '-'}{name.replace('_', ' ')}" for name, w in calm]
    traits.append('long/short' if d['max_short'] > 0.3 else 'long-only')
    if d['vol_target_mix'] > 0.5:
        traits.append(f"vol target {d['vol_target']:.0%}")
    traits.append(f"stop {d['stop_loss']:.0%}")
    return ', '.join(traits)
