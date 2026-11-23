from pydantic import BaseModel, ConfigDict


class UtilisateurReponseModel(BaseModel):
    """Utilisateur renvoyé par l'API (sans le mot de passe)."""

    # Permet de construire le modèle directement depuis un objet Utilisateur
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom_utilisateur: str
    grade: str
