from Classes_Objets import Gare, Ligne


class LigneDAO:

    def creer(self, ligne: Ligne) -> Ligne:
        return ligne

    def rechercher(self, gare_depart: Gare, gare_arrivee: Gare) -> Ligne:
        pass

    def trouver_par_id(id_ligne: int) -> Ligne:
        pass
