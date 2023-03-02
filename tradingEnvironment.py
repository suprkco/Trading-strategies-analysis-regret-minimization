import datetime
import os
import random
import time
import numpy as np
import pandas as pd
import yfinance as yf
from tradingStrategies import high_liquidity_strategy, low_liquidity_strategy, trend_following_strategy, high_risk_strategy, low_risk_strategy
import colorama

# https://pypi.org/project/yfinance/ 


# Initialisation de 100 traders equitablement répartis sur les stratégies
traderStrategy = ['high_liquidity_strategy', 'low_liquidity_strategy', 'trend_following_strategy', 'high_risk_strategy', 'low_risk_strategy']
traders = {}
tradersNumbers = 100
for i in range(tradersNumbers):
    traders['trader %i' % (i)] = {
        'strategy': traderStrategy[i%len(traderStrategy)], 
        'portfolio': {'AAPL': 0, 'MSFT': 0, 'GOOG': 0, 'AMZN': 0, 'FB': 0},
        'balance': 1_000_000,
    }


# Initialisation de l'environnement de trading
companies = ['AAPL', 'MSFT', 'GOOG', 'AMZN']


# Initialisation des paramètres de la simulation
generationMax = 10 # Nombre de fois que la simulation est lancée en supprimant les 5% des traders les moins performants
dayMax = 5 # nombre de jours de simulation par generation
errorRate = 0.05 # taux d'erreur de la simulation


# random date functions
def str_time_prop(start, end, time_format, prop):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%m/%d/%Y %I:%M %p', prop)


