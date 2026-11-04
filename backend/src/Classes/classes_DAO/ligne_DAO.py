from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.utils.db_connexion import DBConnexion
from src.utils.log_utils import get_logger, log

logger = get_logger(__name__)

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
    """
    Classe qui interagit avec la base de données pour les objets de type Ligne
    """
    @staticmethod
    def _construire_ligne(ligne_bdd: dict) -> Ligne:
        """
        Transforme une ligne renvoyée par SELECT_LIGNE en objet Ligne complet (avec ses deux Gares).

        Param:
        ------
        ligne_bdd: dict
            une ligne renvoyée par le curseur après la requête SELECT_LIGNE

        Return:
        ------
        Ligne
            la ligne avec ses gares de départ et d'arrivée
        """
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

    @log
    def creer(self, gare_depart: Gare, gare_arrivee: Gare, id_collaborateur: int | None = None) -> Ligne:
        """
        Enregistre une nouvelle ligne dans la base de données.

        Param:
        ------
        gare_depart: Gare
            la gare de début de ligne
        gare_arrivee: Gare
            la gare de fin de ligne
        id_collaborateur: int | None
            l'identifiant du collaborateur qui crée la ligne (optionnel)

        Return:
        ------
        Ligne
            la ligne créée, avec son id_ligne renseigné

        Raises:
        ------
        psycopg2.errors.ForeignKeyViolation
            si une des gares ou le collaborateur n'existe pas
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
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
        except Exception as e:
            logger.error(f"Erreur base de données dans LigneDAO.creer : {e}")
            raise

        return Ligne(gare_depart=gare_depart, gare_arrivee=gare_arrivee, id_ligne=id_ligne)

    @log
    def rechercher(self, gare_depart: Gare, gare_arrivee: Gare) -> Ligne | None:
        """
        Recherche la ligne reliant une gare de départ à une gare d'arrivée.

        Param:
        ------
        gare_depart: Gare
            la gare de départ
        gare_arrivee: Gare
            la gare d'arrivée

        Return:
        ------
        Ligne | None
            la ligne trouvée, ou None si aucune ligne ne relie ces deux gares

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
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
        except Exception as e:
            logger.error(f"Erreur base de données dans LigneDAO.rechercher : {e}")
            raise

        return self._construire_ligne(ligne_bdd) if ligne_bdd else None

    @log
    def trouver_par_id(self, id_ligne: int) -> Ligne | None:
        """
        Récupère une ligne par son identifiant.

        Param:
        ------
        id_ligne: int
            l'identifiant unique de la ligne

        Return:
        ------
        Ligne | None
            la ligne trouvée, ou None si elle n'existe pas

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    SELECT_LIGNE +
                    " WHERE l.id_ligne = %(id_ligne)s                      ",
                    {"id_ligne": id_ligne}
                )
                ligne_bdd = cursor.fetchone()
        except Exception as e:
            logger.error(f"Erreur base de données dans LigneDAO.trouver_par_id : {e}")
            raise

        return self._construire_ligne(ligne_bdd) if ligne_bdd else None

    @log
    def modifier(self, ligne: Ligne) -> bool:
        """
        Met à jour les gares de départ et d'arrivée d'une ligne existante.

        Param:
        ------
        ligne: Ligne
            la ligne contenant les nouvelles gares (identifiée par son id_ligne)

        Return:
        ------
        bool
            True si la modification a réussi, False si la ligne n'existe pas

        Raises:
        ------
        psycopg2.errors.ForeignKeyViolation
            si une des nouvelles gares n'existe pas
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE lignes                                     "
                    "   SET id_gare_depart  = %(id_gare_depart)s,      "
                    "       id_gare_arrivee = %(id_gare_arrivee)s      "
                    " WHERE id_ligne = %(id_ligne)s                    ",
                    {
                        "id_gare_depart": ligne.gare_depart.id_gare,
                        "id_gare_arrivee": ligne.gare_arrivee.id_gare,
                        "id_ligne": ligne.id_ligne,
                    },
                )
                nb_lignes_modifiees = cursor.rowcount
        except Exception as e:
            logger.error(f"Erreur base de données dans LigneDAO.modifier : {e}")
            raise

        return nb_lignes_modifiees > 0

    @log
    def supprimer(self, id_ligne: int) -> bool:
        """
        Supprime une ligne de la base de données.

        Param:
        ------
        id_ligne: int
            l'identifiant de la ligne à supprimer

        Return:
        ------
        bool
            True si la suppression a réussi, False si la ligne n'existe pas

        Raises:
        ------
        psycopg2.errors.ForeignKeyViolation
            si des trajets utilisent encore cette ligne
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM lignes                                "
                    " WHERE id_ligne = %(id_ligne)s                    ",
                    {"id_ligne": id_ligne},
                )
                nb_lignes_supprimees = cursor.rowcount
        except Exception as e:
            logger.error(f"Erreur base de données dans LigneDAO.supprimer : {e}")
            raise

        return nb_lignes_supprimees > 0

    @log
    def a_des_trajets(self, id_ligne: int) -> bool:
        """
        Indique si des trajets sont prévus sur une ligne.

        Param:
        ------
        id_ligne: int
            l'identifiant de la ligne

        Return:
        ------
        bool
            True si au moins un trajet utilise cette ligne, False sinon

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT EXISTS (SELECT 1 FROM trajets WHERE id_ligne = %(id_ligne)s) AS existe",
                    {"id_ligne": id_ligne},
                )
                return cursor.fetchone()["existe"]
        except Exception as e:
            logger.error(f"Erreur base de données dans LigneDAO.a_des_trajets : {e}")
            raise
