from gare import Gare


class Ligne:
    def __init__(self, id_ligne: int, gare_depart: Gare, gare_arrivee: Gare):
        self.id_ligne = id_ligne
        self.gare_depart = gare_depart
        self.gare_arrivee = gare_arrivee

    def __str__(self):
        return f"la gare de depart de la ligne : #{self.id_ligne} est #{self.gare_depart} et la gare d'arrivée est : # {self.gare_arrivee}"
