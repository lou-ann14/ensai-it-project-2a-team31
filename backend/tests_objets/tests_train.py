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
                "Le type du train doit être une chaîne de caractères."
            ),
            (
                {"places_initiales": 42},
                TypeError,
                "Les places initiales doit être une liste d'entiers."
            )
        ]
    )
    def test_init_train(params, erreur, message_erreur):
        dico = {
            1,
            "rouge",
            [500, 1000]}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Train(**dico)

    @pytest.mark.parametrize(
        "id_train, type_train, places_initiales, resultat_attendu",
        [(1, "rouge", [500, 1000], "Le train numéro 1 dispose de 500 places en première classe et 1000 en seconde classe, c'est un tgv rouge")]
    )
    def test_str_gare(id_gare, nom, ville, resultat_attendu):
        assert Train.__str__() == resultat_attendu
