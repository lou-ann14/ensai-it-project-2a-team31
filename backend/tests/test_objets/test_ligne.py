import re

import pytest
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne

gare_matabiau = Gare("Matabiau", "Toulouse", "stop_area:SNCF:87611004", 1)
gare_rennes = Gare("Gare de Rennes", "Rennes", "stop_area:SNCF:87471003", 2)


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
                "La gare de départ doit être de type Gare."
            ),
            (
                {"gare_arrivee": 42},
                TypeError,
                "La gare d'arrivée doit être de type Gare."
            )
        ]
    )
    def test_init_ligne(self, params, erreur, message_erreur):
        dico = {
            "id_ligne": 1,
            "gare_depart": gare_matabiau,
            "gare_arrivee": gare_rennes}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Ligne(**dico)

    def test_init_ligne_sans_id(self):
        """Une ligne pas encore enregistrée en base n'a pas d'id"""
        assert Ligne(gare_matabiau, gare_rennes).id_ligne is None

    @pytest.mark.parametrize(
        "id_ligne, gare_depart, gare_arrivee, resultat_attendu",
        [(
            1,
            gare_matabiau,
            gare_rennes,
            "la gare de depart de la ligne #1 est : #Matabiau et la gare d'arrivée est : # Gare de Rennes"
        )]
    )
    def test_str_ligne(self, id_ligne, gare_depart, gare_arrivee, resultat_attendu):
        assert str(Ligne(gare_depart, gare_arrivee, id_ligne)) == resultat_attendu
