from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.utils.db_connexion import DBConnexion

# Récupère une ligne avec ses deux gares.
SELECT_LIGNE = (
    "SELECT l.id_ligne,                                                        "
    "       gd.id_gare AS id_gare_depart, gd.nom AS nom_gare_depart,           "
    "       gd.ville AS ville_gare_depart, gd.id_sncf AS id_sncf_gare_depart,  "
    "       ga.id_gare AS id_gare_arrivee, ga.nom AS nom_gare_arrivee,         "
    "       ga.ville AS ville_gare_arrivee, ga.id_sncf AS id_sncf_gare_arrivee "
    "  FROM lignes l                                                           "
    "  JOIN gares gd ON gd.id_gare = l.id_gare_depart                          "
    "  JOIN gares ga ON ga.id_gare = l.id_gare_arrivee                         "
)


class LigneDAO:
    @staticmethod
    def _construire_ligne(ligne_bdd: dict) -> Ligne:
        """Transforme une ligne renvoyée par SELECT_LIGNE en objet Ligne complet."""
        return Ligne(
            gare_depart=Gare(
                nom=ligne_bdd["nom_gare_depart"],
                ville=ligne_bdd["ville_gare_depart"],
                id_sncf=ligne_bdd["id_sncf_gare_depart"],
                id_gare=ligne_bdd["id_gare_depart"],
            ),
            gare_arrivee=Gare(
                nom=ligne_bdd["nom_gare_arrivee"],
                ville=ligne_bdd["ville_gare_arrivee"],
                id_sncf=ligne_bdd["id_sncf_gare_arrivee"],
                id_gare=ligne_bdd["id_gare_arrivee"],
            ),
            id_ligne=ligne_bdd["id_ligne"],
        )

    def creer(self, gare_depart: Gare, gare_arrivee: Gare, id_collaborateur: int | None = None) -> Ligne:
        """
        Insère une ligne dans la base de données.

        Param:
        ------
        gare_depart: Gare
            la gare qui se trouvera en début de ligne
        gare_arrivee: Gare
            la gare qui se trouvera en bout de ligne
        id_collaborateur: int | None
            l'id du collaborateur qui crée la ligne (optionnel)

        Return:
        ------
        Ligne
            la ligne créée, avec son id_ligne renseigné
        """
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO lignes(id_gare_depart, id_gare_arrivee, id_collaborateur)   "
                "VALUES (%(id_gare_depart)s, %(id_gare_arrivee)s, %(id_collaborateur)s)  "
                "RETURNING id_ligne                                                      ",
                {
                    "id_gare_depart": gare_depart.id_gare,
                    "id_gare_arrivee": gare_arrivee.id_gare,
                    "id_collaborateur": id_collaborateur,
                },
            )
            id_ligne = cursor.fetchone()["id_ligne"]

        return Ligne(gare_depart=gare_depart, gare_arrivee=gare_arrivee, id_ligne=id_ligne)

    def rechercher(self, gare_depart: Gare, gare_arrivee: Gare) -> Ligne | None:
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
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                SELECT_LIGNE +
                " WHERE l.id_gare_depart  = %(id_gare_depart)s         "
                "   AND l.id_gare_arrivee = %(id_gare_arrivee)s        ",
                {
                    "id_gare_depart": gare_depart.id_gare,
                    "id_gare_arrivee": gare_arrivee.id_gare,
                })
            ligne_bdd = cursor.fetchone()

        return self._construire_ligne(ligne_bdd) if ligne_bdd else None

    def trouver_par_id(self, id_ligne: int) -> Ligne | None:
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
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                SELECT_LIGNE +
                " WHERE l.id_ligne = %(id_ligne)s                      ",
                {"id_ligne": id_ligne}
            )
            ligne_bdd = cursor.fetchone()

        return self._construire_ligne(ligne_bdd) if ligne_bdd else None
