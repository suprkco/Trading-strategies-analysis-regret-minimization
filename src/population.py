from stratégie import Stratégie
from joueur import Joueur
import random

class Population:
    def __init__(self, taille: int, nb_strategies: int, poids: float):
        """
        Initialise une population de joueurs

        :param taille int: taille de la population
        :param nb_strategies int: nombre de stratégies de chaque joueur
        :param poids float: poids de chaque stratégie
        """
        self.taille = taille
        self.nb_strategies = nb_strategies
        self.poids = poids
        self.strategies = [Stratégie("Strategie {}".format(i), self.poids) for i in range(self.nb_strategies)]
        self.joueurs = [Joueur("Joueur {}".format(i), self.nb_strategies, self.strategies) for i in range(self.taille)]
        self.meilleures_strategies = []
        self.individus = []
        self.init_strategies()

    def get_taille(self) -> int:
        """
        Retourne la taille de la population
        
        :return int: taille de la population
        """
        return self.taille

    def get_strategies(self) -> list:
        """
        Retourne la liste des stratégies de la population

        :return list: liste des stratégies de la population
        """
        return self.strategies

    def ajouter_strategie(self, strategie: list):
        """
        Ajoute une stratégie à la liste des stratégies de la population
        
        :param strategie list: stratégie à ajouter
        """
        self.strategies.append(strategie)

    def init_strategies(self):
        """
        Initialise les stratégies de la population
        """
        for i in range(self.taille):
            nomJoueur = "Joueur " + str(i)
            joueur = Joueur(nomJoueur, self.nb_strategies, self.strategies)
            self.ajouter_strategie(joueur)

    def jouer_tous(self, marché):
        """
        Fait jouer tous les joueurs de la population
        
        :param marché Marché: marché sur lequel les joueurs vont jouer
        """
        for strat in self.strategies:
            for joueur in strat.get_joueurs():
                ordres = joueur.generer_ordres(marché)
                marché.execute_ordres(ordres, joueur.get_nom())
                joueur.ajouter_rendement(marché.get_prix_actuel())

    def trier_strategies(self):
        """
        Trie les stratégies de la population en fonction de leur rendement moyen
        """
        self.strategies = sorted(self.strategies, key=lambda x: sum([joueur.get_rendements()[-1] for joueur in x.get_joueurs()])/len(x.get_joueurs()), reverse=True)

    def selectionner(self):
        """
        Sélectionne les stratégies les plus performantes de la population
        """
        self.trier_strategies()
        self.meilleures_strategies = self.strategies[:int(self.taille/2)]
        self.strategies = []
        for strat in self.meilleures_strategies:
            self.strategies.append(strat)
            clone = strat.clone()
            clone.muter()
            self.strategies.append(clone)
            
    def get_meilleure_strategie(self) -> Stratégie:
        """
        Retourne la meilleure stratégie de la population
        
        :return Stratégie: meilleure stratégie de la population
        """
        self.trier_strategies()
        return self.strategies[0]
    
    def get_joueurs(self, strat: Stratégie) -> list:
        """
        Retourne la liste des joueurs qui utilisent la stratégie passée en paramètre

        :param strat Stratégie: stratégie dont on veut les joueurs
        :return list: liste des joueurs qui utilisent la stratégie passée en paramètre
        """
        return [joueur for joueur in self.joueurs if joueur.strategies == strat]

    def selectionner_meilleures_strategies(self, pourcentage: float):
        """
        Sélectionne les meilleures stratégies de la population
        """
        nb_strategies = int(self.taille * pourcentage)
        self.meilleures_strategies = self.strategies[:nb_strategies]
        self.individus = [strat for strat in self.meilleures_strategies]

    def reproduire(self):
        """
        Réalise la reproduction des stratégies de la population
        """
        nouvelle_generation = Population(self.taille, self.nb_strategies)
        for i in range(self.taille):
            parents = random.sample(self.meilleures_strategies, 2)
            enfant = self.croisement(parents[0], parents[1])
            nouvelle_generation.ajouter_strategie(enfant)
        return nouvelle_generation

    def croisement(self, parent1, parent2) -> Joueur:
        """
        Réalise le croisement entre deux stratégies
        
        :param parent1 Stratégie: première stratégie
        :param parent2 Stratégie: deuxième stratégie
        :return Stratégie: stratégie enfant
        """
        point_de_croisement = random.randint(1, self.nb_strategies-1)
        enfant_strategie = parent1.get_strategie()[:point_de_croisement] + parent2.get_strategie()[point_de_croisement:]
        enfant = Joueur(parent1.get_nom(), self.nb_strategies)
        enfant.set_strategie(enfant_strategie)
        return enfant
