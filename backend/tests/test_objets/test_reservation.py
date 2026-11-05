import re
from datetime import datetime

import pytest
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.reservation import Reservation
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_objets.utilisateurs.client import Client


def creer_client():
    return Client("0000", "jaimelestrains", id=4)


def creer_trajet():
    ligne = Ligne(
        Gare("Matabiau", "Toulouse", id_gare=1),
        Gare("Montparnasse", "Paris", id_gare=2),
        id_ligne=14,
    )
    train = Train("TGV", 120, 400, 8541, id_train=1)
    return Trajet(datetime(2026, 11, 3, 11, 54), datetime(2026, 11, 3, 17), ligne, train, 150.0, id_trajet=22)


class TestReservation:
    @pytest.mark.parametrize(
        "params, erreur, message_erreur",
        [
            (
                {"id_reservation": "41"},
                TypeError,
                "L'identifiant de la réservation doit être un entier."
            ),
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
                {"place": 42},
                TypeError,
                "La place doit être une chaîne de caractères"
            ),
            (
                {"classe": "2"},
                TypeError,
                "La classe doit être un entier"
            ),
            (
                {"prix": "3600€"},
                TypeError,
                "Le prix doit être un flottant"
            )
        ]
    )
    def test_init_reservation(self, params, erreur, message_erreur):
        dico = {
            "id_reservation": 45,
            "client": creer_client(),
            "trajet": creer_trajet(),
            "place": "67",
            "classe": 1,
            "prix": 180.0}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Reservation(**dico)

    def test_str_reservation(self):
        client = creer_client()
        trajet = creer_trajet()
        reservation = Reservation(client, trajet, "67", 1, 200.0, id_reservation=22)

        assert str(reservation) == (
            f"La réservation #22 du client #{client} pour le trajet #{trajet}, "
            "en 1 à la place 67 a coûté 200.0 euros"
        )
