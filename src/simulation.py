from marché import Marché
from population import Population
from tournoi import Tournoi

class Simulation:
    def __init__(self, nb_generations, nb_tours, nb_joueurs, nb_strategies):
        self.nb_generations = nb_generations
        self.nb_tours = nb_tours
        self.nb_joueurs = nb_joueurs
        self.nb_strategies = nb_strategies
        self.marche = Marché(self.nb_tours)
        self.population = Population(self.nb_joueurs, self.nb_strategies)
        self.resultats = []

    def run(self):
        for i in range(self.nb_generations):
            for j in range(self.nb_tours):
                tournoi = Tournoi(self.marche, self.population.get_strategies(), self.nb_tours, self.nb_joueurs)
                tournoi.jouer()
            self.population.selectionner()
            self.resultats.append(self.population.get_meilleure_strategie())

# 10 generations, 7 tours, 100 joueurs, 10 strategies, un anneaux pour les gouverner tous
sim = Simulation(10, 7, 100, 10)
sim.run()
