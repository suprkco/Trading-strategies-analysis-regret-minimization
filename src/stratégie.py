class Stratégie:
    def __init__(self, nom: str, poids: float):
        self.nom = nom
        self.poids = poids
        self.rendements = []
        self.regrets = []
    
    def get_nom(self) -> str:
        return self.nom
    
    
    def get_rendements(self) -> list:
        return self.rendements
    
    def get_regrets(self) -> list:
        return self.regrets
    
    def jouer(self, marché) -> list:
        ordres = []
        total_qte = sum([joueur.get_qte() for joueur in self.joueurs])
        prix = marché.get_prix()
        if prix is None:
            return None
        qte = int(self.poids * total_qte) - sum([joueur.get_qte() for joueur in self.joueurs if joueur.get_acheteur()])
        if qte > 0:
            ordres.append((prix, qte, True))
        elif qte < 0:
            ordres.append((prix, -qte, False))
        return ordres
    
    def calculer_rendement(self, marché) -> float:
        rendement = marché.get_prix_actuel() - self.prix_achat
        self.rendements.append(rendement)
        return rendement

    def calculer_regret(self, marché, autres_stratégies: list) -> float:
        rendements = [strat.calculer_rendement(marché) for strat in autres_stratégies]
        meilleur_rendement = max(rendements)
        regret = meilleur_rendement - self.calculer_rendement(marché)
        self.regrets.append(regret)
        return regret
