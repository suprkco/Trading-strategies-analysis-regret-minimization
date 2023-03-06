import os


class Tournoi:
    def __init__(self, marche, population, nb_tours: int):
        self.marche = marche
        self.population = population
        self.nb_tours = nb_tours
        self.length_prix = self.marche.get_length_prix()
        self.marche.reset_avancement()
    
    def jouer(self) -> None:
        self.marche.choix_entreprise()
        while self.marche.get_avancement() < self.length_prix:
            for joueur in self.population.get_joueurs():
                strategie = joueur.get_strategie()
                choix, quantite = strategie.get_ordres(self.marche, joueur)
                if choix == 'acheter':
                    joueur.acheter(self.marche, self.marche.get_prix_actuel()['Close'], quantite)
                elif choix == 'vendre':
                    joueur.vendre(self.marche, self.marche.get_prix_actuel()['Close'], quantite)
                # else: garder
            self.population.display_population()
            self.marche.set_prix_actuel()