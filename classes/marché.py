import datetime
import random
import time
import yfinance as yf

def str_time_prop(start, end, time_format, prop):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%m/%d/%Y %I:%M %p', prop)

COMPANIES = [ 'AAPL', 'MFSF', 'MSFT', 'AMZN', 'GOOG' ]

class Marché:
    def __init__(self, nb_tours):
        #
        self.entreprise = random.choice(COMPANIES)
        
        # récupere les données d'un marché aléatoire dans les 30 à 30- nb_tours derniers jours
        self.endSampleDate = (datetime.datetime.now() - datetime.timedelta(days=nb_tours)).strftime('%m/%d/%Y %I:%M %p')
        self.startSampleDate = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%m/%d/%Y %I:%M %p')
        self.randomizedDate = datetime.datetime.strptime(random_date(self.startSampleDate, self.endSampleDate, random.random()), '%m/%d/%Y %I:%M %p') # Date aléatoire de début de simulation
        self.endSimulationDate = self.randomizedDate + datetime.timedelta(days=nb_tours) # Date de fin de simulation
        self.full_prix = yf.download(self.entreprise, start=self.randomizedDate, end=self.endSimulationDate, interval='1m').to_dict('records')
        
        self.prix_actuel = 0
        self.avancement = 0 # Avancement dans la liste de stock
        self.historique_prix = {}
    
    def choix_entreprise(self):
        self.entreprise = random.choice(COMPANIES)
    
    def get_prix_actuel(self):
        return self.prix_actuel
    
    def set_prix_actuel(self, nouveau_prix):
        self.historique_prix.append(self.prix_actuel) # On ajoute le prix actuel à l'historique
        self.prix_actuel = self.full_prix.iloc[self.avancement] # On récupère le prix actuel dans la liste de stock
        self.avancement += 1 # On incrémente l'avancement dans la liste de stock
    
    def get_historique_prix(self):
        return self.historique_prix