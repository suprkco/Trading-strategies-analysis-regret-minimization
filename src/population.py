import os
import random
from typing import List
from joueur import Joueur
from stratégie import Strategie


class Population:
    def __init__(self, marche, nb_joueurs: int):
        self.joueurs = []
        self.nb_strategies = 2
        self.marche = marche
        self.nb_joueurs = nb_joueurs

        self.lenghtSeed = 4
        # Création des joueurs
        for i in range(nb_joueurs):
            # On attribue une stratégie aléatoire à chaque joueur
            seed = [random.uniform(0, 1) for i in range(self.lenghtSeed)]
            strat = Strategie("Strategie {}".format(i%self.nb_strategies), seed)
            joueur = Joueur(str(i+1), strat)
            self.joueurs.append(joueur)
            strat.set_joueur(joueur)

    def get_joueurs(self) -> List[Joueur]:
        return self.joueurs

    def selectionner(self) -> None:
        """
        retourne la population complete avec un croisement des meilleurs joueurs
        On ne peu croiser que des joueurs de la meme strategie ensembles
        """
        meilleurs_joueurs = self.get_meilleures_strategies()
        strategies_type_1 = [joueur.get_strategie() for joueur in meilleurs_joueurs if joueur.get_strategie().get_type() == "Strategie 1"]
        strategies_type_2 = [joueur.get_strategie() for joueur in meilleurs_joueurs if joueur.get_strategie().get_type() == "Strategie 2"]
        new_joueurs = []
        for i in range(len(meilleurs_joueurs)):
            if len(strategies_type_1) > 2:
                s1 = random.choice(strategies_type_1)
                strategies_type_1.remove(s1)
                s2 = random.choice(strategies_type_1)
                strategies_type_1.remove(s2)
                
                seed_s1, seed_s2 = s1.get_seed(), s2.get_seed()
                point_croisement = random.randint(0, len(seed_s1))
                new_seed_s1, new_seed_s2 = seed_s1[:point_croisement] + seed_s2[point_croisement:], seed_s2[:point_croisement] + seed_s1[point_croisement:]
                
                new_joueurs.append(Joueur('Joueur '+str(i+1), Strategie("Strategie 1", new_seed_s1)))
                new_joueurs.append(Joueur('Joueur '+str(i+1), Strategie("Strategie 1", new_seed_s2)))
            
            if len(strategies_type_2) > 2:
                s1 = random.choice(strategies_type_2)
                strategies_type_2.remove(s1)
                s2 = random.choice(strategies_type_2)
                strategies_type_2.remove(s2)
                
                seed_s1, seed_s2 = s1.get_seed(), s2.get_seed()
                point_croisement = random.randint(0, len(seed_s1))
                new_seed_s1, new_seed_s2 = seed_s1[:point_croisement] + seed_s2[point_croisement:], seed_s2[:point_croisement] + seed_s1[point_croisement:]

                new_joueurs.append(Joueur('Joueur '+str(i+1), Strategie("Strategie 2", new_seed_s1)))
                new_joueurs.append(Joueur('Joueur '+str(i+1), Strategie("Strategie 2", new_seed_s2)))
        
        # On ajoute les joueurs qui n'ont pas pu être croisés
        if len(strategies_type_1) > 0:
            for s in strategies_type_1:
                new_joueurs.append(Joueur('Joueur '+str(len(new_joueurs)), s))
        elif len(strategies_type_2) > 0:
            for s in strategies_type_2:
                new_joueurs.append(Joueur('Joueur '+str(len(new_joueurs)), s))
        # On ajoute des joueurs aléatoires   
        while len(new_joueurs) < self.nb_joueurs:
            seed = [random.uniform(0, 1) for i in range(self.lenghtSeed)]
            new_joueurs.append(Joueur('Joueur '+str(len(new_joueurs)), Strategie("Strategie {}".format(random.randint(0, 1)), seed)))
        
        self.joueurs = new_joueurs
        
    def display_population(self) -> None:
        """
        Affiche les joueurs de la population
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        avancement = self.marche.get_avancement()
        length_prix = self.marche.get_length_prix()
        prix_actuel = self.marche.get_prix_actuel()['Close']
        entreprise = self.marche.get_entreprise
        joueurs = self.joueurs
        sorted_joueurs = sorted(joueurs, key=lambda joueur: joueur.get_total_capital(self.marche), reverse=True)
        print("\n\nTour %i/%i, Prix actuel: %f $" % (avancement, length_prix, prix_actuel))
        for joueur in sorted_joueurs:
            strategie = joueur.get_strategie()
            net_worth = joueur.get_total_capital(self.marche)
            capital_depart = joueur.get_capital_depart()
            difference = net_worth - capital_depart
            color_net_worth = '\033[92m' if difference >= 0 else '\033[91m'
            # print("Joueur %s, strategie: %s, performance: %s%f\033[0m $" % (joueur.get_nom(), str(strategie.get_seed()), color_net_worth, difference))
            print("Joueur %s : performance: %s%.1f\033[0m $" % (joueur.get_nom(), color_net_worth, difference), end=', ')
        

    def get_meilleures_strategies(self) -> Strategie:
        """
        Retourne la meilleure stratégie de la population actuelle.
        """
        nb_joueurs_a_selectionner = int(self.nb_joueurs / 2)
        self.joueurs = sorted(self.joueurs, key=lambda joueur: joueur.get_total_capital(self.marche), reverse=True)
        self.joueurs = self.joueurs[:nb_joueurs_a_selectionner]
        return self.joueurs