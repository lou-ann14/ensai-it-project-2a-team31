from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_objets.utilisateurs.client import Client


class Reservation:
    """Modélise la classe Réservation, qui permet de gérer les réservations des clients.

    Params
    ------
    client: Client
        Client à qui appartient la réservation
    trajet: Trajet
        Trajet sur lequel porte la réservation
    place: str
        Place de la réservation
    classe: int
        Classe dans laquelle le client se trouve
    prix: float
        prix de la réservation
    id_réservation: int | None = None
        id de la réservation dans la BDD
    """
    def __init__(self, client: Client, trajet: Trajet, place: str, classe: int, prix: float, id_reservation: int | None = None):
        if id_reservation is not None and not isinstance(id_reservation, int):
            raise TypeError("L'identifiant de la réservation doit être un entier.")
        if not isinstance(client, Client):
            raise TypeError("Le client doit être de type Client.")
        if not isinstance(trajet, Trajet):
            raise TypeError("Le trajet doit être de type Trajet.")
        if not isinstance(place, str):
            raise TypeError("La place doit être une chaîne de caractères.")
        if not isinstance(classe, int):
            raise TypeError("La classe doit être un entier.")
        if not isinstance(prix, float):
            raise TypeError("Le prix doit être un flottant.")

        self.id_reservation = id_reservation
        self.client = client
        self.trajet = trajet
        self.place = place
        self.classe = classe
        self.prix = prix

    def __str__(self):
        return f"La réservation #{self.id_reservation} du client #{self.client} pour le trajet #{self.trajet}, en {self.classe} à la place{self.place} a coûté {self.prix} euros"
