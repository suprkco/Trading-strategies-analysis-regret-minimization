class Situation:
    """
    Classe représentant une situation de jeu

    Attributs :
        marché :    marché sur lequel les joueurs vont jouer
        joueurs :   liste des joueurs de la situation

    Méthodes :
        ajouter_joueur :    ajoute un joueur à la situation
        jouer_tour :        fait jouer tous les joueurs de la situation
    """
    def __init__(self, marché):
        """
        Initialise une situation
        
        :param marché Marché: marché sur lequel les joueurs vont jouer"""
        self.marché = marché
        self.joueurs = []
        
    def ajouter_joueur(self, joueur):
        """
        Ajoute un joueur à la situation
        
        :param joueur Joueur: joueur à ajouter à la situation
        """
        self.joueurs.append(joueur)
        
    def jouer_tour(self):
        """
        Fait jouer tous les joueurs de la situation
        """
        for joueur in self.joueurs:
            action = joueur.jouer(self.marché)
            gain = self.marché.effectuer_transaction(action)
            joueur.mise_a_jour(gain)
