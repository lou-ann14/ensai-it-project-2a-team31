from src.Classes.classes_objets.gare import Gare
from src.utils.db_connexion import DBConnexion


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
                    "  FROM gares                     "
                    " WHERE (%(nom)s IS NULL OR nom ILIKE %(nom)s)          "
                    "   AND (%(ville)s IS NULL OR ville ILIKE %(ville)s)"
                    " ORDER BY nom",
                    {
                        "nom": f"{nom}%" if nom else None,
                        "ville": f"{ville}%" if ville else None,
                    })
                gare_bdd = cursor.fetchall()

        gares = []
        for trouve in gare_bdd:
            gares.append(Gare(
                id_gare=trouve["id_gare"],
                nom=trouve["nom"],
                ville=trouve["ville"]
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
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_gare, nom, ville             "
                    "  FROM gares                           "
                    " WHERE id_gare = %(id_gare)s           ",
                    {"id_gare": id_gare}
                )
                gare_bdd = cursor.fetchone()
       
        gare = None
        if gare_bdd:
            gare = Gare(
                id_gare=gare_bdd["id_gare"],
                nom=gare_bdd["nom"],
                ville=gare_bdd["ville"]
            )
        return gare
    def creer_ou_mettre_a_jour(self, gare: Gare) -> Gare:
        """Enregistre une gare, ou met à jour son nom et sa ville si son id_sncf existe déjà."""
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO gares(nom, ville, id_sncf)                  "
                    "VALUES (%(nom)s, %(ville)s, %(id_sncf)s)                "
                    "ON CONFLICT (id_sncf) DO UPDATE                         "
                    "   SET nom = EXCLUDED.nom, ville = EXCLUDED.ville       "
                    "RETURNING id_gare                                       ",
                    {"nom": gare.nom, "ville": gare.ville, "id_sncf": gare.id_sncf},
                )
                gare.id_gare = cursor.fetchone()["id_gare"]
        return gare