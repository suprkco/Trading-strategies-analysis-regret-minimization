import itertools
import random

class Tournoi:
    """
    Classe représentant un tournoi
    
    Attribut:
        marché :            marché sur lequel les joueurs vont jouer
        population :        liste des joueurs
        nb_matchs :         nombre de matchs par tournoi
        taille_tournoi :    taille des groupes de joueurs

    Méthodes:
        jouer :             fait jouer tous les joueurs du tournoi
        get_scores :        retourne les scores des joueurs
        get_classesment :   retourne le classement des joueurs
        reset :             réinitialise les scores des joueurs
        """
    def __init__(self, marché, population, nb_matchs, taille_tournoi):
        """
        Initialise un tournoi
        
        :param marché Marché: marché sur lequel les joueurs vont jouer
        :param population list: liste des joueurs
        :param nb_matchs int: nombre de matchs par tournoi
        :param taille_tournoi int: taille des groupes de joueurs
        """
        self.marché = marché
        self.population = population
        self.nb_matchs = nb_matchs
        self.taille_tournoi = taille_tournoi
        self.individus = [strat for strat in self.population]

    def jouer(self):
        """
        Fait jouer tous les joueurs du tournoi
        """
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
        """
        Retourne les scores de tous les joueurs du tournoi
        
        :return dict: scores de tous les joueurs du tournoi
        """
        return self.scores

    def get_classement(self) -> list:
        """
        Retourne le classement des joueurs du tournoi

        :return list: classement des joueurs du tournoi
        """
        classement = sorted(self.population, key=lambda s: self.scores[s], reverse=True)
        return classement

    def reset(self):
        """
        Réinitialise le tournoi
        """
        self.scores = {strat: 0 for strat in self.population}
        
    def __iter__(self) -> iter:
        """
        Retourne un itérateur sur les joueurs du tournoi
        
        :return iter: itérateur sur les joueurs du tournoi
        """
        return iter(self.individus)