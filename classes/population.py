from joueur import Joueur
import random

class Population:
    def __init__(self, taille, nb_strategies):
        self.taille = taille
        self.nb_strategies = nb_strategies
        self.stratégies = []
        self.meilleures_stratégies = []
        self.individus = []
        self.init_stratégies()

    def get_taille(self):
        return self.taille

    def get_stratégies(self):
        return self.stratégies

    def ajouter_stratégie(self, stratégie):
        self.stratégies.append(stratégie)

    def init_stratégies(self):
        # Initialise les stratégies de la population avec des joueurs aléatoires
        for i in range(self.taille):
            nomJoueur = "Joueur " + str(i)
            joueur = Joueur(nomJoueur, self.nb_strategies, self.stratégies)
            self.ajouter_stratégie(joueur)

    def jouer_tous(self, marché):
        # Joue toutes les stratégies de la population sur le marché
        for strat in self.stratégies:
            for joueur in strat.get_joueurs():
                ordres = joueur.generer_ordres(marché)
                marché.execute_ordres(ordres, joueur.get_nom())
                joueur.ajouter_rendement(marché.get_prix_actuel())

    def trier_stratégies(self):
        # Trie les stratégies de la population par ordre décroissant de rendement
        self.stratégies.sort(key=lambda strat: strat.get_rendements()[-1], reverse=True)

    def selectionner_meilleures_stratégies(self, pourcentage):
        # Sélectionne les meilleures stratégies de la population
        nb_stratégies = int(self.taille * pourcentage)
        self.meilleures_stratégies = self.stratégies[:nb_stratégies]
        self.individus = [strat for strat in self.meilleures_stratégies]

    def reproduire(self):
        # Reproduction des meilleures stratégies pour créer une nouvelle génération
        nouvelle_génération = Population(self.taille, self.nb_strategies)
        for i in range(self.taille):
            parents = random.sample(self.meilleures_stratégies, 2)
            enfant = self.croisement(parents[0], parents[1])
            nouvelle_génération.ajouter_stratégie(enfant)
        return nouvelle_génération

    def croisement(self, parent1, parent2):
        # Recombinaison d'un point (single-point crossover)
        point_de_croisement = random.randint(1, self.nb_strategies-1)
        enfant_stratégie = parent1.get_stratégie()[:point_de_croisement] + parent2.get_stratégie()[point_de_croisement:]
        enfant = Joueur(self.nb_strategies)
        enfant.set_stratégie(enfant_stratégie)
        return enfant
