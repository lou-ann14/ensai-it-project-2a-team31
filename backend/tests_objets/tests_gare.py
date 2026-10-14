import re

import pytest
from src.Classes.classes_objets.trajet import Gare


class TestGare:
    @pytest.mark.parametrize(
    "params, erreur, message_erreur",
    [
        (
            {"id_gare": "Montparnasse"},
            TypeError,
            "L'identifiant de la gare doit être un entier."
        ),
        (
            {"nom": 42},
            TypeError,
            "Le nom doit être une caîne de caractères."
        ),
        (
            {"ville": 42},
            TypeError,
            "La ville doit être une caîne de caractères."
        )
    ]
    )
    def test_init_gare(params, erreur, message_erreur):
        dico = {
            "1",
            "Montparnasse",
            "Paris"}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Gare(**dico)



    def test_str_gare(params, erreur, message_erreur):
