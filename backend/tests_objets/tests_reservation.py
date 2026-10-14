import re

import pytest
from src.Classes.classes_objets.reservation import Reservation
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
    def test_init_reservation(params, erreur, message_erreur):
        client = Client.__init__(4, "0000", "jaimelestrains")
        trajet = Trajet.__init__()
        dico = {
            1,
            client,
            "Matabiau",
            "Toulouse"}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Reservation(**dico)

    @pytest.mark.parametrize(
        "id_gare, nom, ville, resultat_attendu",
        [("1", "Matabiau", "Toulouse", "La gare Matabiau 1 se situe à Toulouse")]
    )
    def test_str_gare(id_gare, nom, ville, resultat_attendu):
        assert Gare.__str__() == resultat_attendu
