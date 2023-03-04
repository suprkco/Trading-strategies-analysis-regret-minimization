import random

class Joueur:
    def __init__(self, nom: str, nb_strategies: int, strategies: int):
        self.nom = nom
        self.nb_strategies = nb_strategies
        self.strategies = strategies
        self.rendements = []

    def get_nom(self) -> str:
        return self.nom

    def ajouter_rendement(self, rendement: float):
        self.rendements.append(rendement)

    def get_rendements(self) -> list:
        return self.rendements

    def changer_strategie(self):
        if self.strategies:
            self.strategie = random.choice(self.strategies)

    def generer_ordres_joueur(self, marché):
        ordres = []
        for i in range(self.nb_strategies):
            if i != self.strategies:
                qte = random.randint(1, 10)
                prix = random.uniform(marché.get_prix_min(), marché.get_prix_max())
                ordres.append((self.nom, i, qte, prix))
        return ordres
