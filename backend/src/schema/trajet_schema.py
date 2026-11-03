from datetime import datetime

from pydantic import BaseModel
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train


class TrajetBaseModel(BaseModel):

    id_trajet: int
    heure_depart: datetime
    heure_arrivee: datetime
    ligne: Ligne
    train: Train
    tarif_base: float