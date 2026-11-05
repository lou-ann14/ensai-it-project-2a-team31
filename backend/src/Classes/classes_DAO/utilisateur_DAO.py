from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.utils.db_connexion import DBConnexion
from src.utils.log_utils import get_logger, log

logger = get_logger(__name__)


class UtilisateurDAO:
    """
    Classe qui interagit avec la base de données pour les objets de type Utilisateur
    """

    @log
    def creer(self, utilisateur: Utilisateur) -> Utilisateur:
        """
        Enregistre un nouvel utilisateur dans la base de données.
        La date d'inscription est fixée à la date du jour par la base.

        Param:
        ------
        utilisateur: Utilisateur
            l'utilisateur à créer (son id est None avant l'insertion)

        Return:
        ------
        Utilisateur
            le même utilisateur, avec son id renseigné

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO utilisateurs(nom_utilisateur, mdp, grade, date_inscription)  "
                    "VALUES (%(nom_utilisateur)s, %(mdp)s, %(grade)s, CURRENT_DATE)            "
                    "RETURNING id                                                             ",
                    {
                        "nom_utilisateur": utilisateur.nom_utilisateur,
                        "mdp": utilisateur.mdp,
                        "grade": utilisateur.grade,
                    },
                )
                utilisateur.id = cursor.fetchone()["id"]
        except Exception as e:
            logger.error(f"Erreur base de données dans UtilisateurDAO.creer : {e}")
            raise

        return utilisateur

    @log
    def modifier(self, utilisateur: Utilisateur) -> bool:
        """
        Met à jour les informations d'un utilisateur existant
        (nom d'utilisateur, mot de passe, grade et token d'accès).

        Param:
        ------
        utilisateur: Utilisateur
            l'utilisateur contenant les nouvelles données (identifié par son id)

        Return:
        ------
        bool
            True si la modification a réussi, False si l'utilisateur n'existe pas

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE utilisateurs                               "
                    "   SET nom_utilisateur = %(nom_utilisateur)s,     "
                    "       mdp             = %(mdp)s,                 "
                    "       grade           = %(grade)s,              "
                    "       token_acces     = %(token_acces)s         "
                    " WHERE id = %(id)s                                ",
                    {
                        "nom_utilisateur": utilisateur.nom_utilisateur,
                        "mdp": utilisateur.mdp,
                        "grade": utilisateur.grade,
                        "id": utilisateur.id,
                        "token_acces": utilisateur.token
                    },
                )
                nb_lignes_modifiees = cursor.rowcount
        except Exception as e:
            logger.error(f"Erreur base de données dans UtilisateurDAO.modifier : {e}")
            raise

        return nb_lignes_modifiees > 0

    @log
    def modifier_mdp(self, id: int, mdp: str) -> bool:
        """
        Met à jour uniquement le mot de passe d'un utilisateur.

        Param:
        ------
        id: int
            l'identifiant de l'utilisateur
        mdp: str
            le nouveau mot de passe, déjà haché

        Return:
        ------
        bool
            True si la modification a réussi, False si l'utilisateur n'existe pas

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE utilisateurs      "
                    "   SET mdp = %(mdp)s     "
                    " WHERE id = %(id)s       ",
                    {"mdp": mdp, "id": id},
                )
                nb_lignes_modifiees = cursor.rowcount
        except Exception as e:
            logger.error(f"Erreur base de données dans UtilisateurDAO.modifier_mdp : {e}")
            raise

        return nb_lignes_modifiees > 0

    @log
    def trouver_par_nom_utilisateur(self, nom_utilisateur: str) -> Utilisateur | None:
        """
        Récupère un utilisateur par son nom d'utilisateur.

        Param:
        ------
        nom_utilisateur: str
            le nom d'utilisateur recherché

        Return:
        ------
        Utilisateur | None
            l'utilisateur trouvé, ou None s'il n'existe pas

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nom_utilisateur, mdp, grade, token_acces "
                    "  FROM utilisateurs                               "
                    " WHERE nom_utilisateur = %(nom_utilisateur)s      ",
                    {"nom_utilisateur": nom_utilisateur},
                )
                utilisateur_bdd = cursor.fetchone()
        except Exception as e:
            logger.error(f"Erreur base de données dans UtilisateurDAO.trouver_par_nom_utilisateur : {e}")
            raise

        utilisateur = None
        if utilisateur_bdd:
            utilisateur = Utilisateur(
                id=utilisateur_bdd["id"],
                mdp=utilisateur_bdd["mdp"],
                nom_utilisateur=utilisateur_bdd["nom_utilisateur"],
                grade=utilisateur_bdd["grade"],
                token_acces=utilisateur_bdd["token_acces"],
            )
        return utilisateur

    @log
    def trouver_par_id(self, id: int) -> Utilisateur | None:
        """
        Récupère un utilisateur par son identifiant.

        Param:
        ------
        id: int
            l'identifiant unique de l'utilisateur

        Return:
        ------
        Utilisateur | None
            l'utilisateur trouvé, ou None s'il n'existe pas

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nom_utilisateur, mdp, grade, token_acces "
                    "  FROM utilisateurs                               "
                    " WHERE id = %(id)s                                ",
                    {"id": id},
                )
                utilisateur_bdd = cursor.fetchone()
        except Exception as e:
            logger.error(f"Erreur base de données dans UtilisateurDAO.trouver_par_id : {e}")
            raise

        utilisateur = None
        if utilisateur_bdd:
            utilisateur = Utilisateur(
                id=utilisateur_bdd["id"],
                mdp=utilisateur_bdd["mdp"],
                nom_utilisateur=utilisateur_bdd["nom_utilisateur"],
                grade=utilisateur_bdd["grade"],
                token_acces=utilisateur_bdd["token_acces"],
            )
        return utilisateur
    
    @log
    def trouver_par_token(self, token: str) -> Utilisateur | None:
        """
        Récupère un utilisateur à partir de son token d'accès.

        Param:
        ------
        token: str
            le token d'accès de l'utilisateur

        Return:
        ------
        Utilisateur | None
            l'utilisateur trouvé, ou None si le token est vide ou inconnu

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        if not token:
            return None
        
        res = None
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM utilisateurs "
                    "WHERE token_acces = %(token)s;",
                    {"token":token},
                )
                res = cursor.fetchone()
        except Exception as e:
            logger.error(f"Erreur base de données dans UtilisateurDAO.trouver_par_token : {e}")
            raise

        utilisateur = None
        if res:
            utilisateur = Utilisateur(
                nom_utilisateur=res["nom_utilisateur"],
                mdp=res["mdp"],
                grade=res["grade"],
                token_acces=res["token_acces"],
                id=res["id"],
            )
        return utilisateur

    @log
    def login(self, nom: str, mdp: str) -> Utilisateur | None:
        """
        Vérifie un couple nom d'utilisateur / mot de passe.

        Param:
        ------
        nom: str
            le nom d'utilisateur
        mdp: str
            le mot de passe de l'utilisateur

        Return:
        ------
        Utilisateur | None
            l'utilisateur connecté, ou None si le nom ou le mot de passe est incorrect

        Raises:
        ------
        psycopg2.Error
            en cas d'erreur lors de l'accès à la base de données
            (l'erreur est écrite dans les logs puis relancée)
        """
        res = None
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM utilisateurs "
                    "WHERE nom_utilisateur = %(nom_utilisateur)s "
                    "AND mdp = %(mdp)s;",
                    {"nom_utilisateur": nom,
                    "mdp": mdp
                    },
                )
                res = cursor.fetchone()
        except Exception as e:
            logger.error(e)
            raise
        utilisateur = None
        if res:
            utilisateur = Utilisateur(
                nom_utilisateur=res["nom_utilisateur"],
                mdp=res["mdp"],
                grade=res["grade"],
                token_acces=res["token_acces"],
                id=res["id"]
            )
        return utilisateur