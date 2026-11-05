import re

import pytest
from src.Classes.classes_objets.train import Train


class TestTrain:
    @pytest.mark.parametrize(
        "params, erreur, message_erreur",
        [
            (
                {"id_train": "42"},
                TypeError,
                "L'identifiant du train doit être un entier."
            ),
            (
                {"type_train": 42},
                TypeError,
                "Le type de train doit être une chaîne de caractères."
            ),
            (
                {"places_premieres": "500"},
                TypeError,
                "Le nombre de places en première classe doit être un entier."
            ),
            (
                {"places_secondes": "1000"},
                TypeError,
                "Le nombre de places en seconde classe doit être un entier."
            ),
            (
                {"num_train": "1"},
                TypeError,
                "Le numéro du train doit être un entier."
            )
        ]
    )
    def test_init_train(self, params, erreur, message_erreur):
        dico = {
            "id_train": 1,
            "type_train": "rouge",
            "places_premieres": 500,
            "places_secondes": 1000,
            "num_train": 1}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Train(**dico)

    @pytest.mark.parametrize(
        "num_train, type_train, places_premieres, places_secondes, resultat_attendu",
        [(1, "rouge", 500, 1000, "Le train numéro 1 dispose de 500 places en première classe et 1000 en seconde classe, c'est un train rouge")]
    )
    def test_str_train(self, num_train, type_train, places_premieres, places_secondes, resultat_attendu):
        assert str(Train(type_train, places_premieres, places_secondes, num_train)) == resultat_attendu
