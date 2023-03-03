import itertools
import random

from marché import Marché


class Tournoi:
    def __init__(self, marché, population, nb_matchs, taille_tournoi):
        self.marché = marché
        self.population = population # liste de stratégies
        self.nb_matchs = nb_matchs # nombre de matchs par groupe
        self.taille_tournoi = taille_tournoi # nombre de joueurs par groupe
        self.individus = [strat for strat in self.population]

    def jouer(self):
        # Initialise les scores
        scores = {strat: 0 for strat in self.population}
        # Joue le nombre de matchs spécifié
        for i in range(self.nb_matchs):
            # Mélange aléatoirement la population
            random.shuffle(self.population)
            # Divise la population en sous-groupes
            groupes = [self.population[j:j + self.taille_tournoi]
            for j in range(0, len(self.population), self.taille_tournoi)]
            # Joue les matchs de chaque groupe
            for groupe in groupes:
                matchs = itertools.combinations(groupe, 2)
                for s1, s2 in matchs:
                    # Génère les ordres pour chaque stratégie
                    ordres1 = s1.generer_ordres(self.marché)
                    ordres2 = s2.generer_ordres(self.marché)
                    ordres = ordres1 + ordres2
                    # Simule les ordres sur le marché
                    prix, qtes = Marché.simuler_ordres(ordres)
                    # Évalue les stratégies
                    resultat1 = s1.evaluer_match(prix, qtes)
                    resultat2 = s2.evaluer_match(prix, qtes)
                    # Met à jour les scores
                    scores[s1] += resultat1
                    scores[s2] += resultat2
        self.scores = scores

    def get_scores(self):
        return self.scores

    def get_classement(self):
        classement = sorted(self.population, key=lambda s: self.scores[s], reverse=True)
        return classement

    def reset(self):
        self.scores = {strat: 0 for strat in self.population}
        
    def __iter__(self):
        return iter(self.individus)
