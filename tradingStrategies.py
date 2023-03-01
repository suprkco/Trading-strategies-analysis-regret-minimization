import numpy as np

# Stratégie de liquidité élevée :
def high_liquidity_strategy(volume, price, daily_volume, support, resistance, volatility):
    max_liquidity = daily_volume * 0.05
    limit_price = support + (resistance - support) * 0.25
    if volume <= max_liquidity and price <= limit_price + volatility:
        return 'buy'
    elif volume <= max_liquidity and price >= limit_price - volatility:
        return 'sell'
    else:
        return 'hold'

# Stratégie de liquidité faible :
def low_liquidity_strategy(volume, price, daily_volume, target_price):
    max_quantity = 100
    if price <= target_price:
        return 'buy', min(max_quantity, int(max_quantity * (target_price - price) / target_price))
    elif price >= target_price:
        return 'sell', min(max_quantity, int(max_quantity * (price - target_price) / target_price))
    else:
        return 'hold', 0

# Stratégie de réaction rapide :
def fast_reaction_strategy(volume, price, daily_volume, volatility):
    if price >= price + volatility:
        return 'sell'
    elif price <= price - volatility:
        return 'buy'
    else:
        return 'hold'
    
# Stategie de suivie de tendance :
def trend_following_strategy(prices, window_size):
    if len(prices) < window_size:
        return 'hold'

    returns = np.diff(prices) / prices[:-1]
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    threshold = mean_return - 2 * std_return

    if returns[-1] < threshold:
        return 'sell'
    elif returns[-1] > threshold:
        return 'buy'
    else:
        return 'hold'

# Stratégie de prise de risque élevée :
def high_risk_strategy(volume, price, daily_volume, support, resistance, volatility):
    limit_price = support + (resistance - support) * 0.75
    if price >= limit_price:
        return 'buy'
    elif price <= support:
        return 'sell'
    else:
        return 'hold'

# Stratégie de prise de risque faible :
def low_risk_strategy(volume, price, daily_volume, support, resistance, volatility):
    limit_price = support + (resistance - support) * 0.25
    if price >= limit_price:
        return 'sell'
    elif price <= support:
        return 'buy'
    else:
        return 'hold'