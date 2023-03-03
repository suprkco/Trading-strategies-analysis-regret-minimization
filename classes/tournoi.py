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
        scores = {strat: 0 for strat in self.population}
        for i in range(self.nb_matchs):
            random.shuffle(self.population)
            groupes = [self.population[j:j + self.taille_tournoi]
                       for j in range(0, len(self.population), self.taille_tournoi)]
            for groupe in groupes:
                matchs = itertools.combinations(groupe, 2)
                for s1, s2 in matchs:
                    ordres1 = s1.generer_ordres(self.marché)
                    ordres2 = s2.generer_ordres(self.marché)
                    prix, qtes = Marché.simuler_ordres(ordres1 + ordres2)
                    resultat1 = s1.evaluer_match(prix, qtes)
                    resultat2 = s2.evaluer_match(prix, qtes)
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
