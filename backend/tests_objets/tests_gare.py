import re

import pytest
from src.Classes.classes_objets.trajet import Gare


class TestGare:
    @pytest.mark.parametrize(
        "params, erreur, message_erreur",
        [
            (
                {"id_gare": "Matabiau"},
                TypeError,
                "L'identifiant de la gare doit être un entier."
            ),
            (
                {"nom": 42},
                TypeError,
                "Le nom doit être une chaîne de caractères."
            ),
            (
                {"ville": 42},
                TypeError,
                "La ville doit être une chaîne de caractères."
            )
        ]
    )
    def test_init_gare(params, erreur, message_erreur):
        dico = {
            "1",
            "Matabiau",
            "Toulouse"}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Gare(**dico)

    @pytest.mark.parametrize(
        "id_gare, nom, ville, resultat_attendu",
        [("1", "Matabiau", "Toulouse", "La gare Matabiau 1 se situe à Toulouse")]
    )
    def test_str_gare(id_gare, nom, ville, resultat_attendu):
        assert Gare.__str__() == resultat_attendu
