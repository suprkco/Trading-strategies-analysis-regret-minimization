import random

class Regret:
    def __init__(self, actions):
        self.regrets = {a: 0 for a in actions}
        self.total_regret = 0
        
    def mise_a_jour(self, actions_payoffs):
        optimal_payoff = max(actions_payoffs.values())
        
        for action in actions_payoffs:
            regret = optimal_payoff - actions_payoffs[action]
            self.regrets[action] += regret
            self.total_regret += abs(regret)
            
    def choisir_action(self):
        if self.total_regret == 0:
            return random.choice(list(self.regrets.keys()))
        
        weighted_regrets = {a: self.regrets[a] / self.total_regret for a in self.regrets}
        return random.choices(list(weighted_regrets.keys()), list(weighted_regrets.values()))[0]
