from marché import Marché
from population import Population
from tournoi import Tournoi

class Simulation:
    def __init__(self, nb_generations: int, nb_tours: int, nb_joueurs: int):
        self.nb_generations = nb_generations
        self.nb_tours = nb_tours
        self.nb_joueurs = nb_joueurs
        self.marche = Marché(self.nb_tours)
        self.population = Population(self.marche, self.nb_joueurs)

    def run(self):
        for i in range(self.nb_generations):
            tournoi = Tournoi(self.marche, self.population, self.nb_tours)
            tournoi.jouer()
            self.population.selectionner()
            print("\n\nGénération", i+1, "terminée.")
            input()

if __name__ == "__main__":
    sim = Simulation(10, 7, 10)
    sim.run()
