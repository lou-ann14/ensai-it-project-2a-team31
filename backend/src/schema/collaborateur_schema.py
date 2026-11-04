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
    heure_arrivee: datetime
    tarif_base: float


class TrajetCreeModel(BaseModel):
    """Réponse renvoyée après la création d'un trajet."""

    message: str
    id_trajet: int
