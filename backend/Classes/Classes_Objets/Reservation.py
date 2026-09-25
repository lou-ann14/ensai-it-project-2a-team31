from Classes_Objets import Client

from . import Trajet


class Reservation:
    """Modélise les réservations de trajet des clients."""


    def __init__(self, id_reservation: int, id_client: int, id_trajet: int, place: str, classe: int, prix: float):
        self.id_reservation = id_reservation
        self.id_client = id_client
        self.id_trajet = id_trajet
        self.place = place
        self.classe = classe
        self.prix = prix

    def __str__(self):
        return f"La réservation #{self.id_reservation} du client #{self.id_client} pour le trajet #{self.id_trajet}, en {self.classe} à la place{self.place} a coûté {self.prix} euros"
