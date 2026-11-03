from unittest.mock import MagicMock, patch

import pytest
from src.Classes.classes_DAO.utilisateur_DAO import UtilisateurDAO
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur

# La base de données est simulée : DBConnexion est remplacé par un MagicMock,
# on contrôle donc ce que renvoie le curseur et on vérifie les paramètres reçus.

utilisateur_bdd = {"id": 1, "nom_utilisateur": "jaimelestrains", "mdp": "1234", "role": "CLIENT"}


@pytest.fixture
def curseur():
    """Remplace la connexion à la base par un faux curseur"""
    curseur = MagicMock()
    with patch("src.Classes.classes_DAO.utilisateur_DAO.DBConnexion") as mock_db:
        connexion = mock_db.return_value.connexion.__enter__.return_value
        connexion.cursor.return_value.__enter__.return_value = curseur
        yield curseur


@pytest.fixture
def utilisateur():
    """Utilisateur à enregistrer (MagicMock pour ne pas dépendre du constructeur d'Utilisateur)"""
    return MagicMock(id=None, nom_utilisateur="jaimelestrains", mdp="1234", role="CLIENT")


class TestUtilisateurDAO:

    # tests creer

    def test_creer_ok(self, curseur, utilisateur):
        """L'utilisateur est créé et récupère l'id généré par la base"""
        # GIVEN
        curseur.fetchone.return_value = {"id": 1}

        # WHEN
        resultat = UtilisateurDAO().creer(utilisateur)

        # THEN
        assert resultat is utilisateur
        assert resultat.id == 1

    def test_creer_parametres(self, curseur, utilisateur):
        """Les informations de l'utilisateur sont bien transmises à la requête"""
        # GIVEN
        curseur.fetchone.return_value = {"id": 1}

        # WHEN
        UtilisateurDAO().creer(utilisateur)

        # THEN
        requete, parametres = curseur.execute.call_args.args
        assert "INSERT INTO utilisateurs" in requete
        assert parametres == {"nom_utilisateur": "jaimelestrains", "mdp": "1234", "role": "CLIENT"}

    # tests modifier

    def test_modifier_ok(self, curseur, utilisateur):
        """Une ligne est modifiée : True"""
        # GIVEN
        utilisateur.id = 1
        curseur.rowcount = 1

        # WHEN
        resultat = UtilisateurDAO().modifier(utilisateur)

        # THEN
        assert resultat is True
        requete, parametres = curseur.execute.call_args.args
        assert "UPDATE utilisateurs" in requete
        assert parametres["id"] == 1

    def test_modifier_utilisateur_inexistant(self, curseur, utilisateur):
        """Aucune ligne modifiée (id inconnu) : False"""
        # GIVEN
        utilisateur.id = 999
        curseur.rowcount = 0

        # WHEN
        resultat = UtilisateurDAO().modifier(utilisateur)

        # THEN
        assert resultat is False

    # tests trouver_par_id

    def test_trouver_par_id_ok(self, curseur):
        """L'utilisateur existe : un objet Utilisateur est renvoyé"""
        # GIVEN
        curseur.fetchone.return_value = utilisateur_bdd

        # WHEN
        resultat = UtilisateurDAO().trouver_par_id(1)

        # THEN
        assert isinstance(resultat, Utilisateur)
        assert resultat.id == 1
        assert resultat.nom_utilisateur == "jaimelestrains"
        assert resultat.role == "CLIENT"
        assert curseur.execute.call_args.args[1] == {"id": 1}

    def test_trouver_par_id_inexistant(self, curseur):
        """L'utilisateur n'existe pas : None"""
        # GIVEN
        curseur.fetchone.return_value = None

        # WHEN
        resultat = UtilisateurDAO().trouver_par_id(999)

        # THEN
        assert resultat is None

    # tests trouver_par_nom_utilisateur

    def test_trouver_par_nom_utilisateur_ok(self, curseur):
        """L'utilisateur existe : un objet Utilisateur est renvoyé"""
        # GIVEN
        curseur.fetchone.return_value = utilisateur_bdd

        # WHEN
        resultat = UtilisateurDAO().trouver_par_nom_utilisateur("jaimelestrains")

        # THEN
        assert isinstance(resultat, Utilisateur)
        assert resultat.id == 1
        assert resultat.nom_utilisateur == "jaimelestrains"
        assert curseur.execute.call_args.args[1] == {"nom_utilisateur": "jaimelestrains"}

    def test_trouver_par_nom_utilisateur_inexistant(self, curseur):
        """L'utilisateur n'existe pas : None"""
        # GIVEN
        curseur.fetchone.return_value = None

        # WHEN
        resultat = UtilisateurDAO().trouver_par_nom_utilisateur("inconnu")

        # THEN
        assert resultat is None
