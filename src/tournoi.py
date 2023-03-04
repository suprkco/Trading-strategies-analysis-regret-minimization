import itertools
import random

class Tournoi:
    def __init__(self, marché, population, nb_matchs, taille_tournoi):
        self.marché = marché
        self.population = population
        self.nb_matchs = nb_matchs
        self.taille_tournoi = taille_tournoi
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
                    ordres1 = s1.jouer(self.marché)
                    if ordres1 is None:
                        ordres1 = []
                    ordres2 = s2.jouer(self.marché)
                    if ordres2 is None:
                        ordres2 = []
                    ordres = ordres1 + ordres2
                    prix_qtes = self.marché.simuler_ordres(ordres)
                    if not prix_qtes:
                        continue
                    prix, qtes = prix_qtes
                    resultat1 = s1.evaluer_match(prix, qtes)
                    resultat2 = s2.evaluer_match(prix, qtes)
                    scores[s1] += resultat1
                    scores[s2] += resultat2
        self.scores = scores


    def get_scores(self) -> dict:
        return self.scores

    def get_classement(self) -> list:
        classement = sorted(self.population, key=lambda s: self.scores[s], reverse=True)
        return classement

    def reset(self):
        self.scores = {strat: 0 for strat in self.population}
        
    def __iter__(self) -> iter:
        return iter(self.individus)