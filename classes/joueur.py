import random
from stratégie import Stratégie

class Joueur:
    def __init__(self, nom, nb_strategies, strategies):
        self.nom = nom
        self.nb_strategies = nb_strategies
        self.strategies = strategies
        self.rendements = []
        self.strategie = random.choice(self.strategies)

    def get_nom(self):
        return self.nom

    def ajouter_rendement(self, rendement):
        self.rendements.append(rendement)

    def get_rendements(self):
        return self.rendements

    def changer_strategie(self):
        self.strategie = random.choice(self.strategies)
        
    def generer_ordres(self, marché):
        ordres = []
        if self.strategie == "strategie1":
            # ...
            pass
        elif self.strategie == "strategie2":
            # ...
            pass
        return ordres
