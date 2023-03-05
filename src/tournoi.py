class Tournoi:
    def __init__(self, marche, population, nb_tours: int):
        self.marche = marche
        self.population = population
        self.nb_tours = nb_tours
    
    def jouer(self) -> None:
        self.marche.choix_entreprise()
        for joueur in self.population.get_joueurs():
            strategie = joueur.get_strategie()
            choix, quantite = strategie.get_ordres(self.marche, joueur)
            if choix == 'achat':
                joueur.acheter(self.marche, self.marche.get_prix_actuel()['Close'], quantite)
            elif choix == 'vente':
                joueur.vendre(self.marche, self.marche.get_prix_actuel()['Close'], quantite)
            # else: garder
            self.marche.set_prix_actuel()
