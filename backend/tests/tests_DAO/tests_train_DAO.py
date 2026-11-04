# TODO: test créer données
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
    return MagicMock(id=None, type_train="TGV", places_initiales="[200, 400]")


class TestsTrainDAO:

    # Tests créer

    def test_creer_train_ok(self, curseur, train) -> bool:
        """Vérifie que le train est bien créé"""
        # GIVEN
        curseur.fetchone.return_value = {"id": 1}

        # WHEN
        resultat = TrainDAO().creer(train)

        # THEN
        assert resultat is train
        assert resultat.id == 1

    def test_creer_parametres(self, curseur, utilisateur):
        """Les informations du train sont bien transmises à la requête"""
        # GIVEN
        curseur.fetchone.return_value = {"id": 1}

        # WHEN
        TrainDAO().creer(train)

        # THEN
        requete, parametres = curseur.execute.call_args.args
        assert "INSERT INTO train" in requete
        assert parametres == {"type_train": "TGV", "places_initiales": "[200, 400]"}

    # tests modifier

    def test_modifier_capacite_ok(self, curseur, train):
        """Une ligne est modifiée : True"""
        # GIVEN
        train.id = 1
        curseur.rowcount = 1

        # WHEN
        resultat = TrainDAO().modifier(train)

        # THEN
        assert resultat is True
        requete, parametres = curseur.execute.call_args.args
        assert "UPDATE train" in requete
        assert parametres["id"] == 1

    def test_modifier_train_inexistant(self, curseur, utilisateur):
        """Aucune ligne modifiée (id inconnu) : False"""
        # GIVEN
        train.id = 999
        curseur.rowcount = 0

        # WHEN
        resultat = TrainDAO().modifier(train)

        # THEN
        assert resultat is False

    # tests trouver_par_id

    def test_trouver_par_id_ok(self, curseur):
        """L'utilisateur existe : un objet Utilisateur est renvoyé"""
        # GIVEN
        curseur.fetchone.return_value = train_bdd

        # WHEN
        resultat = TrainDAO().trouver_par_id(1)

        # THEN
        assert isinstance(resultat, Train)
        assert resultat.id == 1
        assert resultat.nom_utilisateur == "jaimelestrains"
        assert resultat.grade == "CLIENT"
        assert curseur.execute.call_args.args[1] == {"id": 1}

    def test_trouver_par_id_inexistant(self, curseur):
        """L'utilisateur n'existe pas : None"""
        # GIVEN
        curseur.fetchone.return_value = None

        # WHEN
        resultat = UtilisateurDAO().trouver_par_id(999)

        # THEN
        assert resultat is None