from pydantic import BaseModel
from src.Classes.classes_objets.gare import Gare


class LigneBaseModel(BaseModel):

    id_gare: int
    gare_depart: Gare
    gare_arrivee: Gare