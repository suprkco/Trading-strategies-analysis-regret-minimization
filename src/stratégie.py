import random

import numpy as np

class Strategie:
    def __init__(self, type: str, seed: list):
        self.type = type
        self.seed = seed
        self.stop_loss = 0
        
        self.volume_min = 1000000 * ( 0.25 * (self.seed[0] - 0.5))
        
    
    def get_type(self) -> str:
        return self.type
    
    def get_seed(self) -> list:
        return self.seed
    
    def set_joueur(self, joueur) -> None:
        self.joueur = joueur
    
    def get_joueur(self) -> list:
        return self.joueur
    
    def strategie1(self, marche, joueur) -> tuple:
        choix, quantite = '', 0
        full_historique = marche.get_historique_prix()
        
        self.periode = 20 + int(10 * (self.seed[1] * 2 - 0.5))
        self.pertes_max = 0.05 * self.seed[2]
        
        if len(full_historique) > 20:
            prix_ouverture, prix_haut, prix_bas, prix_fermeture, prix_adj_fermeture, volume = marche.get_prix_actuel().values()
            prix_historiques = []
            [prix_historiques.append(prix['Close']) for prix in full_historique[len(full_historique) - self.periode:]]
            moyenne_mobile = np.mean(prix_historiques)
            if prix_fermeture > moyenne_mobile and volume > self.volume_min:
                choix = 'acheter'
                quantite = joueur.get_capital() // prix_fermeture
                self.stop_loss = prix_fermeture * (1 - self.pertes_max)
                self.volume_min = volume * 0.5
            elif prix_fermeture < self.stop_loss:
                choix = 'vendre'
                quantite = joueur.get_actions()
            elif prix_fermeture < self.stop_loss:
                self.stop_loss = 0
            
            self.stop_loss = max(self.stop_loss, prix_fermeture * (1 - self.pertes_max))
                
        return choix, quantite
    
    def strategie2(self):
        choix, quantite = '', 0
        return  choix, quantite

    def get_ordres(self, marche, joueur) -> tuple:
        choix, quantite = '', 0
        if self.type == 'Strategie 1':
            choix, quantite = self.strategie1(marche, joueur)
        elif self.type == 'Strategie 2':
            choix, quantite = self.strategie2(marche, joueur)
        return choix, quantite