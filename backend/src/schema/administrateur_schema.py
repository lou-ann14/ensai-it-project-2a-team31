from pydantic import BaseModel, ConfigDict


class UtilisateurCreationModel(BaseModel):
    """Données envoyées par l'administrateur pour créer un utilisateur.
    L'id n'est pas demandé : il est généré par la base (SERIAL)."""

    nom_utilisateur: str
    mdp: str
    grade: str = "CLIENT"


class UtilisateurReponseModel(BaseModel):
    """Utilisateur renvoyé par l'API (sans le mot de passe)."""

    # Permet de construire le modèle directement depuis un objet Utilisateur
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_utilisateur: str
    grade: str
