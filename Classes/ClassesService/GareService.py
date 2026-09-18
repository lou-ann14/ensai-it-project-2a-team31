from Classes import Gare


class GareService:
    """Modélise les méthodes proposées à l'utilisateur en ce qui concerne les gares

    Param
    -----
    gares: list[Gare]
        recense les gares pour la recherche
    """

    def __init__(self, gares: list[Gare]):
        self.gares = gares