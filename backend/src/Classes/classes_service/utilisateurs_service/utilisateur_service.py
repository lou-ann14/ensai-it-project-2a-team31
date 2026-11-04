import secrets

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
        """
        utilisateur = Utilisateur(
            nom_utilisateur=nom,
            mdp=hash_password(mdp, nom),
            grade="CLIENT"
        )
        return utilisateur if UtilisateurDAO().creer(utilisateur) else None


    @log
    def changer_mdp(self, id_utilisateur: int, ancien_mdp: str, nouveau_mdp: str) -> bool:
        check_query = "SELECT id FROM utilisateurs WHERE id = %s AND mdp = %s;"
        update_query = "UPDATE utilisateurs SET mdp = %s WHERE id = %s;"
        with self.conn.cursor() as cur:
            cur.execute(check_query, (id_utilisateur, ancien_mdp))
            if cur.fetchone():
                cur.execute(update_query, (nouveau_mdp, id_utilisateur))
                self.conn.commit()
                return True
            return False

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