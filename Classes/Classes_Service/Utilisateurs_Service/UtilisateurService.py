from ClassesDAO import UtilisateursDAO


class UtilisateurService:
    """classe qui gère les actions des utilisateurs
    """
    def __init__(self, utilisateur_dao: UtilisateursDAO):
        self.utilisateur_dao = utilisateur_dao
