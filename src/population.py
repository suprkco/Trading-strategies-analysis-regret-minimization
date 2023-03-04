from stratégie import Stratégie
from joueur import Joueur
import random

class Population:
    def __init__(self, taille: int, nb_strategies: int, poids: float):
        self.taille = taille
        self.nb_strategies = nb_strategies
        self.poids = poids
        self.strategies = [Stratégie("Strategie {}".format(i), self.poids) for i in range(self.nb_strategies)]
        self.joueurs = [Joueur("Joueur {}".format(i), self.nb_strategies, self.strategies) for i in range(self.taille)]
        self.meilleures_strategies = []
        self.individus = []
        self.init_strategies()

    def get_taille(self) -> int:
        return self.taille

    def get_strategies(self) -> list:
        return self.strategies

    def ajouter_strategie(self, strategie: list):
        self.strategies.append(strategie)

    def init_strategies(self):
        for i in range(self.taille):
            nomJoueur = "Joueur " + str(i)
            joueur = Joueur(nomJoueur, self.nb_strategies, self.strategies)
            self.ajouter_strategie(joueur)

    def jouer_tous(self, marché):
        for strat in self.strategies:
            for joueur in strat.get_joueurs():
                ordres = joueur.generer_ordres(marché)
                marché.execute_ordres(ordres, joueur.get_nom())
                joueur.ajouter_rendement(marché.get_prix_actuel())

    def trier_strategies(self):
        self.strategies = sorted(self.strategies, key=lambda x: sum([joueur.get_rendements()[-1] for joueur in x.get_joueurs()])/len(x.get_joueurs()), reverse=True)

    def selectionner(self):
        self.trier_strategies()
        self.meilleures_strategies = self.strategies[:int(self.taille/2)]
        self.strategies = []
        for strat in self.meilleures_strategies:
            self.strategies.append(strat)
            clone = strat.clone()
            clone.muter()
            self.strategies.append(clone)
            
    def get_meilleure_strategie(self):
        self.trier_strategies()
        return self.strategies[0]
    
    def get_joueurs(self, strat: Stratégie) -> list:
        return [joueur for joueur in self.joueurs if joueur.strategies == strat]

    def selectionner_meilleures_strategies(self, pourcentage: float):
        nb_strategies = int(self.taille * pourcentage)
        self.meilleures_strategies = self.strategies[:nb_strategies]
        self.individus = [strat for strat in self.meilleures_strategies]

    def reproduire(self):
        nouvelle_generation = Population(self.taille, self.nb_strategies)
        for i in range(self.taille):
            parents = random.sample(self.meilleures_strategies, 2)
            enfant = self.croisement(parents[0], parents[1])
            nouvelle_generation.ajouter_strategie(enfant)
        return nouvelle_generation

    def croisement(self, parent1, parent2):
        point_de_croisement = random.randint(1, self.nb_strategies-1)
        enfant_strategie = parent1.get_strategie()[:point_de_croisement] + parent2.get_strategie()[point_de_croisement:]
        enfant = Joueur(parent1.get_nom(), self.nb_strategies)
        enfant.set_strategie(enfant_strategie)
        return enfant
