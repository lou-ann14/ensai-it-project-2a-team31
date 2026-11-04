from src.Classes.classes_objets.gare import Gare


class Ligne:
    """Modélise la classe Ligne, qui permet de gérer les différentes caracteristiques des lignes.

    Params
    ------
    gare_depart: Gare
        Gare de départ de la ligne
    gare_arrivee: Gare
        Gare d'arrivée de la ligne
    id_ligne: int
        id de la ligne dans la BDD
    """
    def __init__(self, gare_depart: Gare, gare_arrivee: Gare, id_ligne: int | None = None):
        if not isinstance(gare_depart, Gare):
            raise TypeError("La gare de départ doit être de type Gare")
        if not isinstance(gare_arrivee, Gare):
            raise TypeError("La gare d'arrivée doit être de type Gare.")
        if not isinstance(id_ligne, int):
            raise TypeError("L'id de la ligne doit être un entier.")

        self.id_ligne = id_ligne
        self.gare_depart = gare_depart
        self.gare_arrivee = gare_arrivee

    def __str__(self):
        return f"la gare de depart de la ligne #{self.id_ligne} est : #{self.gare_depart.nom} et la gare d'arrivée est : # {self.gare_arrivee.nom}"
