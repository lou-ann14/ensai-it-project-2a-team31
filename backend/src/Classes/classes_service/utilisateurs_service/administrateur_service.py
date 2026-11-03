from src.Classes.classes_DAO.utilisateur_DAO import UtilisateurDAO
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.utils.log_utils import log

ROLES_VALIDES = ("CLIENT", "COLLABORATEUR", "ADMIN")


class AdministrateurService:
    """Classe qui gère les actions réservées aux administrateurs"""

    @log
    def gerer_habilitation(self, id_utilisateur: int, nouveau_role: str) -> Utilisateur:
        """
        Modifie le niveau d'habilitation (rôle) d'un utilisateur.

        Param:
        ------
        id_utilisateur: int
            l'identifiant de l'utilisateur à modifier
        nouveau_role: str
            le nouveau rôle (CLIENT, COLLABORATEUR ou ADMIN)

        Return:
        ------
        Utilisateur
            l'utilisateur avec son nouveau rôle

        Raises:
        ------
        ValueError
            si le rôle est invalide, si l'utilisateur n'existe pas
            ou si l'utilisateur est un administrateur
        """
        nouveau_role = nouveau_role.strip().upper() if nouveau_role else ""
        if nouveau_role not in ROLES_VALIDES:
            raise ValueError(f"Le rôle doit être parmi {', '.join(ROLES_VALIDES)}.")

        utilisateur = UtilisateurDAO().trouver_par_id(id_utilisateur)
        if utilisateur is None:
            raise ValueError(f"L'utilisateur #{id_utilisateur} n'existe pas.")
        if utilisateur.role == "ADMIN":
            raise ValueError("Impossible de modifier les droits d'un administrateur.")

        utilisateur.role = nouveau_role
        UtilisateurDAO().modifier(utilisateur)
        return utilisateur

    @log
    def recherche_compte(
        self, nom_utilisateur: str | None = None, id_utilisateur: int | None = None
    ) -> Utilisateur | None:
        """
        Recherche un compte par identifiant ou par nom d'utilisateur.
        Si les deux sont renseignés, l'identifiant est prioritaire.

        Param:
        ------
        nom_utilisateur: str | None
            le nom d'utilisateur recherché (optionnel)
        id_utilisateur: int | None
            l'identifiant recherché (optionnel)

        Return:
        ------
        Utilisateur | None
            l'utilisateur trouvé, ou None s'il n'existe pas

        Raises:
        ------
        ValueError
            si aucun critère n'est renseigné
        """
        if id_utilisateur is not None:
            return UtilisateurDAO().trouver_par_id(id_utilisateur)
        if nom_utilisateur and nom_utilisateur.strip():
            return UtilisateurDAO().trouver_par_nom_utilisateur(nom_utilisateur.strip())
        raise ValueError("Il faut renseigner un identifiant ou un nom d'utilisateur.")
