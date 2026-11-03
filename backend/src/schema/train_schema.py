from pydantic import BaseModel


class TrainBaseModel(BaseModel):

    type_train: str
    places_initiales: list[int, int]
    num_train: int