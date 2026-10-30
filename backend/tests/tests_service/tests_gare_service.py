from unittest.mock import MagicMock

import pytest
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_service.gare_service import GareService

gares = [Gare(1, "Paris Nord", "Paris"), Gare(2, "Paris Est", "Paris")]


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
