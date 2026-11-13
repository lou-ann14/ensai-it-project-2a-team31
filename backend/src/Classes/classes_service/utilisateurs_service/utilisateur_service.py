import secrets

from psycopg2.errors import UniqueViolation

from src.Classes.classes_DAO.utilisateur_DAO import UtilisateurDAO
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.utils.log_utils import log
from src.utils.securite import hash_password


class UtilisateurService:

    @log
    def creer_compte(self, nom : str, mdp: str) -> Utilisateur | None:
        """Créer un compte utilisateur
        Param:
            nom (str): nom d'utilisateur
            mdp (str): mot de passe
        Returns:
            Utilisateur créer ou None sinon.
        Raises:
            ValueError: si le nom d'utilisateur est déjà pris (contrainte UNIQUE de la base,
                qui protège aussi contre deux inscriptions simultanées avec le même nom)
        """
        utilisateur = Utilisateur(
            nom_utilisateur=nom,
            mdp=hash_password(mdp, nom),
            grade="CLIENT"
        )
        try:
            return utilisateur if UtilisateurDAO().creer(utilisateur) else None
        except UniqueViolation:
            raise ValueError("Ce nom d'utilisateur est déjà pris.")


    @log
    def changer_mdp(self, id_utilisateur: int, ancien_mdp: str, nouveau_mdp: str) -> bool:
        """Change le mot de passe d'un utilisateur après avoir vérifié l'ancien
        Param:
            id_utilisateur (int): l'id de l'utilisateur.
            ancien_mdp (str): le mot de passe actuel, en clair.
            nouveau_mdp (str): le nouveau mot de passe, en clair.
        Returns:
            True si le mot de passe a été changé, False si l'utilisateur n'existe pas
            ou si l'ancien mot de passe est incorrect.
        """
        utilisateur = UtilisateurDAO().trouver_par_id(id_utilisateur)
        if utilisateur is None:
            return False

        # Le sel est le nom d'utilisateur, comme dans creer_compte et login
        nom = utilisateur.nom_utilisateur
        if utilisateur.mdp != hash_password(ancien_mdp, nom):
            return False

        return UtilisateurDAO().modifier_mdp(id_utilisateur, hash_password(nouveau_mdp, nom))

    @log
    def rechercher(self, nom: str | None = None, id_utilisateur: int | None = None) -> Utilisateur | None:
        """Recherche un utilisateur à l'aide de son id ou de son nom
        Param:
            nom (str): le nom de l'utilisateur recherché.
            id_utilisateur (int): l'id de l'utilisateur recherché.
        Returns:

        """
        res = None
        if nom:
            res = UtilisateurDAO().trouver_par_nom_utilisateur(nom)
            return res
        elif id_utilisateur:
            res = UtilisateurDAO().trouver_par_id(id_utilisateur)
            return res
        else:
            return res

    @log
    def modifier(self, utilisateur: Utilisateur):
        return utilisateur if UtilisateurDAO().modifier(utilisateur) else None
    
    @log
    def login(self, nom: str, mdp: str):
        utilisateur = UtilisateurDAO().login(nom=nom, mdp=hash_password(mdp, nom))
        if utilisateur:
            utilisateur.token=secrets.token_urlsafe(32)
            self.modifier(utilisateur=utilisateur)
            return utilisateur
        return None