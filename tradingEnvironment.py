import threading
import time
import numpy as np
import yfinance as yf
from tradingStrategies import high_liquidity_strategy, low_liquidity_strategy, fast_reaction_strategy, trend_following_strategy, high_risk_strategy, low_risk_strategy

class TradingEnvironment:
    def __init__(self, stock_symbol, start_date, end_date, initial_cash, max_quantity, strategy_weights):
        self.stock_symbol = stock_symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_cash = initial_cash
        self.max_quantity = max_quantity
        self.strategy_weights = strategy_weights

        self.stock_data = yf.download(stock_symbol, start=start_date, end=end_date)
        self.stock_data['Volume'] = self.stock_data['Volume'].fillna(0)
        self.stock_data['Daily Volume'] = self.stock_data['Volume'].rolling(window=20).mean()

        self.commissions = 0.01 # 1%
        self.cash = initial_cash
        self.shares = 0
        self.portfolio_value = initial_cash

    def get_support_resistance(self):
        highs = self.stock_data['High'].rolling(window=20).max()
        lows = self.stock_data['Low'].rolling(window=20).min()
        return lows.iloc[-1], highs.iloc[-1]

    def run_trading(self):
        t1 = threading.Thread(target=self.monitor_trading)
        t1.start()

    def monitor_trading(self):
        for i in range(len(self.stock_data)):
            current_price = self.stock_data['Close'][i]
            current_volume = self.stock_data['Volume'][i]
            daily_volume = self.stock_data['Daily Volume'][i]

            support, resistance = self.get_support_resistance()
            volatility = np.std(self.stock_data['Close'][i-20:i])

            signals = {}

            signals['high_liquidity_strategy'] = high_liquidity_strategy(current_volume, current_price, daily_volume, support, resistance, volatility)
            signals['low_liquidity_strategy'] = low_liquidity_strategy(current_volume, current_price, daily_volume, current_price * 0.99)
            signals['fast_reaction_strategy'] = fast_reaction_strategy(current_volume, current_price, daily_volume, volatility)
            signals['trend_following_strategy'] = trend_following_strategy(self.stock_data['Close'][:i], window_size=20)
            signals['high_risk_strategy'] = high_risk_strategy(current_volume, current_price, daily_volume, support, resistance, volatility)
            signals['low_risk_strategy'] = low_risk_strategy(current_volume, current_price, daily_volume, support, resistance, volatility)

            strategy_scores = {}
            for strategy, signal in signals.items():
                if signal == 'buy':
                    strategy_scores[strategy] = current_price / daily_volume
                elif signal == 'sell':
                    strategy_scores[strategy] = -current_price / daily_volume
                else:
                    strategy_scores[strategy] = 0

            weights_sum = sum(self.strategy_weights.values())
            weighted_scores = {strategy: score * (self.strategy_weights[strategy] / weights_sum) for strategy, score in strategy_scores.items()}
            best_strategy = max(weighted_scores, key=weighted_scores.get)

            if signals[best_strategy] == 'buy':
                quantity = min(int(self.cash / current_price), self.max_quantity)
                self.shares += quantity
                self.cash -= quantity * current_price * (1 + self.commissions)
            elif signals[best_strategy] == 'sell':
                quantity = min(self.shares, self.max_quantity)
                self.shares -= quantity
                self.cash += quantity * current_price * (1 - self.commissions)

class Trader():
    def init(self, name, strategy, capital):
        self.name = name
        self.strategy = strategy
        self.capital = capital
        self.portfolio = {}
        self.history = []
    def execute_trade(self, symbol, action, quantity, price):
        if action == 'buy':
            self.capital -= quantity * price
            if symbol in self.portfolio:
                self.portfolio[symbol] += quantity
            else:
                self.portfolio[symbol] = quantity
        elif action == 'sell':
            self.capital += quantity * price
            self.portfolio[symbol] -= quantity

        trade = {
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'price': price,
            'datetime': pd.Timestamp.now(),
            'capital': self.capital,
            'portfolio': self.portfolio.copy()
        }
        self.history.append(trade)

    def update(self, symbol, price):
        volume = int(yf.Ticker(symbol).info['volume'])
        daily_volume = yf.download(symbol, period='1d')['Volume'][-1]
        support = yf.Ticker(symbol).info['regularMarketDayLow']
        resistance = yf.Ticker(symbol).info['regularMarketDayHigh']
        volatility = yf.Ticker(symbol).info['regularMarketVolatility']
        target_price = yf.Ticker(symbol).info['regularMarketPrice'] * 1.05

        action, quantity = self.strategy(volume, price, daily_volume, support, resistance, volatility, target_price)

        if action != 'hold' and quantity > 0:
            self.execute_trade(symbol, action, quantity, price)

class TradingEnvironment:
    def init(self, symbols, traders):
        self.symbols = symbols
        self.traders = traders
    def update_traders(self):
        threads = []
        for symbol in self.symbols:
            data = yf.download(symbol, period='1d')
            price = data['Close'][-1]
            for trader in self.traders:
                thread = threading.Thread(target=trader.update, args=(symbol, price))
                threads.append(thread)
                thread.start()
        for thread in threads:
            thread.join()

    def run(self, days):
        for i in range(days):
            self.update_traders()

# Initialisation de 100 traders equitably répartis sur les stratégies
traderStrategy = ['high_liquidity_strategy', 'low_liquidity_strategy', 'fast_reaction_strategy', 'trend_following_strategy', 'high_risk_strategy', 'low_risk_strategy']
traders = []
number_of_traders = 100
for i in range(number_of_traders):
    traders.append(Trader('Trader ' + str(i), traderStrategy[i%len(traderStrategy)], 1000))

# Initialisation de l'environnement de trading
symbols = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'FB']
trading_environment = TradingEnvironment(symbols, traders)

# Lancement de la simulation de trading pour 10 jours

trading_environment.run(10)

# Affichage de l'historique des trades de chaque trader
for trader in traders:
    print(trader.name)
    for trade in trader.history:
        print(trader.name, trade)
        
        