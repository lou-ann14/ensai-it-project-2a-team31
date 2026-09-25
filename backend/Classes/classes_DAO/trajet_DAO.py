from classes_objets.gare import Gare
from classes_objets.trajet import Trajet


class TrajetDAO:
    """classe qui intéragit avec la base de données pour les objets de type Trajet
    """
    def creer(self, trajet: Trajet):
        pass

    def modifier(self, trajet: Trajet):
        pass

    def supprimer(self, trajet: Trajet):
        pass

    def rechercher(self, gare_arrivee: Gare, gare_depart: Gare):
        pass

    def trouver_par_id(self, id_trajet: int):
        pass
