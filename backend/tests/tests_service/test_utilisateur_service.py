from unittest.mock import patch

import pytest
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.Classes.classes_service.utilisateurs_service.utilisateur_service import UtilisateurService
from src.utils.securite import hash_password

# La base est simulée : aucun appel réel n'est fait.

DAO = "src.Classes.classes_service.utilisateurs_service.utilisateur_service.UtilisateurDAO"


@pytest.fixture
def dao():
    with patch(DAO) as utilisateur_dao:
        utilisateur_dao.return_value.trouver_par_id.return_value = Utilisateur(
            hash_password("ancien", "alice"), "alice", "CLIENT", id=1
        )
        utilisateur_dao.return_value.modifier_mdp.return_value = True
        yield utilisateur_dao.return_value


def test_changer_mdp_ok(dao):
    assert UtilisateurService().changer_mdp(1, "ancien", "nouveau") is True
    dao.modifier_mdp.assert_called_once_with(1, hash_password("nouveau", "alice"))


def test_changer_mdp_ancien_incorrect(dao):
    assert UtilisateurService().changer_mdp(1, "faux", "nouveau") is False
    dao.modifier_mdp.assert_not_called()


def test_changer_mdp_utilisateur_inconnu(dao):
    dao.trouver_par_id.return_value = None

    assert UtilisateurService().changer_mdp(99, "ancien", "nouveau") is False
    dao.modifier_mdp.assert_not_called()


def test_changer_mdp_ne_passe_pas_par_modifier(dao):
    """modifier remettrait le token à vide : trouver_par_id ne le lit pas."""
    UtilisateurService().changer_mdp(1, "ancien", "nouveau")
    dao.modifier.assert_not_called()


# Tests creer_compte


def test_creer_compte_ok(dao):
    dao.creer.return_value = True

    utilisateur = UtilisateurService().creer_compte("alice", "secret")

    assert utilisateur.grade == "CLIENT"
    assert utilisateur.mdp == hash_password("secret", "alice")  # jamais stocké en clair


def test_creer_compte_nom_deja_pris_en_base(dao):
    """Deux inscriptions simultanées : la contrainte UNIQUE de la base refuse la seconde"""
    from psycopg2.errors import UniqueViolation

    dao.creer.side_effect = UniqueViolation

    with pytest.raises(ValueError, match="déjà pris"):
        UtilisateurService().creer_compte("alice", "secret")


@pytest.mark.parametrize("nouveau", ["", "   ", None])
def test_changer_mdp_nouveau_vide(dao, nouveau):
    """Un nouveau mot de passe vide est refusé, sans toucher à la base"""
    with pytest.raises(ValueError, match="obligatoire"):
        UtilisateurService().changer_mdp(1, "ancien", nouveau)
    dao.modifier_mdp.assert_not_called()
