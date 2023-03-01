import numpy as np

# Stratégie de liquidité élevée :
def high_liquidity_strategy(portfolio, balance, price, daily_volume, support, resistance, volatility):
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
def low_liquidity_strategy(portfolio, balance, price, daily_volume, target_price):
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
def fast_reaction_strategy(portfolio, balance, price, daily_volume, volatility):
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

# Stratégie de suivi de tendance :
def trend_following_strategy(portfolio, balance, price, daily_volume, support, resistance, volatility):
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


# Stratégie de risque élevé :
def high_risk_strategy(portfolio, balance, price, daily_volume, support, resistance, volatility):
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


# Stratégie de risque faible :
def low_risk_strategy(portfolio, balance, price, daily_volume, support, resistance, volatility):
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
