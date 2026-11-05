import re

import pytest
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne


class TestLigne:
    @pytest.mark.parametrize(
        "params, erreur, message_erreur",
        [
            (
                {"id_ligne": "Matabiau-Rennes"},
                TypeError,
                "L'id de la ligne doit être un entier."
            ),
            (
                {"gare_depart": 42},
                TypeError,
                "La gare de départ doit être de type Gare"
            ),
            (
                {"gare_arrivee": 42},
                TypeError,
                "La gare d'arrivée doit être de type Gare."
            )
        ]
    )
    def test_init_ligne(self, params, erreur, message_erreur):
        gare_depart = Gare("Matabiau", "Toulouse", id_gare=1)
        gare_arrivee = Gare("Gare de Rennes", "Rennes", id_gare=2)
        dico = {
            "id_ligne": 1,
            "gare_depart": gare_depart,
            "gare_arrivee": gare_arrivee}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Ligne(**dico)

    @pytest.mark.parametrize(
        "id_ligne, gare_depart, gare_arrivee, resultat_attendu",
        [(
            1,
            Gare("Matabiau", "Toulouse", id_gare=1),
            Gare("Gare de Rennes", "Rennes", id_gare=2),
            "la gare de depart de la ligne #1 est : #Matabiau et la gare d'arrivée est : # Gare de Rennes"
        )]
    )
    def test_str_ligne(self, id_ligne, gare_depart, gare_arrivee, resultat_attendu):
        assert str(Ligne(gare_depart, gare_arrivee, id_ligne=id_ligne)) == resultat_attendu
