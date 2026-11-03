from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.utils.db_connexion import DBConnexion


class UtilisateurDAO:
    """Classe qui interagit avec la base de données pour les objets de type Utilisateur"""

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
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
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
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE utilisateurs                               "
                    "   SET nom_utilisateur = %(nom_utilisateur)s,     "
                    "       mdp             = %(mdp)s,                 "
                    "       grade            = %(grade)s                 "
                    " WHERE id = %(id)s                                ",
                    {
                        "nom_utilisateur": utilisateur.nom_utilisateur,
                        "mdp": utilisateur.mdp,
                        "grade": utilisateur.grade,
                        "id": utilisateur.id,
                    },
                )
                nb_lignes_modifiees = cursor.rowcount

        return nb_lignes_modifiees > 0

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
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
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
        with DBConnexion().connexion as connection:
            with connection.cursor() as cursor:
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
