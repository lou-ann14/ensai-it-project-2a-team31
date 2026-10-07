from classes_DAO import UtilisateursDAO
from classes.classes_objets.gare.py import Gare
from datetime import datetime

class UtilisateurService:
    """classe qui gère les actions des utilisateurs
    """
    def creer_compte(self, nom_utilisateur: str, mdp: str, role: str):
        pass

    def recherche_trajet(self, gare_depart: Gare, gare_arrivee: Gare, date: datetime):
        pass

    def recherche_gare(self, nom: str | None, ville: str | None):
        pass
    def changer_mdp(self, id_utilisateur: int, ancien_mdp: str, nouveau_mdp: str):
        pass
    def rechercher(self, nom_utilisateur: str | None, id: int):
        pass


