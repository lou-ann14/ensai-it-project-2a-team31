from classes_DAO import utilisateurs_DAO
from classes.classes_objets.gare.py import gare

class UtilisateurService:
    """classe qui gère les actions des utilisateurs
    """
    def creer_compte(self, nom_utilisateur: str, mdp: str, role: str):
        pass

    def recherche_trajet(self, gare_depart: gare, gare_arrivee: gare, date: datetime):
        pass

    def recherche_gare(self, nom: str | None, ville: str | None):
        pass
    def changer_mdp(self, id_utilisateur: int, ancien_mdp: str, nouveau_mdp: str):
        pass
    def rechercher(self, nom_utilisateur: str | None, id: int):
        pass


