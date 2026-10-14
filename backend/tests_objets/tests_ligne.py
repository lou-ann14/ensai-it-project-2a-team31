import re

import pytest
from src.Classes.classes_objets.ligne import Ligne


class TestLigne:
    @pytest.mark.parametrize(
        "params, erreur, message_erreur",
        [
            (
                {"id_ligne": "Matabiau-Rennes"},
                TypeError,
                "L'identifiant de la gare doit être un entier."
            ),
            (
                {"gare_depart": 42},
                TypeError,
                "La gare de départ doit être de type Gare."
            ),
            (
                {"gare_arrivee": 42},
                TypeError,
                "La gare d'arrivée doit être de type Gare."
            )
        ]
    )
    def test_init_ligne(params, erreur, message_erreur):
        dico = {
            "1",
            "Matabiau",
            "Rennes"}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Ligne(**dico)

    @pytest.mark.parametrize(
        "id_ligne, gare_depart, gare_arrivee, resultat_attendu",
        [("1", "Matabiau", "Rennes", "la gare de depart de la ligne : 1 est Matabiau et la gare d'arrivée est : Rennes")]
        )
    def test_str_gare(id_ligne, gare_depart, gare_arrivee, resultat_attendu):
        assert Ligne.__str__() == resultat_attendu
