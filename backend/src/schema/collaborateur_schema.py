from datetime import datetime

from pydantic import BaseModel


class LigneCreationModel(BaseModel):
    """Données envoyées par un collaborateur pour créer une ligne."""

    gare_depart_id: int
    gare_arrivee_id: int
    id_collaborateur: int


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


class LigneModificationModel(BaseModel):
    """Nouvelles gares d'une ligne."""

    gare_depart_id: int
    gare_arrivee_id: int


class LigneModifieeModel(LigneCreeeModel):
    """Réponse renvoyée après la modification d'une ligne."""


class TrajetModificationModel(TrajetCreationModel):
    """Nouvelles informations d'un trajet (l'arrivée est recalculée avec l'API SNCF)."""


class TrajetModifieModel(TrajetCreeModel):
    """Réponse renvoyée après la modification d'un trajet."""


class MessageModel(BaseModel):
    """Réponse contenant uniquement un message de confirmation."""

    message: str
