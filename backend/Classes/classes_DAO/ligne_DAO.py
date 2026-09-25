from classes_objets import gare, ligne


class LigneDAO:

    def creer(self, ligne: ligne) -> ligne:
        return ligne

    def rechercher(self, gare_depart: gare, gare_arrivee: gare) -> ligne:
        pass

    def trouver_par_id(id_ligne: int) -> ligne:
        pass
