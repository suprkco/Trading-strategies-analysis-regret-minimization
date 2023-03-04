import random
from marché import Marché
from population import Population
from tournoi import Tournoi

class Simulation:
    """
    Classe représentant une simulation

    Attributs :
        nb_generations :    nombre de générations
        nb_tours :          nombre de tours par génération
        nb_joueurs :        nombre de joueurs par génération
        nb_strategies :     nombre de stratégies par génération
        marché :            marché sur lequel les joueurs vont jouer

    Méthodes :
        run :               lance la simulation
        afficher_details :  affiche les détails de la simulation
    """
    def __init__(self, nb_generations: int, nb_tours: int, nb_joueurs: int, nb_strategies: int):
        """
        Initialise une simulation
        
        :param nb_generations int: nombre de générations
        :param nb_tours int: nombre de tours par génération
        :param nb_joueurs int: nombre de joueurs par génération
        :param nb_strategies int: nombre de stratégies par génération
        """
        self.nb_generations = nb_generations
        self.nb_tours = nb_tours
        self.nb_joueurs = nb_joueurs
        self.nb_strategies = nb_strategies
        self.marche = Marché(self.nb_tours)
        self.population = Population(self.nb_joueurs, self.nb_strategies, random.uniform(0, 1))
        self.resultats = []

    def run(self):
        """
        Lance la simulation
        """
        for i in range(self.nb_generations):
            for j in range(self.nb_tours):
                tournoi = Tournoi(self.marche, self.population.get_strategies(), self.nb_tours, self.nb_joueurs)
                tournoi.jouer()
                self.afficher_details()
            self.population.selectionner()
            self.resultats.append(self.population.get_meilleure_strategie())

    def afficher_details(self):
        """
        Affiche les détails de la simulation
        """
        for strat in self.population.get_strategies():
            print("Stratégie", strat.get_nom(), ":", sum([joueur.get_rendements()[-1] for joueur in strat.get_joueurs()])/len(strat.get_joueurs()))
        print("Meilleure stratégie :", self.population.get_meilleure_strategie().get_nom())

if __name__ == "__main__":
    sim = Simulation(10, 7, 100, 10)
    sim.run()
