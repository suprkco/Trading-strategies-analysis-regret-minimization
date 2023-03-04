import datetime
import random
import time
import yfinance as yf


def str_time_prop(start: datetime, end: datetime, time_format: str, prop: float) -> str:
    """
    Récupère une date aléatoire entre deux dates et retourne une date au format str

    :param start datetime: date de début
    :param end datetime: date de fin
    :param time_format str: format de la date
    :param prop float: proportion de la date
    :return str: date aléatoire
    """
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(time_format, time.localtime(ptime))


def random_date(start: datetime, end: datetime, prop: float) -> str:
    """
    Récupère une date aléatoire entre deux dates
    
    :param start datetime: date de début
    :param end datetime: date de fin
    :param prop float: proportion de la date
    :return str: date aléatoire
    """
    return str_time_prop(start, end, '%m/%d/%Y %I:%M %p', prop)


COMPANIES = ['AAPL', 'MFSF', 'AMZN', 'GOOG']


class Marché:
    """
    Classe représentant le marché

    Attributs :
        entreprise :            entreprise du marché
        endSampleDate :         date de fin de l'échantillon
        startSampleDate :       date de début de l'échantillon
        randomizedDate :        date aléatoire
        endSimulationDate :     date de fin de la simulation
        full_prix :             liste des prix de l'entreprise
        prix_actuel :           prix actuel de l'entreprise
        avancement :            avancement de la simulation
        historique_prix :       historique des prix de l'entreprise
    
    Méthodes :
        choix_entreprise :          change l'entreprise du marché
        get_prix_actuel :           retourne le prix actuel de l'entreprise
        set_prix_actuel :           change le prix actuel de l'entreprise
        get_historique_prix :       retourne l'historique des prix de l'entreprise
        simuler_ordres :            simule les ordres du joueur
    """
    def __init__(self, nb_tours: int):
        """
        Initialise le marché

        :param nb_tours int: nombre de tours de la simulation
        """
        self.entreprise = random.choice(COMPANIES)

        self.endSampleDate = (datetime.datetime.now() - datetime.timedelta(days=nb_tours)).strftime('%m/%d/%Y %I:%M %p')
        self.startSampleDate = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%m/%d/%Y %I:%M %p')
        self.randomizedDate = datetime.datetime.strptime(random_date(self.startSampleDate, self.endSampleDate, random.random()), '%m/%d/%Y %I:%M %p')
        self.endSimulationDate = self.randomizedDate + datetime.timedelta( days=nb_tours)
        self.full_prix = yf.download(self.entreprise, start=self.randomizedDate, end=self.endSimulationDate, interval='1m').to_dict('records')

        self.prix_actuel = 0
        self.avancement = 0
        self.historique_prix = []

    def choix_entreprise(self):
        """
        Change l'entreprise du marché
        """
        self.entreprise = random.choice(COMPANIES)

    def get_prix_actuel(self) -> float:
        """
        Retourne le prix actuel de l'entreprise
        """
        return self.prix_actuel

    def set_prix_actuel(self):
        """
        Change le prix actuel de l'entreprise
        """
        self.historique_prix.append(self.prix_actuel)
        self.prix_actuel = self.full_prix[self.avancement]['Close']
        self.avancement += 1

    def get_historique_prix(self) -> list:
        """
        Retourne l'historique des prix de l'entreprise
        
        :return list: historique des prix
        """
        return self.historique_prix

    def simuler_ordres(self, ordres: list) -> list:
        """
        Simule les ordres et retourne les ordres exécutés
        
        :param ordres list: ordres à simuler
        :return list: ordres exécutés
        """
        if not ordres:
            return []
        for ordre in ordres:
            prix_actuel = self.get_prix_actuel()
            if ordre['type'] == 'achat' and ordre['prix'] >= prix_actuel:
                ordre['statut'] = 'refusé'
            elif ordre['type'] == 'vente' and ordre['prix'] <= prix_actuel:
                ordre['statut'] = 'refusé'
            else:
                ordre['statut'] = 'refusé'
                
        prix = [ordre['prix'] for ordre in ordres if ordre['statut'] == 'exécuté']
        qtes = [ordre['quantité'] for ordre in ordres if ordre['statut'] == 'exécuté']
        return prix, qtes
