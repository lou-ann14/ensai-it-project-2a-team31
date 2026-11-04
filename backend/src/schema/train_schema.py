from pydantic import BaseModel, ConfigDict


class TrainBaseModel(BaseModel):

    type_train: str
    places_premieres: int
    places_secondes: int
    num_train: int


class TrainReponseModel(TrainBaseModel):
    """Train renvoyé par l'API, avec l'id_train nécessaire pour créer un trajet."""

    # Permet de construire le modèle directement depuis un objet Train
    model_config = ConfigDict(from_attributes=True)

    id_train: int
