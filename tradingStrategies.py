import numpy as np

# 'portfolio': {'AAPL': 0, 'MSFT': 0, 'GOOG': 0, 'AMZN': 0, 'FB': 0}
# stockParameters = {'openPrice': openPrice, 'highPrice': highPrice, 'lowPrice': lowPrice, 'closePrice': closePrice, 'adjustedClosePrice': adjustedClosePrice, 'volume': volume}'}

# Fonction pour calculer la moyenne mobile exponentielle
def calculate_EMA(df, period=20, column='Close'):
    return df[column].ewm(span=period, adjust=False).mean()


# Fonction pour calculer le RSI
def calculate_RSI(df, period=14, column='Close'):
    delta = df[column].diff()
    up = delta.where(delta > 0, 0)
    down = -delta.where(delta < 0, 0)
    ema_up = up.ewm(com=period-1, min_periods=period).mean()
    ema_down = down.ewm(com=period-1, min_periods=period).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))


# Stratégie de liquidité élevée :
def high_liquidity_strategy(portfolio, balance, stockParameters):
    price = stockParameters['closePrice']
    daily_volume = stockParameters['volume']
    support = stockParameters['lowPrice']
    resistance = stockParameters['highPrice']
    volatility = (resistance - support) * 0.25
    
    max_liquidity = daily_volume * 0.05
    limit_price = support + (resistance - support) * 0.25
    stock_to_trade = None
    quantity_to_trade = 0
    
    for stock in portfolio:
        volume = portfolio[stock]
        if volume == 0:
            continue
        if volume <= max_liquidity and price <= limit_price + volatility:
            max_buy_quantity = int(balance / price)
            quantity = min(max_buy_quantity, int(balance * 0.25 / price))
            if quantity > 0:
                stock_to_trade = stock
                quantity_to_trade = quantity
                break
        elif volume <= max_liquidity and price >= limit_price - volatility:
            if balance > 0:
                quantity = min(balance, int(balance * 0.25 / price))
                if quantity > 0:
                    stock_to_trade = stock
                    quantity_to_trade = -quantity
                    break
        else:
            continue
    
    return stock_to_trade, quantity_to_trade


# Stratégie de liquidité faible :
def low_liquidity_strategy(portfolio, balance, stockParameters):
    price = stockParameters['closePrice']
    target_Price = stockParameters['openPrice']
    
    max_quantity = 100
    stock_to_trade = None
    quantity_to_trade = 0
    
    for stock in portfolio:
        volume = portfolio[stock]
        if volume == 0:
            continue
        if price <= target_price:
            max_buy_quantity = int(balance / price)
            quantity = min(max_buy_quantity, max_quantity)
            if quantity > 0:
                stock_to_trade = stock
                quantity_to_trade = quantity
                break
        elif price >= target_price:
            max_sell_quantity = volume
            quantity = min(max_sell_quantity, max_quantity)
            if quantity > 0:
                stock_to_trade = stock
                quantity_to_trade = -quantity
                break
        else:
            continue
    
    return stock_to_trade, quantity_to_trade


# Stratégie de réaction rapide :
def fast_reaction_strategy(portfolio, balance, stockParameters):
    price = stockParameters['closePrice']
    daily_volume = stockParameters['volume']
    volatility = stockParameters['highPrice'] - stockParameters['lowPrice']
    
    max_quantity = int(balance / price)
    stock_to_trade = None
    quantity_to_trade = 0
    
    if price >= price + volatility:
        for stock in portfolio:
            volume = portfolio[stock]
            if volume == 0:
                continue
            if balance > 0:
                stock_to_trade = stock
                quantity_to_trade = -max_quantity
                break
    elif price <= price - volatility:
        for stock in portfolio:
            volume = portfolio[stock]
            if volume == 0:
                continue
            max_buy_quantity = int(balance / price)
            quantity = min(max_buy_quantity, max_quantity)
            if quantity > 0:
                stock_to_trade = stock
                quantity_to_trade = quantity
                break
    else:
        pass
    
    return stock_to_trade, quantity_to_trade


# Stategie de suivie de tendance :
def trend_following_strategy(portfolio, balance, stockParameters):
    price = stockParameters['closePrice']
    daily_volume = stockParameters['volume']
    support = stockParameters['lowPrice']
    resistance = stockParameters['highPrice']
    volatility = resistance - support
    
    stock_to_trade = None
    quantity_to_trade = 0
    
    if price > resistance + volatility:
        for stock in portfolio:
            if portfolio[stock] > 0:
                stock_to_trade = stock
                quantity_to_trade = -portfolio[stock]
                break
    elif price < support - volatility:
        max_buy_quantity = int(balance / price)
        quantity = min(max_buy_quantity, int(balance * 0.25 / price))
        for stock in portfolio:
            if portfolio[stock] == 0 and quantity > 0:
                stock_to_trade = stock
                quantity_to_trade = quantity
                break
    
    return stock_to_trade, quantity_to_trade


# Stratégie de prise de risque élevée :
def high_risk_strategy(portfolio, balance, stockParameters):
    price = stockParameters['closePrice']
    daily_volume = stockParameters['volume']
    support = stockParameters['lowPrice']
    resistance = stockParameters['highPrice']
    volatility = resistance - support
    
    stock_to_trade = None
    quantity_to_trade = 0
    
    for stock in portfolio:
        if portfolio[stock] > 0:
            stock_to_trade = stock
            quantity_to_trade = -portfolio[stock]
            break
    
    if stock_to_trade is None:
        max_buy_quantity = int(balance / price)
        quantity = min(max_buy_quantity, int(balance * 0.25 / price))
        for stock in portfolio:
            if portfolio[stock] == 0 and quantity > 0:
                stock_to_trade = stock
                quantity_to_trade = quantity
                break
    
    return stock_to_trade, quantity_to_trade


# Stratégie de prise de risque faible :
def low_risk_strategy(portfolio, balance, stockParameters):
    price = stockParameters['closePrice']
    daily_volume = stockParameters['volume']
    support = stockParameters['lowPrice']
    resistance = stockParameters['highPrice']
    volatility = resistance - support
    
    max_liquidity = daily_volume * 0.05
    limit_price = support + (resistance - support) * 0.25
    stock_to_trade = None
    quantity_to_trade = 0
    
    for stock in portfolio:
        volume = portfolio[stock]
        if volume == 0:
            continue
        if volume <= max_liquidity and price <= limit_price + volatility:
            max_buy_quantity = int(balance / price)
            quantity = min(max_buy_quantity, int(balance * 0.25 / price))
            if quantity > 0:
                stock_to_trade = stock
                quantity_to_trade = quantity
                break
        elif volume <= max_liquidity and price >= limit_price - volatility:
            if balance > 0:
                quantity = min(balance, int(balance * 0.25 / price))
                if quantity > 0:
                    stock_to_trade = stock
                    quantity_to_trade = -quantity
                    break
        else:
            continue
    
    return stock_to_trade, quantity_to_trade