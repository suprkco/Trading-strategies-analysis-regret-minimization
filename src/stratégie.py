import random

class Strategie:
    def __init__(self, type: str, seed: int):
        self.type = type
        self.seed = seed
    
    def get_type(self) -> str:
        return self.type
    
    def get_seed(self) -> list:
        return self.seed
    
    def set_joueur(self, joueur) -> None:
        self.joueur = joueur
    
    def get_joueur(self) -> list:
        return self.joueur
    
    def minimize_regret(self, choix, quantite) -> str:
        max_regret = float('inf')
        # Calculer la quantité optimale d'actions à acheter ou vendre pour minimiser les regrets
        # en utilisant la méthode de votre choix
        return choix, quantite
    
    def get_ordres(self, marche, joueur) -> tuple:
        choix, quantite = '', 0
        prix_ouverture, prix_haut, prix_bas, prix_fermeture, prix_adj_fermeture, volume = marche.get_prix_actuel().values()
        # Utiliser la méthode minimize_regret pour minimiser les regrets
        choix, quantite = self.minimize_regret(choix)
        return choix, quantite
