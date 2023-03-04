class Stratégie:
    """
    Classe représentant une stratégie
    
    Attributs :
        nom :           nom de la stratégie
        poids :         poids de la stratégie
        rendements :    liste des rendements de la stratégie
        regrets :       liste des regrets de la stratégie

    Méthodes :
        get_nom :               retourne le nom de la stratégie
        get_rendements :        retourne la liste des rendements de la stratégie
        get_regrets :           retourne la liste des regrets de la stratégie
        jouer :                 fait jouer la stratégie
        calculer_rendement :    calcule le rendement de la stratégie
        calculer_regret :       calcule le regret de la stratégie
        """
    def __init__(self, nom: str, poids: float):
        """
        Initialise une stratégie
        
        :param nom str: nom de la stratégie
        :param poids float: poids de la stratégie
        """
        self.nom = nom
        self.poids = poids
        self.rendements = []
        self.regrets = []
    
    def get_nom(self) -> str:
        """
        Retourne le nom de la stratégie
        
        :return str: nom de la stratégie
        """
        return self.nom
    
    
    def get_rendements(self) -> list:
        """
        Retourne la liste des rendements de la stratégie

        :return list: liste des rendements de la stratégie
        """
        return self.rendements
    
    def get_regrets(self) -> list:
        """
        Retourne la liste des regrets de la stratégie

        :return list: liste des regrets de la stratégie
        """
        return self.regrets
    
    def jouer(self, marché) -> list:
        """
        Fait jouer la stratégie

        :param marché Marché: marché sur lequel la stratégie va jouer
        :return list: liste des ordres de la stratégie
        """
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
        """
        Calcule le rendement de la stratégie

        :param marché Marché: marché sur lequel la stratégie a joué
        :return float: rendement de la stratégie
        """
        rendement = marché.get_prix_actuel() - self.prix_achat
        self.rendements.append(rendement)
        return rendement

    def calculer_regret(self, marché, autres_stratégies: list) -> float:
        """
        Calcule le regret de la stratégie
        
        :param marché Marché: marché sur lequel la stratégie a joué
        :param autres_stratégies list: liste des autres stratégies
        :return float: regret de la stratégie
        """
        rendements = [strat.calculer_rendement(marché) for strat in autres_stratégies]
        meilleur_rendement = max(rendements)
        regret = meilleur_rendement - self.calculer_rendement(marché)
        self.regrets.append(regret)
        return regret
