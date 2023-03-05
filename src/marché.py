import datetime
import random
import time
import yfinance as yf

class Marché:
    def __init__(self, nb_tours: int):
        self.entreprises = ['AAPL', 'MFSF', 'AMZN', 'GOOG']
        self.entreprise = random.choice(self.entreprises)

        self.endSampleDate = (datetime.datetime.now() - datetime.timedelta(days=nb_tours)).strftime('%m/%d/%Y %I:%M %p')
        self.startSampleDate = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%m/%d/%Y %I:%M %p')
        self.randomizedDate = datetime.datetime.strptime(random_date(self.startSampleDate, self.endSampleDate, random.random()), '%m/%d/%Y %I:%M %p')
        self.endSimulationDate = self.randomizedDate + datetime.timedelta( days=nb_tours)
        self.full_prix = yf.download(self.entreprise, start=self.randomizedDate, end=self.endSimulationDate, interval='1m').to_dict('records')

        self.prix_actuel = 0
        self.avancement = 0
        self.historique_prix = []

    def choix_entreprise(self):
        self.entreprise = random.choice(self.entreprises)

    def get_prix_actuel(self):
        return self.prix_actuel

    def set_prix_actuel(self):
        self.historique_prix.append(self.prix_actuel)
        self.prix_actuel = self.full_prix[self.avancement]
        self.avancement += 1

    def get_historique_prix(self):
        return self.historique_prix

    def simuler_ordres(self, ordres):
        if not ordres:
            return []
        for ordre in ordres:
            prix_actuel = self.get_prix_actuel()
            if ordre['type'] == 'achat' and ordre['prix'] >= prix_actuel:
                ordre['statut'] = 'refuse'
            elif ordre['type'] == 'vente' and ordre['prix'] <= prix_actuel:
                ordre['statut'] = 'refuse'
            else:
                ordre['statut'] = 'execute'
                
        prix = [ordre['prix'] for ordre in ordres if ordre['statut'] == 'execute']
        qtes = [ordre['quantite'] for ordre in ordres if ordre['statut'] == 'execute']
        return prix, qtes
    
def str_time_prop(start: datetime, end: datetime, time_format: str, prop: float) -> str:
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))


def random_date(start: datetime, end: datetime, prop: float) -> str:
    return str_time_prop(start, end, '%m/%d/%Y %I:%M %p', prop)