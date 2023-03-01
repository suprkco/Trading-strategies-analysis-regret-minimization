import datetime
import random
import threading
import time
import numpy as np
import yfinance as yf
from tradingStrategies import high_liquidity_strategy, low_liquidity_strategy, fast_reaction_strategy, trend_following_strategy, high_risk_strategy, low_risk_strategy

# Initialisation de 100 traders equitablement répartis sur les stratégies
traderStrategy = ['high_liquidity_strategy', 'low_liquidity_strategy', 'fast_reaction_strategy', 'trend_following_strategy', 'high_risk_strategy', 'low_risk_strategy']
traders = {}
tradersNumbers = 100
for i in range(tradersNumbers):
    traders['trader'+i] = {
        'strategy': traderStrategy[i%len(traderStrategy)], 
        'portfolio': {'AAPL': 0, 'MSFT': 0, 'GOOG': 0, 'AMZN': 0, 'FB': 0},
        'balance': 1_000_000,
        }

# Initialisation de l'environnement de trading
companies = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'FB']

# Initialisation des paramètres de la simulation
generationMax = 100 # Nombre de fois que la simulation est lancée en supprimant les 5% des traders les moins performants
dayMax = 10 # nombre de jours de simulation par generation

def str_time_prop(start, end, time_format, prop):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))

def random_date(start, end, prop):
    return str_time_prop(start, end, '%m/%d/%Y %I:%M %p', prop)

def stockData(company, start, end, interval):
    return yf.download(company, start=start, end=end, interval=interval)

for generation in range(generationMax):
    currentDay = 0 # jour de la simulation
    intevaleStock = 1 # 1s d'intervalle de temps entre chaque observation des stocks
    endStockData = random_date("1/1/2010 1:30 PM", "12/31/2019 4:50 AM", random.random()) # Date aléatoire de début de simulation (entre 2010 et 2019)
    
    # Initialisation des stocks de toute les sociétés en initialisant leurs valeurs avec un mois de données
    startStockData = datetime.datetime.strptime(endStockData, '%m/%d/%Y %I:%M %p') - datetime.timedelta(days=30)
    stocks = {}
    
    # tant que le nombre de jours de simulation n'est pas atteint on acutalise le portefeuille de tout les traders
    while currentDay < dayMax :
        
        # Initialisation des outils et des données de trading
        price, daily_volume, volume, trend, volatility = {}, {}, {}, {}, {}
        window_size = 30 # taille de la fenêtre de temps pour calculer la volatilité et la tendance
            
        # verifie si les stocks sont ouverts
        if startStockData.hour == 9 and startStockData.minute == 30 and startStockData.second == 0:
            for company in companies:
                stocks[company] = yf.download(company, start=startStockData, end=endStockData, interval=intevaleStock)
                # calculs, recuperation des données de trading de chaque société
                price[company] = stocks[company]['Adj Close']
                daily_volume[company] = stocks[company]['Volume']
                volume[company] = daily_volume[company].rolling(window=window_size).mean()
                trend[company] = price[company].rolling(window=window_size).mean()
                volatility[company] = price[company].rolling(window=window_size).std()
            
            # actualisation des portefeuilles
            for trader in traders:
                # actualisation du portefeuille de chaque trader
                for company in companies:
                    # actualisation du portefeuille de chaque trader de chaque société
                    stock_to_trade, quantity_to_trade = traders[trader]['strategy'](stocks[company], traders[trader]['portfolio'][company], traders[trader]['balance'])
                    # TODO: actualisation du portefeuille de chaque trader de chaque société
                    # ATTENTION penser à bien verifier les parametres passé à la fonction de trading, certain outils de trading peuvent avoir été oublié
                        
        
        # actualisation des stocks
        startStockData = datetime.datetime.strptime(startStockData, '%m/%d/%Y %I:%M %p') + datetime.timedelta(seconds=1) # on avance d'une seconde
        endStockData = datetime.datetime.strptime(endStockData, '%m/%d/%Y %I:%M %p') + datetime.timedelta(seconds=1) # on avance d'uune seconde
        
        if startStockData.hour == 9 and startStockData.minute == 30 and startStockData.second == 0:
            currentDay += 1
            print('Day', currentDay)