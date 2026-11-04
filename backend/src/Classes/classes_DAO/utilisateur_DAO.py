from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.utils.db_connexion import DBConnexion
from src.utils.log_utils import get_logger, log

logger = get_logger(__name__)

class UtilisateurDAO:
    """Classe qui interagit avec la base de données pour les objets de type Utilisateur"""

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
            l'objet Utilisateur créé, avec son id renseigné
        """
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

        return utilisateur

    @log
    def modifier(self, utilisateur: Utilisateur) -> bool:
        """
        Met à jour les informations d'un utilisateur existant
        (nom d'utilisateur, mot de passe et rôle).

        Param:
        ------
        utilisateur: Utilisateur
            l'objet contenant les nouvelles données (identifié par son id)

        Return:
        ------
        bool
            True si la modification a réussi, False sinon
        """
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE utilisateurs                               "
                "   SET nom_utilisateur = %(nom_utilisateur)s,     "
                "       mdp             = %(mdp)s,                 "
                "       grade           = %(grade)s               "
                "       token_acces     = %(token_acces)s"
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
        Utilisateur
            l'objet Utilisateur trouvé, ou None s'il n'existe pas
        """
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, nom_utilisateur, mdp, grade             "
                "  FROM utilisateurs                               "
                " WHERE nom_utilisateur = %(nom_utilisateur)s      ",
                {"nom_utilisateur": nom_utilisateur},
            )
            utilisateur_bdd = cursor.fetchone()

        utilisateur = None
        if utilisateur_bdd:
            utilisateur = Utilisateur(
                id=utilisateur_bdd["id"],
                mdp=utilisateur_bdd["mdp"],
                nom_utilisateur=utilisateur_bdd["nom_utilisateur"],
                grade=utilisateur_bdd["grade"],
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
        Utilisateur
            l'objet Utilisateur trouvé, ou None s'il n'existe pas
        """
        with DBConnexion().connexion as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, nom_utilisateur, mdp, grade             "
                "  FROM utilisateurs                               "
                " WHERE id = %(id)s                                ",
                {"id": id},
            )
            utilisateur_bdd = cursor.fetchone()

        utilisateur = None
        if utilisateur_bdd:
            utilisateur = Utilisateur(
                id=utilisateur_bdd["id"],
                mdp=utilisateur_bdd["mdp"],
                nom_utilisateur=utilisateur_bdd["nom_utilisateur"],
                grade=utilisateur_bdd["grade"],
            )
        return utilisateur
    
    @log
    def trouver_par_token(self, token: str) -> Utilisateur | None:
        """Trouve un utilisateur à partir de son token.
        Param:
            token (str): le token à partir duquel faire la recherche
        Returns:
            Utilisateur : l'utilisateur trouvé, et None sinon.
        """
        if not token:
            return None
        
        res = None
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM utilisateurs"
                    "WHERE token_acces = %(token)s;",
                    {"token":token},
                )
                res = cursor.fetchone()
        except Exception as e:
            logger.error(f"Error finding player by token: {e}")
            raise

        utilisateur = None
        if res:
            utilisateur = Utilisateur(
                nom_utilisateur=res["nom_utilisateur"],
                mdp=res["mdp"],
                grade=res["grade"],
                token_acces=res["token_acces"]
            )
        return utilisateur

    @log
    def login(self, nom: str, mdp: str) -> Utilisateur | None:
        """Permet de se login avec son nom et un mot de passe.
        Param:
            nom (str): le nom d'utilisateur.
            mdp (str): le mot de passe de l'utilisateur.
        Returns:
            L'utilisateur connecté, None sinon.
        """
        res = None
        try:
            with DBConnexion().connexion as connection, connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM utilisateurs"
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