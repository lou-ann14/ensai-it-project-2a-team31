from datetime import datetime

from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train


class Trajet:
    """Classe qui modélise un trajet et ses différentes caractéristiques.

    Param:
    ------
    id_trajet: int | None
        identifiant du trajet (None tant qu'il n'est pas enregistré en base)
    heure_depart: datetime
        date et heure de départ
    heure_arrivee: datetime
        date et heure d'arrivée
    ligne: Ligne
        la ligne sur laquelle le trajet est effectué
    train: Train
        le train utilisé pour ce trajet
    tarif_base: float
        le prix de base du trajet
    """

    def __init__(
        self,
        id_trajet: int | None,
        heure_depart: datetime,
        heure_arrivee: datetime,
        ligne: Ligne,
        train: Train,
        tarif_base: float,
    ):
        self.id_trajet = id_trajet
        self.heure_depart = heure_depart
        self.heure_arrivee = heure_arrivee
        self.ligne = ligne
        self.train = train
        self.tarif_base = tarif_base

    @property
    def horaires(self) -> str:
        return f"{self.heure_depart}, {self.heure_arrivee}"

    def __str__(self):
        return (
            f"Le trajet #{self.id_trajet} du train #{self.train.id_train} "
            f"sur la ligne #{self.ligne.id_ligne} au prix initial de {self.tarif_base} euros "
            f"a pour horaires: {self.horaires}"
        )