for generation in range(generationMax):
    currentDay = 0 # jour de la simulation
    
    
    intevaleStock = '1m' # 1s d'intervalle de temps entre chaque observation des stocks
    dateStart = (datetime.datetime.now() - datetime.timedelta(days=dayMax+1)).strftime('%m/%d/%Y %I:%M %p')
    dateEnd = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%m/%d/%Y %I:%M %p')
    # randomDate = datetime.datetime.strptime(random_date("1/1/2010 1:30 PM", "12/31/2019 4:50 AM", random.random()), '%m/%d/%Y %I:%M %p') # Date aléatoire de début de simulation (entre 2010 et 2019)
    randomDate = datetime.datetime.strptime(random_date(dateStart, dateEnd, random.random()), '%m/%d/%Y %I:%M %p') # Date aléatoire de début de simulation (entre 2010 et 2019)
    endDate = randomDate + datetime.timedelta(days=dayMax) # Date de fin de simulation
    
    
    stocks = {}
    for company in companies:
        stocksDataFrame = yf.download(company, start=randomDate, end=endDate, interval=intevaleStock) # get a pandas.core.frame.DataFrame object
        # decompose the dataframe into a list of dictionaries
        # {'Open': f, 'High': f, 'Low': f, 'Close': f, 'Adj Close': f, 'Volume': f}
        stocks[company] = stocksDataFrame.to_dict('records')
    
    stockIndex = 0
    
    # tant que le nombre de jours de simulation n'est pas atteint on acutalise le portefeuille de tout les traders
    while (currentDay < dayMax) & (stockIndex < len(stocks[company])):
        # initialisation des statistiques de la simulation, comptage des proportion de traders par stratégie
        stats = {
            'count': {
                'high_liquidity_strategy': 0, 
                'low_liquidity_strategy': 0, 
                'trend_following_strategy': 0, 
                'high_risk_strategy': 0, 
                'low_risk_strategy': 0
                }
            }
        
        # actualisation du stock considéré comme actuel
        for company in companies:
            currentStock = stocks[company][stockIndex]
            openPrice, highPrice, lowPrice, closePrice = currentStock['Open'], currentStock['High'], currentStock['Low'], currentStock['Close']
            adjustedClosePrice, volume = currentStock['Adj Close'], currentStock['Volume']
            
            # cration de l'objet stock
            stockParameters = {
                'openPrice': openPrice, 
                'highPrice': highPrice, 
                'lowPrice': lowPrice, 
                'closePrice': closePrice, 
                'adjustedClosePrice': adjustedClosePrice, 
                'volume': volume
                }
            
            # actualisation des portefeuilles
            for key, trader in traders.items():
                # actualisation du portefeuille de chaque trader de chaque société
                # stock_to_trade, quantity_to_trade = traders[key][]
                portfolio = trader['portfolio']
                balance = trader['balance']
                
                # call the strategy function
                strategyName = trader['strategy']
                stock_to_trade, quantity_to_trade = globals()[strategyName](portfolio, balance, stockParameters)
                
                # mise à jour des statistiques de la simulation
                if strategyName not in stats:
                    stats[strategyName] = {
                        'balance': 0,
                        'portfolio': {'AAPL': 0, 'MSFT': 0, 'GOOG': 0, 'AMZN': 0}
                    }
                    
                if stock_to_trade is not None:
                    # actualisation du portefeuille du trader
                    if stock_to_trade == company:
                        # si le trader a choisi de vendre
                        if quantity_to_trade < 0:
                            # s'il a assez d'actions dans son portefeuille
                            if portfolio[stock_to_trade] >= abs(quantity_to_trade):
                                # on vend
                                balance += (1 - errorRate) * abs(quantity_to_trade) * closePrice
                                portfolio[stock_to_trade] += quantity_to_trade
                            # sinon on vend tout ce qu'il a
                            else:
                                balance += (1 - errorRate) * portfolio[stock_to_trade] * closePrice
                                portfolio[stock_to_trade] = 0
                        # si le trader a choisi d'acheter
                        elif quantity_to_trade > 0:
                            # s'il a assez d'argent dans son compte
                            if balance >= (1 + errorRate) * quantity_to_trade * closePrice:
                                # on achète
                                balance -= (1 + errorRate) * quantity_to_trade * closePrice
                                portfolio[stock_to_trade] += quantity_to_trade
                            # sinon on achète le maximum d'actions possible
                            else:
                                portfolio[stock_to_trade] += int(balance / (1 + errorRate) / closePrice)
                                balance -= (1 + errorRate) * portfolio[stock_to_trade] * closePrice
                                
                    # mise à jour du portefeuille du trader
                    traders[key]['portfolio'] = portfolio
                    traders[key]['balance'] = balance
                # end if stock_to_trade is not None:
            # end for key, trader in traders.items():
        # end for company in companies:
        stockIndex += 1
        
        # parcours des traders pour calculer les statistiques de la simulation, net worth = balance + nonbre d'actions * prix de clôture
        for key, trader in traders.items():
            stats['count'][trader['strategy']] += 1
            
            strategy = trader['strategy']
            
            portfolio = trader['portfolio']
            balance = trader['balance']
            netWorth = balance
            
            for company in companies:
                netWorth += portfolio[company] * stocks[company][stockIndex]['Close']
            
            stats[strategy]['balance'] += balance
            stats[strategy]['portfolio'][company] += portfolio[company]
            stats[strategy]['netWorth'] = netWorth
            
        for key, value in stats['count'].items():
            stats['count'][key] = value / tradersNumbers * 100
    
        # affichage des résultats et des statistiques de la simulation
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Generation %i, Date: %s ,Jour %i/%i, traders proportions: %.1f/%.1f/%.1f/%.1f/%.1f' % (generation, randomDate, currentDay, dayMax, stats['count']['high_liquidity_strategy'], stats['count']['low_liquidity_strategy'], stats['count']['trend_following_strategy'], stats['count']['high_risk_strategy'], stats['count']['low_risk_strategy']))
        print('Moyenne des valeur nette, des balances & des portefeuilles:')
        
        high_liquidity_color = '\033[92m' if stats['high_liquidity_strategy']['balance'] >= stats['low_liquidity_strategy']['balance'] else '\033[91m'
        low_liquidity_color = '\033[92m' if stats['low_liquidity_strategy']['balance'] >= stats['high_liquidity_strategy']['balance'] else '\033[91m'
        trend_following_color = '\033[92m' if stats['trend_following_strategy']['balance'] >= stats['high_liquidity_strategy']['balance'] else '\033[91m'
        high_risk_color = '\033[92m' if stats['high_risk_strategy']['balance'] >= stats['high_liquidity_strategy']['balance'] else '\033[91m'
        low_risk_color = '\033[92m' if stats['low_risk_strategy']['balance'] >= stats['high_liquidity_strategy']['balance'] else '\033[91m'

        print('Strategie de haute liquidité, net worth: %s%.1f\033[0m $, balance: %.1f $, portefeuille moyens: %.1f/%.1f/%.1f/%.1f' % (high_liquidity_color, stats['high_liquidity_strategy']['netWorth'], stats['high_liquidity_strategy']['balance'], stats['high_liquidity_strategy']['portfolio']['AAPL'], stats['high_liquidity_strategy']['portfolio']['MSFT'], stats['high_liquidity_strategy']['portfolio']['GOOG'], stats['high_liquidity_strategy']['portfolio']['AMZN']))
        print('Strategie de basse liquidité, net worth: %s%.1f\033[0m $, balance: %.1f $, portefeuille moyens: %.1f/%.1f/%.1f/%.1f' % (low_liquidity_color, stats['low_liquidity_strategy']['netWorth'], stats['low_liquidity_strategy']['balance'], stats['low_liquidity_strategy']['portfolio']['AAPL'], stats['low_liquidity_strategy']['portfolio']['MSFT'], stats['low_liquidity_strategy']['portfolio']['GOOG'], stats['low_liquidity_strategy']['portfolio']['AMZN']))
        print('Strategie de suivi de tendance, net worth: %s%.1f\033[0m $, balance: %.1f $, portefeuille moyens: %.1f/%.1f/%.1f/%.1f' % (trend_following_color, stats['trend_following_strategy']['netWorth'], stats['trend_following_strategy']['balance'], stats['trend_following_strategy']['portfolio']['AAPL'], stats['trend_following_strategy']['portfolio']['MSFT'], stats['trend_following_strategy']['portfolio']['GOOG'], stats['trend_following_strategy']['portfolio']['AMZN']))
        print('Strategie à haut risque, net worth: %s%.1f\033[0m $, balance: %.1f $, portefeuille moyens: %.1f/%.1f/%.1f/%.1f' % (high_risk_color, stats['high_risk_strategy']['netWorth'], stats['high_risk_strategy']['balance'], stats['high_risk_strategy']['portfolio']['AAPL'], stats['high_risk_strategy']['portfolio']['MSFT'], stats['high_risk_strategy']['portfolio']['GOOG'], stats['high_risk_strategy']['portfolio']['AMZN']))
        print('Strategie à bas risque, net worth: %s%.1f\033[0m $, balance: %.1f $, portefeuille moyens: %.1f/%.1f/%.1f/%.1f' % (low_risk_color, stats['low_risk_strategy']['netWorth'], stats['low_risk_strategy']['balance'], stats['low_risk_strategy']['portfolio']['AAPL'], stats['low_risk_strategy']['portfolio']['MSFT'], stats['low_risk_strategy']['portfolio']['GOOG'], stats['low_risk_strategy']['portfolio']['AMZN']))
