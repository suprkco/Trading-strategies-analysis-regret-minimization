import random

class Regret:
    """
    Classe représentant un regret
    
    Attributs :
        regrets :           dictionnaire des regrets des actions
        total_regret :      regret total
        
    Méthodes :
        mise_a_jour :       met à jour le regret
        choisir_action :    choisit une action en fonction du regret
    """
    def __init__(self, actions: list):
        """
        Initialise un regret
        
        :param actions list: liste des actions
        """
        self.regrets = {a: 0 for a in actions}
        self.total_regret = 0
        
    def mise_a_jour(self, actions_payoffs: dict):
        """
        Met à jour le regret
        
        :param actions_payoffs dict: dictionnaire des payoffs des actions
        """
        optimal_payoff = max(actions_payoffs.values())
        for action in actions_payoffs:
            regret = optimal_payoff - actions_payoffs[action]
            self.regrets[action] += regret
            self.total_regret += abs(regret)
            
    def choisir_action(self):
        """
        Choisi une action en fonction du regret
        
        :return str: action choisie
        """
        if self.total_regret == 0:
            return random.choice(list(self.regrets.keys()))
        weighted_regrets = {a: self.regrets[a] / self.total_regret for a in self.regrets}
        return random.choices(list(weighted_regrets.keys()), list(weighted_regrets.values()))[0]
