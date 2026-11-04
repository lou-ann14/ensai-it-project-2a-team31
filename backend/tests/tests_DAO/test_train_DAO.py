from unittest.mock import MagicMock, patch

import pytest
from src.Classes.classes_DAO.train_DAO import TrainDAO
from src.Classes.classes_objets.train import Train

# La base de données est simulée : DBConnexion est remplacé par un MagicMock.

train_bdd = {"id_train": 1, "type_train": "TGV", "places_premieres": 200, "places_secondes": 400, "num_train": 8541}


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
    """Train à enregistrer"""
    return Train("TGV", 200, 400, 8541)


class TestsTrainDAO:

    # Tests créer

    def test_creer_train_ok(self, curseur, train):
        """Le train est créé et récupère l'id généré par la base"""
        curseur.fetchone.return_value = {"id_train": 1}

        resultat = TrainDAO().creer(train)

        assert resultat is train
        assert resultat.id_train == 1

    def test_creer_parametres(self, curseur, train):
        """Les places sont réparties dans les deux colonnes de la table"""
        curseur.fetchone.return_value = {"id_train": 1}

        TrainDAO().creer(train)

        requete, parametres = curseur.execute.call_args.args
        assert "INSERT INTO trains" in requete
        assert parametres == {"type_train": "TGV", "places_premieres": 200, "places_secondes": 400, "num_train": 8541}

    # Tests modifier_capacite

    def test_modifier_capacite_ok(self, curseur):
        """Une ligne est modifiée : True"""
        curseur.rowcount = 1

        resultat = TrainDAO().modifier_capacite(8541, 100, 300)

        assert resultat is True
        requete, parametres = curseur.execute.call_args.args
        assert "UPDATE trains" in requete
        assert " SET " in requete
        assert "WHERE num_train = %(num_train)s" in requete
        assert parametres == {"places_premieres": 100, "places_secondes": 300, "num_train": 8541}

    def test_modifier_capacite_train_inexistant(self, curseur):
        """Aucune ligne modifiée (numéro inconnu) : False"""
        curseur.rowcount = 0

        assert TrainDAO().modifier_capacite(9999, 100, 300) is False

    # Tests trouver_train_par_num

    def test_trouver_train_par_num_ok(self, curseur):
        """Le train existe : un objet Train complet est renvoyé"""
        curseur.fetchone.return_value = train_bdd

        resultat = TrainDAO().trouver_train_par_num(8541)

        requete, parametres = curseur.execute.call_args.args

        assert "SELECT *" in requete
        assert "FROM trains" in requete
        assert "WHERE num_train = %(num_train)s" in requete
        assert parametres == {"num_train": 8541}
        assert isinstance(resultat, Train)
        assert resultat.id_train == 1
        assert resultat.type_train == "TGV"
        assert resultat.places_premieres == 200
        assert resultat.places_secondes == 400
        assert resultat.num_train == 8541
        assert curseur.execute.call_args.args[1] == {"num_train": 8541}

    def test_trouver_train_par_num_inexistant(self, curseur):
        """Le train n'existe pas : None"""
        curseur.fetchone.return_value = None

        assert TrainDAO().trouver_train_par_num(9999) is None

    # Tests trouver_id_par_num

    def test_trouver_id_par_num_ok(self, curseur):
        """Le train existe : son id est renvoyé sous forme d'entier"""
        curseur.fetchone.return_value = {"id_train": 1}

        requete, parametres = curseur.execute.call_args.args

        assert "SELECT id_train" in requete
        assert "FROM trains" in requete
        assert "WHERE num_train = %(num_train)s" in requete
        assert parametres == {"num_train": 8541}
        assert TrainDAO().trouver_id_par_num(8541) == 1

    def test_trouver_id_par_num_inexistant(self, curseur):
        """Le train n'existe pas : None"""
        curseur.fetchone.return_value = None

        assert TrainDAO().trouver_id_par_num(9999) is None
