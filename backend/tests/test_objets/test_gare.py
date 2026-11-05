import re

import pytest
from src.Classes.classes_objets.gare import Gare


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
            ),
            (
                {"id_sncf": 87471003},
                TypeError,
                "L'identifiant SNCF doit être une chaîne de caractères."
            )
        ]
    )
    def test_init_gare(self, params, erreur, message_erreur):
        dico = {
            "id_gare": 1,
            "nom": "Matabiau",
            "ville": "Toulouse"}
        dico.update(**params)
        with pytest.raises(erreur, match=re.escape(message_erreur)):
            Gare(**dico)

    @pytest.mark.parametrize(
        "id_gare, nom, ville, resultat_attendu",
        [(1, "Matabiau", "Toulouse", "La gare Matabiau 1 se situe à Toulouse")]
    )
    def test_str_gare(self, id_gare, nom, ville, resultat_attendu):
        assert str(Gare()) == resultat_attendu

    def test_gare_importee_depuis_l_api_sans_id(self):
        """Cas de GareService.importer : l'id SNCF est du texte et la gare n'a pas encore d'id."""
        gare = Gare("Rennes", "Rennes", "stop_area:SNCF:87471003", None)
        assert gare.id_sncf == "stop_area:SNCF:87471003"
        assert gare.id_gare is None

    def test_gare_lue_en_base(self):
        gare = Gare(id_gare=1, nom="Rennes", ville="Rennes", id_sncf="stop_area:SNCF:87471003")
        assert gare.id_gare == 1

    def test_gare_sans_id_sncf(self):
        assert Gare("Rennes", "Rennes").id_sncf is None
