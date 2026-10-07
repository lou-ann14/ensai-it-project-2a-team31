from utils.db_connexion import DBConnexion
from classes_objets.gare import Gare


class GareDAO:

    def rechercher(self, nom: str | None, ville: str | None) -> list[Gare]:
        """
        Recherche des gares en fonction du nom ou de la ville.

        Param:
        ------
        nom: str | None
            le nom de la gare (optionnel)
        ville: str | None
            la ville de la gare (optionnel)

        Return:
        ------
        Gare
            l'objet Gare correspondant à la recherche
        """
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_gare, nom, ville                          "
                    "  FROM gare                      "
                    " WHERE (%(nom)s IS NULL OR nom ILIKE %(nom)           "
                    "   AND (%(ville)s IS NULL OR ville ILIKE %(ville)s)"
                    " ORDER BY nom",
                    {
                        "nom": f"{nom}%" if nom else None,
                        "ville": f"{ville}%" if ville else None,
                    },
                gare_bdd = cursor.fetchall()

        gares = []
        for trouve in gare_bdd:
            gares.append( Gare(
                id_gare=trouve["id_gare"],
                nom = trouve["nom"],
                ville = trouve["ville"]
            ))
        return gares

    def trouver_par_id(self, id_gare: int) -> Gare:
        """
        Récupère une gare spécifique par son identifiant.

        Param:
        ------
        id_gare: int
            l'identifiant unique de la gare

        Return:
        ------
        Gare
            l'objet Gare trouvé
        """
       
       
        pass
