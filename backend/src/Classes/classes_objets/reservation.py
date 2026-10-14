from client import Client
from trajet import Trajet


class Reservation:
    """Modélise les réservations de trajet des clients."""

    def __init__(self, id_reservation: int, client: Client, trajet: Trajet, place: str, classe: int, prix: float):
        self.id_reservation = id_reservation
        self.client = client
        self.trajet = trajet
        self.place = place
        self.classe = classe
        self.prix = prix

    def __str__(self):
        return f"La réservation #{self.id_reservation} du client #{self.client} pour le trajet #{self.trajet}, en {self.classe} à la place{self.place} a coûté {self.prix} euros"
