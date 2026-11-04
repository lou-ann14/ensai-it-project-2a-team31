from src.Classes.classes_objets.gare import Gare
from src.utils.db_connexion import DBConnexion
from src.utils.log_utils import get_logger, log

logger = get_logger(__name__)


class GareDAO:
    """
    Classe qui interagit avec la base de données pour les objets de type Gare
    """

    @log
    def rechercher(self, nom: str | None, ville: str | None) -> list[Gare]:
        """
        Recherche des gares dont le nom et/ou la ville commencent par le texte donné
        (insensible à la casse). Si aucun critère n'est renseigné, toutes les gares sont renvoyées.

        Param:
        ------
        nom: str | None
            le début du nom de la gare (optionnel)
        ville: str | None
            le début du nom de la ville (optionnel)

        Return:
        ------
        list[Gare]
            la liste des gares trouvées, triées par nom (vide si aucune)

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_gare, nom, ville, id_sncf                 "
                    "  FROM gares                     "
                    " WHERE (%(nom)s IS NULL OR nom ILIKE %(nom)s)          "
                    "   AND (%(ville)s IS NULL OR ville ILIKE %(ville)s)"
                    " ORDER BY nom",
                    {
                        "nom": f"{nom}%" if nom else None,
                        "ville": f"{ville}%" if ville else None,
                    })
                gare_bdd = cursor.fetchall()
        except Exception as e:
            logger.error(f"Erreur base de données dans GareDAO.rechercher : {e}")
            raise

        gares = []
        for trouve in gare_bdd:
            gares.append(Gare(
                id_gare=trouve["id_gare"],
                nom=trouve["nom"],
                ville=trouve["ville"],
                id_sncf=trouve["id_sncf"],
            ))
        return gares

    @log
    def trouver_par_id(self, id_gare: int) -> Gare:
        """
        Récupère une gare par son identifiant.

        Param:
        ------
        id_gare: int
            l'identifiant unique de la gare

        Return:
        ------
        Gare | None
            l'objet Gare trouvé, ou None s'il n'existe pas

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_gare, nom, ville, id_sncf    "
                    "  FROM gares                           "
                    " WHERE id_gare = %(id_gare)s           ",
                    {"id_gare": id_gare}
                )
                gare_bdd = cursor.fetchone()
        except Exception as e:
            logger.error(f"Erreur base de données dans GareDAO.trouver_par_id : {e}")
            raise

        gare = None
        if gare_bdd:
            gare = Gare(
                id_gare=gare_bdd["id_gare"],
                nom=gare_bdd["nom"],
                ville=gare_bdd["ville"],
                id_sncf=gare_bdd["id_sncf"],
            )
        return gare

    @log
    def creer_ou_mettre_a_jour(self, gare: Gare) -> Gare:
        """
        Enregistre une gare dans la base de données.
        Si une gare avec le même id_sncf existe déjà, son nom et sa ville sont mis à jour
        au lieu de créer un doublon.

        Param:
        ------
        gare: Gare
            la gare à enregistrer (avec son id_sncf renseigné)

        Return:
        ------
        Gare
            la même gare, avec son id_gare renseigné

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO gares(nom, ville, id_sncf)                  "
                    "VALUES (%(nom)s, %(ville)s, %(id_sncf)s)                "
                    "ON CONFLICT (id_sncf) DO UPDATE                         "
                    "   SET nom = EXCLUDED.nom, ville = EXCLUDED.ville       "
                    "RETURNING id_gare                                       ",
                    {"nom": gare.nom, "ville": gare.ville, "id_sncf": gare.id_sncf},
                )
                gare.id_gare = cursor.fetchone()["id_gare"]
        except Exception as e:
            logger.error(f"Erreur base de données dans GareDAO.creer_ou_mettre_a_jour : {e}")
            raise
        return gare
