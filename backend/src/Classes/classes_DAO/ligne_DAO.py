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
        """Recherche la ligne reliant une gare de départ à une gare d'arrivée.

        Param:
        ------
        gare_depart: Gare
            la gare de départ
        gare_arrivee: Gare
            la gare d'arrivée

        Return:
        -------
        Ligne
            l'objet Ligne trouvé, ou None si aucune ligne ne relie ces deux gares
        """
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_ligne, id_gare_depart, id_gare_arrivee      "
                    "  FROM lignes                                         "
                    " WHERE id_gare_depart    = %(id_gare_depart)s         "
                    "   AND id_gare_arrivee   = %(id_gare_arrivee)s        ",
                    {
                        "id_gare_depart": gare_depart.id_gare,
                        "id_gare_arrivee": gare_arrivee.id_gare,
                    })
                ligne_bdd = cursor.fetchone()

        ligne = None
        if ligne_bdd:
            ligne = Ligne(
                id_ligne=ligne_bdd["id_ligne"],
                id_gare_depart=ligne_bdd["id_gare_depart"],
                id_gare_arrivee=ligne_bdd["id_gare_arrivee"],
            )
        return ligne

    def trouver_par_id(id_ligne: int) -> Ligne:
        """
        Récupère une ligne spécifique par son identifiant.

        Param:
        ------
        id_ligne: int
            l'identifiant unique de la ligne

        Return:
        ------
        Ligne
            l'objet Ligne trouvé
        """
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_ligne                         "
                    "FROM ligne                              "
                    "WHERE id_ligne = %(id_ligne)s            ",
                    {"id_ligne": id_ligne}
                )
                ligne_bdd = cursor.fetchone()
       
        ligne = None
        if ligne_bdd:
            ligne = Ligne(
                id_ligne=ligne_bdd["id_gare"],
                id_gare_depart=ligne_bdd["id_gare_depart"],
                id_gare_arrivee=ligne_bdd["id_gare_arrivee"]
            )
        return ligne
