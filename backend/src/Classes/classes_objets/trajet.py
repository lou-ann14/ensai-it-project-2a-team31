from datetime import datetime

from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train


class Trajet:
    """Modélise la classe Trajet, qui permet de gérer les différentes caracteristiques des trajets.

    Params
    ------
    heure_depart: datetime
        Heure de départ du trajet
    heure_arrivee: datetime
        Heure d'arrivée du trajet
    ligne: Ligne
        Ligne sur laquelle à lieu le trajet
    train: Train
        Train utilisé pour le trajet
    tarif_base: float
        Tarif minimum pour le trajet effectué
    temps_trajet: int | None = None
        Temps que prends le trajet
    id_trajet: int | None = None
        id du trajet dans la BDD
    """
    def __init__(self, heure_depart: datetime, heure_arrivee: datetime, ligne: Ligne, train: Train, tarif_base: float, id_trajet: int | None = None, temps_trajet: int | None = None):
        if not isinstance(heure_depart, datetime):
            raise TypeError("L'heure de départ doit être de type datetime.")
        if not isinstance(heure_arrivee, datetime):
            raise TypeError("L'heure d'arrivée doit être de type datetime.")
        if not isinstance(ligne, Ligne):
            raise TypeError("La ligne doit être de type Ligne")
        if not isinstance(train, Train):
            raise TypeError("Le train doit être de type Train.")
        if not isinstance(tarif_base, float):
            raise TypeError("Le tarif de base doit être un nombre flottant.")

        self.id_trajet = id_trajet
        self.heure_depart = heure_depart
        self.heure_arrivee = heure_arrivee
        self.horaires = f"{heure_depart}, {heure_arrivee}"
        self.ligne = ligne
        self.train = train
        self.tarif_base = tarif_base
        self.temps_trajet = temps_trajet

    def __str__(self):
        id_train = self.train.id_train if self.train else None
        return f"Le trajet #{self.id_trajet} du train #{id_train} sur la ligne #{self.ligne.id_ligne} au prix initial de {self.tarif_base} euros a pour horaires: {self.horaires}"
