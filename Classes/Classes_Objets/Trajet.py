from datetime import datetime


class Trajet:

    def __init__(self, id_trajet: int, heure_depart: datetime, heure_arrivee: datetime, id_ligne: int, id_train: int, tarif_base: float):
        self.id_trajet = id_trajet
        self.horaires = f"{heure_depart}, {heure_arrivee}"
        self.id_ligne = id_ligne
        self.id_train = id_train
        self.tarif_base = tarif_base

    def __str__(self):
        return f"Le trajet #{self.id_trajet} du train #{self.id_train} sur la ligne #{self.id_ligne} au prix initial de {self.tarif_base} euros a pour horaires: {self.horaires}"
