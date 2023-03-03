from joueur import Joueur
import random

class Population:
    def __init__(self, taille, nb_strategies):
        self.taille = taille
        self.nb_strategies = nb_strategies
        self.strategies = []
        self.meilleures_strategies = []
        self.individus = []
        self.init_strategies()

    def get_taille(self):
        return self.taille

    def get_strategies(self):
        return self.strategies

    def ajouter_strategie(self, strategie):
        self.strategies.append(strategie)

    def init_strategies(self):
        # Initialise les strategies de la population avec des joueurs aléatoires
        for i in range(self.taille):
            nomJoueur = "Joueur " + str(i)
            joueur = Joueur(nomJoueur, self.nb_strategies, self.strategies)
            self.ajouter_strategie(joueur)

    def jouer_tous(self, marché):
        # Joue toutes les strategies de la population sur le marché
        for strat in self.strategies:
            for joueur in strat.get_joueurs():
                ordres = joueur.generer_ordres(marché)
                marché.execute_ordres(ordres, joueur.get_nom())
                joueur.ajouter_rendement(marché.get_prix_actuel())

    def trier_strategies(self):
        # Trie les strategies de la population par ordre décroissant de rendement moyen de tous les joueurs dans chaque stratégie
        self.strategies = sorted(self.strategies, key=lambda x: sum([joueur.get_rendements()[-1] for joueur in x.get_joueurs()])/len(x.get_joueurs()), reverse=True)

    def selectionner(self):
        # Sort the strategies by score
        self.trier_strategies()
        # Keep only the best half of the strategies
        self.meilleures_strategies = self.strategies[:int(self.taille/2)]
        # Reset the strategies list
        self.strategies = []
        # Add the best strategies and their clones to the list
        for strat in self.meilleures_strategies:
            self.strategies.append(strat)
            clone = strat.clone()
            clone.muter()
            self.strategies.append(clone)
            
    def get_meilleure_strategie(self):
        self.trier_strategies()
        return self.strategies[0]

    def selectionner_meilleures_strategies(self, pourcentage):
        # Sélectionne les meilleures strategies de la population
        nb_strategies = int(self.taille * pourcentage)
        self.meilleures_strategies = self.strategies[:nb_strategies]
        self.individus = [strat for strat in self.meilleures_strategies]

    def reproduire(self):
        # Reproduction des meilleures strategies pour créer une nouvelle génération
        nouvelle_generation = Population(self.taille, self.nb_strategies)
        for i in range(self.taille):
            parents = random.sample(self.meilleures_strategies, 2)
            enfant = self.croisement(parents[0], parents[1])
            nouvelle_generation.ajouter_strategie(enfant)
        return nouvelle_generation

    def croisement(self, parent1, parent2):
        # Recombinaison d'un point (single-point crossover)
        #   On choisit un point aléatoire de croisement entre 1 et le nombre de stratégies
        point_de_croisement = random.randint(1, self.nb_strategies-1)
        #   On concatène la première partie de la stratégie du parent 1 avec la deuxième partie de la stratégie du parent 2
        enfant_strategie = parent1.get_strategie()[:point_de_croisement] + parent2.get_strategie()[point_de_croisement:]
        #   On crée un nouveau joueur avec la stratégie de l'enfant
        enfant = Joueur(parent1.get_nom(), self.nb_strategies)
        enfant.set_strategie(enfant_strategie)
        return enfant
