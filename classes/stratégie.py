from regret import Regret
from situation import Situation

class Stratégie:
    def __init__(self, nom):
        self.nom = nom
        self.rendements = []
        self.regrets = []
    
    def get_nom(self):
        return self.nom
    
    def get_rendements(self):
        return self.rendements
    
    def get_regrets(self):
        return self.regrets
    
    def jouer(self, marché):
        # Méthode abstraite à implémenter dans chaque stratégie
        pass
    
    def calculer_rendement(self, marché):
        # Calcul du rendement obtenu en jouant la stratégie sur le marché
        # Ajout du rendement à la liste des rendements
        rendement = marché.get_prix_actuel() - self.prix_achat
        self.rendements.append(rendement)
        return rendement

    def calculer_regret(self, marché, autres_stratégies):
        # Calcul du regret de ne pas avoir joué une autre stratégie plus rentable
        meilleur_rendement = max([strat.calculer_rendement(marché) for strat in autres_stratégies])
        regret = meilleur_rendement - self.calculer_rendement(marché)
        self.regrets.append(regret)
        return regret
