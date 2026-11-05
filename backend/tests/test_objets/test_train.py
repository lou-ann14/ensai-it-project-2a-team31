import re

import pytest
from src.Classes.classes_objets.train import Train


class TestTrain:
    @pytest.mark.parametrize(
        "params, erreur, message_erreur",
        [
            (
                {"type_train": 42},
                TypeError,
                "Le type de train doit être une chaîne de caractères."
            ),
            (
                {"places_premieres": "120"},
                TypeError,
                "Le nombre de places en première classe doit être un entier."
            ),
            (
                {"places_secondes": [400]},
                TypeError,
                "Le nombre de places en seconde classe doit être un entier."
            ),
            (
                {"num_train": "8541"},
                TypeError,
                "Le numéro du train doit être un entier."
            )
        ]
    )
    def test_init_train(self, params, erreur, message_erreur):
        dico = {
            "type_train": "TGV",
            "places_premieres": 120,
            "places_secondes": 400,
            "num_train": 8541,
            "id_train": 1}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Train(**dico)

    @pytest.mark.parametrize(
        "type_train, places_premieres, places_secondes, num_train, resultat_attendu",
        [("TGV", 120, 400, 8541, "Le train numéro 8541 dispose de 120 places en première classe et 400 en seconde classe, c'est un train TGV")]
    )
    def test_str_train(self, type_train, places_premieres, places_secondes, num_train, resultat_attendu):
        assert str(Train(type_train, places_premieres, places_secondes, num_train)) == resultat_attendu
