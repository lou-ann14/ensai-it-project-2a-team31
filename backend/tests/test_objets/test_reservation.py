import datetime
import re

import pytest
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.reservation import Reservation
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_objets.utilisateurs.client import Client


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
                "Le trajet doit être de type trajet."
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
        client = Client.__init__(4, "0000", "jaimelestrains")
        heure_depart = datetime(2026, 11, 3, 11, 54)
        heure_arrivee = datetime(2026, 11, 3, 17)
        gare_depart = Gare.__init__(1, "Matabiau", "Toulouse")
        gare_arrivee = Gare.__init__(2, "Montparnasse", "Paris")
        ligne = Ligne.__init__(14, gare_depart, gare_arrivee)
        train = Train.__init__("TGV", [120, 400])
        trajet = Trajet.__init__(22, heure_depart, heure_arrivee, ligne, train, 150.0)
        dico = {
            "id_reservation": 45,
            "client": client,
            "trajet": trajet,
            "place": 67,
            "classe": 1,
            "prix": 180.0}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Reservation(**dico)

    @pytest.mark.parametrize(
        "id_reservation, client, trajet, place, classe, prix",
        [("22", "Alice", "Matabiau-Montparnasse", "67", "1", "200.0", "La réservation 22 du client Alice pour le trajet Matabiau-Montparnasse, en 1 à la place 67 a coûté 200.0 euros")]
    )
    def test_str_reservation(self, id_reservation, client, trajet, place, classe, prix, resultat_attendu):
        assert Reservation.__str__() == resultat_attendu
