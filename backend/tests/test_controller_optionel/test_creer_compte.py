from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from src.Classes.controller.utilisateur_controller import creer_compte
from src.schema.utilisateur_schema import CompteCreationModel
from src.utils.securite import hash_password

# La base est simulée : aucun appel réel n'est fait.

UTILISATEUR_DAO = "src.Classes.controller.utilisateur_controller.UtilisateurDAO"
ADMIN_SQL = Path(__file__).resolve().parents[2] / "data" / "admin.sql"


@pytest.fixture
def dao():
    with patch(UTILISATEUR_DAO) as utilisateur_dao:
        utilisateur_dao.return_value.trouver_par_nom_utilisateur.return_value = None
        yield utilisateur_dao.return_value


def test_creer_compte_passe_par_le_service(dao):
    """Le mot de passe est confié au service, qui le hache : la route n'écrit pas elle-même en base"""
    service = MagicMock()

    resultat = creer_compte(CompteCreationModel(nom_utilisateur="  alice ", mdp="secret"), service)

    assert resultat is service.creer_compte.return_value
    service.creer_compte.assert_called_once_with("alice", "secret")
    dao.creer.assert_not_called()


def test_creer_compte_nom_deja_pris(dao):
    dao.trouver_par_nom_utilisateur.return_value = MagicMock()
    service = MagicMock()

    with pytest.raises(HTTPException) as erreur:
        creer_compte(CompteCreationModel(nom_utilisateur="alice", mdp="secret"), service)

    assert erreur.value.status_code == 400
    service.creer_compte.assert_not_called()


@pytest.mark.parametrize("nom, mdp", [("   ", "secret"), ("alice", "")])
def test_creer_compte_donnee_vide(dao, nom, mdp):
    service = MagicMock()

    with pytest.raises(HTTPException) as erreur:
        creer_compte(CompteCreationModel(nom_utilisateur=nom, mdp=mdp), service)

    assert erreur.value.status_code == 400
    service.creer_compte.assert_not_called()


def test_creer_compte_nom_trop_long(dao):
    """Le service refuse le nom (ValueError) : la route répond 400 et non 500"""
    service = MagicMock()
    service.creer_compte.side_effect = ValueError("Le nom doit faire 15 caractères maximum")

    with pytest.raises(HTTPException) as erreur:
        creer_compte(CompteCreationModel(nom_utilisateur="a" * 16, mdp="secret"), service)

    assert erreur.value.status_code == 400


@pytest.mark.parametrize(
    "nom, mdp, grade",
    [("admin", "123", "ADMIN"), ("collaborateur", "456", "COLLABORATEUR"), ("client", "789", "CLIENT")],
)
def test_admin_sql_contient_les_mots_de_passe_haches(nom, mdp, grade):
    assert f"('{nom}', '{hash_password(mdp, nom)}', '{grade}')" in ADMIN_SQL.read_text(encoding="utf-8")


def test_login_message_en_francais():
    """Mauvais identifiants : 401 avec un message en français (comme le reste de l'API)"""
    from src.Classes.controller.login_controller import login
    from src.schema.utilisateur_schema import CompteCreationModel

    service = MagicMock()
    service.login.return_value = None

    with pytest.raises(HTTPException) as erreur:
        login(CompteCreationModel(nom_utilisateur="alice", mdp="faux"), service)

    assert erreur.value.status_code == 401
    assert erreur.value.detail == "Nom d'utilisateur ou mot de passe incorrect."
