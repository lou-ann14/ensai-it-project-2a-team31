# TODO: test créer ok, créer données
# tests modifier capacité ok, modifier capacité pas de nombre de places
# tests trouver par num ok, trouver par num sans num valide

from unittest.mock import MagicMock, patch

import pytest
from src.Classes.classes_DAO.train_DAO import TrainDAO
from src.Classes.classes_objets.train import Train


@pytest.fixture
def curseur():
    """Remplace la connexion à la base par un faux curseur"""
    curseur = MagicMock()
    with patch("src.Classes.classes_DAO.train_DAO.DBConnexion") as mock_db:
        connexion = mock_db.return_value.connexion.__enter__.return_value
        connexion.cursor.return_value.__enter__.return_value = curseur
        yield curseur


@pytest.fixture
def train():
    """Train à enregistrer (MagicMock pour ne pas dépendre du constructeur de Train)"""
    return MagicMock(id_sncf=None, type_train="jaimelestrains", places_initiales="[200, 400]")


class TestsTrainDAO:

    # Tests créer

    def test_creer_train_ok(self, curseur, train) -> bool:
        """Vérifie que le train est bien créé"""
