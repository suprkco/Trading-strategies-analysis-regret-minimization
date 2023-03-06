import random

class Joueur:
    def __init__(self, nom: str, strategie):
        self.nom = nom
        self.strategie = strategie
        self.capital = 1000 # $
        self.capital_depart = self.capital
        self.actions = 0 # N°
        self.rendements = []

    def get_nom(self) -> str:
        return self.nom
    
    def get_strategie(self):
        return self.strategie
    
    def get_capital(self) -> float:
        return self.capital
    
    def get_capital_depart(self) -> float:
        return self.capital_depart
    
    def get_actions(self) -> int:
        return self.actions
    
    def get_rendements(self) -> list:
        return self.rendements
    
    def get_total_capital(self, marché) -> float:
        return self.capital + self.actions * marché.get_prix_actuel()['Close']

    def ajouter_rendement(self, rendement: float):
        self.rendements.append(rendement)
    
    def jouer(self, marché):
        return self.strategie.jouer(marché, self.capital)
    
    def acheter(self, marché, prix: float, quantite: int):
        self.capital -= prix
        self.actions += quantite
        
    def vendre(self, marché, prix: float, quantite: int):
        self.capital += prix
        self.actions -= quantite

    def generer_ordres_joueur(self, marché) -> list:
        pass
