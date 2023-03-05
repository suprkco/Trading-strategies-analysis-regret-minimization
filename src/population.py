import random
from typing import List
from joueur import Joueur
from stratégie import Strategie


class Population:
    def __init__(self, nb_joueurs: int):
        self.joueurs = []
        self.nb_strategies = 3
        self.nb_joueurs = nb_joueurs

        # Création des joueurs
        for i in range(nb_joueurs):
            # On attribue une stratégie aléatoire à chaque joueur
            seed = [random.randint(0, 2**32-1) for _ in range(4)]
            strat = Strategie("Strategie {}".format(i%self.nb_strategies), seed)
            joueur = Joueur(str(i+1), strat)
            self.joueurs.append(joueur)
            strat.set_joueur(joueur)

    def get_joueurs(self) -> List[Joueur]:
        return self.joueurs

    def selectionner(self) -> None:
        """
        Sélectionne les 50% des joueurs les plus performants et recrée la population en mélangeant
        les joueurs sélectionnées.
        """
        nb_joueurs_a_selectionner = int(self.nb_joueurs / 2)
        self.joueurs = sorted(self.joueurs, key=lambda joueur: joueur.get_score(), reverse=True)
        self.joueurs = self.joueurs[:nb_joueurs_a_selectionner]
        new_population = []
        while len(new_population) < self.nb_joueurs:
            random.shuffle(self.joueurs)
            new_population.extend(self.joueurs[:nb_joueurs_a_selectionner])
        self.joueurs = new_population
        

    def get_meilleure_strategie(self) -> Strategie:
        """
        Retourne la meilleure stratégie de la population actuelle.
        """
        return max([joueur.get_strategie() for joueur in self.joueurs], key=lambda strat: strat.get_score())