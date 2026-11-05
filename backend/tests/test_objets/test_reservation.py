import re
from datetime import datetime

import pytest
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.reservation import Reservation
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_objets.utilisateurs.client import Client

client = Client("0000", "jaimelestrains", id=4)
ligne = Ligne(
    Gare("Matabiau", "Toulouse", "stop_area:SNCF:87611004", 1),
    Gare("Montparnasse", "Paris", "stop_area:SNCF:87391003", 2),
    id_ligne=14,
)
train = Train("TGV", 120, 400, 8541, id_train=3)
trajet = Trajet(datetime(2026, 11, 3, 11, 54), datetime(2026, 11, 3, 17, 0), ligne, train, 150.0, id_trajet=22)


class TestReservation:
    @pytest.mark.parametrize(
        "params, erreur, message_erreur",
        [
            (
                {"client": 42},
                TypeError,
                "Le client doit être de type Client."
            ),
            (
                {"trajet": 42},
                TypeError,
                "Le trajet doit être de type Trajet."
            ),
            (
                {"place": 67},
                TypeError,
                "La place doit être une chaîne de caractères."
            ),
            (
                {"classe": "2"},
                TypeError,
                "La classe doit être un entier."
            ),
            (
                {"prix": "3600€"},
                TypeError,
                "Le prix doit être un flottant."
            )
        ]
    )
    def test_init_reservation(self, params, erreur, message_erreur):
        dico = {
            "id_reservation": 45,
            "client": client,
            "trajet": trajet,
            "place": "67",
            "classe": 1,
            "prix": 180.0}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Reservation(**dico)

    def test_init_reservation_ok(self):
        reservation = Reservation(client, trajet, "67", 1, 180.0, id_reservation=45)
        assert reservation.client is client
        assert reservation.trajet is trajet
        assert reservation.prix == 180.0

    def test_str_reservation(self):
        reservation = Reservation(client, trajet, "67", 1, 200.0, id_reservation=22)
        texte = str(reservation)
        assert texte.startswith("La réservation #22 du client")
        assert "a coûté 200.0 euros" in texte
