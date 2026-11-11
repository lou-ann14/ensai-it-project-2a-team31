from unittest.mock import MagicMock, patch

import pytest
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_service.gare_service import GareService

gares = [Gare("Paris Nord", "Paris", id_gare=1), Gare("Paris Est", "Paris", id_gare=2)]


@pytest.mark.parametrize(
    "nom, ville, nom_attendu, ville_attendue",
    [
        ("Paris", "Lyon", "Paris", "Lyon"),
        (" Paris ", " Lyon ", "Paris", "Lyon"),
        (None, "Lyon", None, "Lyon"),
        ("Paris", None, "Paris", None),
        ("", "", None, None),
        ("   ", "   ", None, None),
        (None, None, None, None),
    ]
)
def test_rechercher_ok(nom, ville, nom_attendu, ville_attendue):

    # GIVEN
    service = GareService()
    service.gare_dao.rechercher = MagicMock(return_value=gares)

    # WHEN
    res = service.rechercher(nom, ville)
    # THEN
    # vérifie que le dao est appelé une fois et avec les bons arguments
    service.gare_dao.rechercher.assert_called_once_with(
        nom=nom_attendu,
        ville=ville_attendue
    )
    # vérifie que GareService().rechercher renvoie ce que le dao renvoie
    assert res == gares


# Tests importer

gares_api = [
    {"nom": "Rennes", "ville": "Rennes", "id_sncf": "stop_area:SNCF:87471003"},
    {"nom": "Rennes Beaulieu Chimie", "ville": "Rennes", "id_sncf": "stop_area:SNCF:87478107"},
]


@patch("src.Classes.classes_service.gare_service.SncfClient")
def test_importer_ok(mock_sncf):
    """L'API trouve 2 gares : elles sont enregistrées et renvoyées"""
    # GIVEN
    mock_sncf().rechercher_gares.return_value = gares_api
    service = GareService()
    service.gare_dao.creer_ou_mettre_a_jour = MagicMock(side_effect=lambda gare: gare)

    # WHEN
    res = service.importer("  Rennes ")

    # THEN
    mock_sncf().rechercher_gares.assert_called_with("Rennes")  # texte nettoyé des espaces
    assert service.gare_dao.creer_ou_mettre_a_jour.call_count == 2
    assert [gare.nom for gare in res] == ["Rennes", "Rennes Beaulieu Chimie"]
    assert res[0].id_sncf == "stop_area:SNCF:87471003"


@patch("src.Classes.classes_service.gare_service.SncfClient")
def test_importer_aucune_gare(mock_sncf):
    """L'API ne trouve rien : liste vide, rien n'est enregistré"""
    mock_sncf().rechercher_gares.return_value = []
    service = GareService()
    service.gare_dao.creer_ou_mettre_a_jour = MagicMock()

    assert service.importer("Zzz") == []
    service.gare_dao.creer_ou_mettre_a_jour.assert_not_called()


@pytest.mark.parametrize("texte", [None, "", "R", "  R  "])
@patch("src.Classes.classes_service.gare_service.SncfClient")
def test_importer_texte_trop_court(mock_sncf, texte):
    """Moins de 2 caractères : ValueError, sans appeler l'API"""
    with pytest.raises(ValueError, match="2 caractères"):
        GareService().importer(texte)
    mock_sncf().rechercher_gares.assert_not_called()
