class Situation:
    def __init__(self, marché):
        self.marché = marché
        self.joueurs = []
        
    def ajouter_joueur(self, joueur):
        self.joueurs.append(joueur)
        
    def jouer_tour(self):
        for joueur in self.joueurs:
            action = joueur.jouer(self.marché)
            gain = self.marché.effectuer_transaction(action)
            joueur.mise_a_jour(gain)
