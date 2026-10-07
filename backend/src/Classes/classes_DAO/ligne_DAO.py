from classes_objets.gare import Gare
from classes_objets.ligne import Ligne
from src.utils.db_connexion import DBConnexion


class LigneDAO:
    def creer(self, ligne: Ligne) -> None:
        """
        Insère une ligne dans la base de données.

        Param:
        ------
        ligne: Ligne
          la ligne à créer (son id_ligne est None avant l'insertion)

        """
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO lignes(id_gare_depart, id_gare_arrivee)   "
                    "VALUES (%(id_gare_depart)s, %(id_gare_arrivee)s)      "
                    "RETURNING id_ligne                                    ",
                    {
                        "id_gare_depart": ligne.id_gare_depart,
                        "id_gare_arrivee": ligne.id_gare_arrivee,
                    },
                )
        return None

    def rechercher(self, gare_depart: Gare, gare_arrivee: Gare) -> Ligne:
        pass

    def trouver_par_id(id_ligne: int) -> Ligne:
        pass
