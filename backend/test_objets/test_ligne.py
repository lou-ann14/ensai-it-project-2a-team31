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
                {"id_gare_depart": "Matabiau"},
                TypeError,
                "L'identifiant de la gare de départ doit être un entier."
            ),
            (
                {"id_gare_arrivee": "Rennes"},
                TypeError,
                "L'identifiant de la gare d'arrivée doit être un entier."
            )
        ]
    )
    def test_init_ligne(self, params, erreur, message_erreur):
        dico = {
            "id_ligne": 1,
            "id_gare_depart": 1,
            "id_gare_arrivee": 2}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Ligne(**dico)

    @pytest.mark.parametrize(
        "id_ligne, id_gare_depart, id_gare_arrivee, resultat_attendu",
        [(1, 1, 2, "la gare de depart de la ligne : 1 est 1 et la gare d'arrivée est : 2")]
        )
    def test_str_ligne(self, id_ligne, id_gare_depart, id_gare_arrivee, resultat_attendu):
        assert str(Ligne(id_ligne, id_gare_depart, id_gare_arrivee)) == resultat_attendu
