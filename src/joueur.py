import random

class Joueur:
    """
    Classe représentant un joueur
    
    Attributs :
        nom :           nom du joueur
        nb_strategies : nombre de stratégies du joueur
        strategies :    stratégie du joueur
        rendements :    liste des rendements du joueur
        
    Méthodes :
        get_nom :                   retourne le nom du joueur
        ajouter_rendement :         ajoute un rendement à la liste des rendements du joueur
        get_rendements :            retourne la liste des rendements du joueur
        changer_strategie :         change la stratégie du joueur
        generer_ordres_joueur :     génère des ordres pour le joueur
        """
    def __init__(self, nom: str, nb_strategies: int, strategies: int):
        """
        Initialise un joueur

        :param nom str: nom du joueur
        :param nb_strategies int: nombre de stratégies du joueur
        :param strategies int: stratégie du joueur
        """
        self.nom = nom
        self.nb_strategies = nb_strategies
        self.strategies = strategies
        self.rendements = []

    def get_nom(self) -> str:
        """
        Retourne le nom du joueur
        
        :return str: nom du joueur
        """
        return self.nom

    def ajouter_rendement(self, rendement: float):
        """
        Ajoute un rendement à la liste des rendements du joueur

        :param rendement float: rendement du joueur
        """
        self.rendements.append(rendement)

    def get_rendements(self) -> list:
        """
        Retourne la liste des rendements du joueur

        :return list: liste des rendements du joueur
        """
        return self.rendements

    def changer_strategie(self):
        """
        Change la stratégie du joueur
        """
        if self.strategies:
            self.strategie = random.choice(self.strategies)

    def generer_ordres_joueur(self, marché) -> list:
        """
        Génère des ordres pour le joueur

        :param marché Marché: marché sur lequel le joueur va générer des ordres
        :return list: liste des ordres du joueur
        """
        ordres = []
        for i in range(self.nb_strategies):
            if i != self.strategies:
                qte = random.randint(1, 10)
                prix = random.uniform(marché.get_prix_min(), marché.get_prix_max())
                ordres.append((self.nom, i, qte, prix))
        return ordres
