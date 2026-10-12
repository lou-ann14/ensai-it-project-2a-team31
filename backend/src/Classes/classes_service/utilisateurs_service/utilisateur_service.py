from classes_DAO import UtilisateursDAO
from classes.classes_objets.gare import Gare  # Correction: retrait du .py
from datetime import datetime

# Il faudra importer vos classes métiers ici (chemins à adapter selon votre projet)
from client import Client
from collaborateur import Collaborateur
from administrateur import Administrateur

class UtilisateurService:
    """Classe qui gère les actions des utilisateurs."""
    
    def __init__(self):
        self.dao = UtilisateursDAO()

    def creer_compte(self, nom_utilisateur: str, mdp: str, role: str):
        if self.rechercher(nom_utilisateur=nom_utilisateur, id=None):
            raise ValueError("Ce nom d'utilisateur est déjà utilisé.")
        
        nouvel_id = self.dao.generer_nouvel_id() 
        
        if role == "CLIENT":
            nouvel_utilisateur = Client(id=nouvel_id, mdp=mdp, nom_utilisateur=nom_utilisateur)
        elif role == "COLLABORATEUR":
            nouvel_utilisateur = Collaborateur(id=nouvel_id, mdp=mdp, nom_utilisateur=nom_utilisateur)
        elif role == "ADMIN":
            nouvel_utilisateur = Administrateur(id=nouvel_id, mdp=mdp, nom_utilisateur=nom_utilisateur)
        else:
            raise ValueError("Rôle invalide.")
            
        # !!!fausse base de données!!!
        self.dao.sauvegarder(nouvel_utilisateur)
        return nouvel_utilisateur

    def recherche_trajet(self, gare_depart: Gare, gare_arrivee: Gare, date: datetime):
        pass

    def recherche_gare(self, nom: str | None, ville: str | None):
        pass

    def changer_mdp(self, id_utilisateur: int, ancien_mdp: str, nouveau_mdp: str):
        utilisateur = self.rechercher(nom_utilisateur=None, id=id_utilisateur)
        
        if not utilisateur:
            raise ValueError("Utilisateur introuvable.")
            
        if utilisateur.mdp != ancien_mdp:
            raise ValueError("L'ancien mot de passe est incorrect.")
            
        utilisateur.mdp = nouveau_mdp
        self.dao.mettre_a_jour(utilisateur)
        return True

    def rechercher(self, nom_utilisateur: str | None, id: int | None = None):
        if id is not None:
            return self.dao.get_by_id(id)
        elif nom_utilisateur is not None:
            return self.dao.get_by_nom(nom_utilisateur)
        return None


