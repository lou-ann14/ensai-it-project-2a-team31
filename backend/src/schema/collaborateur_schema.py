from datetime import datetime

from pydantic import BaseModel, ConfigDict
from src.schema.gare_schema import GareReponseModel
from src.schema.utilisateur_schema import TrajetReponseModel


class LigneReponseModel(BaseModel):
    """Ligne renvoyée par l'API, avec ses deux gares."""

    # Permet de construire le modèle directement depuis un objet Ligne
    model_config = ConfigDict(from_attributes=True)

    id_ligne: int
    gare_depart: GareReponseModel
    gare_arrivee: GareReponseModel


class TrajetListeModel(TrajetReponseModel):
    """Trajet de la liste du collaborateur, avec la ligne nécessaire pour le modifier."""

    ligne: LigneReponseModel


class LigneCreeeModel(BaseModel):
    """Réponse renvoyée après la création d'une ligne."""

    message: str
    id_ligne: int


class TrajetCreationModel(BaseModel):
    """Données envoyées par un collaborateur pour créer un trajet."""

    id_ligne: int
    id_train: int
    heure_depart: datetime
    tarif_base: float


class TrajetCreeModel(BaseModel):
    """Réponse renvoyée après la création d'un trajet."""

    message: str
    id_trajet: int
    heure_arrivee: datetime
    temps_trajet: int  # en minutes


class LigneModifieeModel(LigneCreeeModel):
    """Réponse renvoyée après la modification d'une ligne."""


class TrajetModificationModel(TrajetCreationModel):
    """Nouvelles informations d'un trajet (l'arrivée est recalculée avec l'API SNCF)."""


class TrajetModifieModel(TrajetCreeModel):
    """Réponse renvoyée après la modification d'un trajet."""


class MessageModel(BaseModel):
    """Réponse contenant uniquement un message de confirmation."""

    message: str
