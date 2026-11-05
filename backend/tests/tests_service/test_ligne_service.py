from unittest.mock import patch

import pytest
from psycopg2.errors import ForeignKeyViolation
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_service.ligne_service import LigneService

# données préenregistrées
gare_matabiau = Gare("Matabiau", "Toulouse", "stop_area:SNCF:87611004", 1)
gare_montparnasse = Gare("Montparnasse", "Paris", "stop_area:SNCF:87391003", 3)
gare_rennes = Gare("Gare de Rennes", "Rennes", "stop_area:SNCF:87471003", 7)

ligne_toulouse_paris = Ligne(gare_matabiau, gare_montparnasse, id_ligne=1)
ligne_paris_rennes = Ligne(gare_montparnasse, gare_rennes, id_ligne=2)


@pytest.fixture
def dao():
    """Remplace LigneDAO par un faux DAO : aucune vraie base n'est utilisée"""
    with patch("src.Classes.classes_service.ligne_service.LigneDAO") as ligne_dao:
        ligne_dao.return_value.rechercher.return_value = None  # par défaut : aucune ligne existante
        ligne_dao.return_value.a_des_trajets.return_value = False
        yield ligne_dao.return_value


# Tests creer


def test_creer_ok(dao):
    """Ligne inexistante : le service la crée et renvoie ce que renvoie le DAO"""
    # GIVEN
    dao.creer.return_value = ligne_toulouse_paris

    # WHEN
    res = LigneService().creer(gare_matabiau, gare_montparnasse, 5)

    # THEN
    dao.creer.assert_called_once_with(gare_matabiau, gare_montparnasse, 5)
    assert res is ligne_toulouse_paris


@pytest.mark.parametrize(
    "gare_depart, gare_arrivee",
    [
        (None, gare_montparnasse),
        (gare_matabiau, None),
        (None, None),
    ]
)
def test_creer_gare_manquante(dao, gare_depart, gare_arrivee):
    """Une gare manque : ValueError et rien n'est créé"""
    with pytest.raises(ValueError, match="obligatoires"):
        LigneService().creer(gare_depart, gare_arrivee)
    dao.creer.assert_not_called()


def test_creer_gares_identiques(dao):
    """Départ = arrivée : ValueError"""
    with pytest.raises(ValueError, match="différentes"):
        LigneService().creer(gare_matabiau, gare_matabiau)
    dao.creer.assert_not_called()


def test_creer_ligne_deja_existante(dao):
    """Une ligne relie déjà ces gares : ValueError"""
    # GIVEN
    dao.rechercher.return_value = ligne_toulouse_paris

    # WHEN / THEN
    with pytest.raises(ValueError, match="existe déjà"):
        LigneService().creer(gare_matabiau, gare_montparnasse)
    dao.creer.assert_not_called()


def test_creer_collaborateur_inexistant(dao):
    """La BDD refuse le collaborateur (clé étrangère) : ValueError"""
    # GIVEN
    dao.creer.side_effect = ForeignKeyViolation

    # WHEN / THEN
    with pytest.raises(ValueError, match="collaborateur #99"):
        LigneService().creer(gare_matabiau, gare_montparnasse, 99)


# Tests rechercher


def test_rechercher_ok(dao):
    """Le service renvoie la ligne trouvée par le DAO"""
    # GIVEN
    dao.rechercher.return_value = ligne_toulouse_paris

    # WHEN
    res = LigneService().rechercher(gare_matabiau, gare_montparnasse)

    # THEN
    dao.rechercher.assert_called_once_with(gare_depart=gare_matabiau, gare_arrivee=gare_montparnasse)
    assert res is ligne_toulouse_paris


def test_rechercher_gare_manquante(dao):
    """Une gare manque : None, sans interroger le DAO"""
    assert LigneService().rechercher(None, gare_montparnasse) is None
    dao.rechercher.assert_not_called()


# Tests trouver_par_id


def test_trouver_par_id_ok(dao):
    """L'id 1 existe : le service renvoie la ligne"""
    dao.trouver_par_id.return_value = ligne_toulouse_paris

    assert LigneService().trouver_par_id(1) is ligne_toulouse_paris
    dao.trouver_par_id.assert_called_once_with(1)


def test_trouver_par_id_introuvable(dao):
    """L'id 99 n'existe pas : None"""
    dao.trouver_par_id.return_value = None

    assert LigneService().trouver_par_id(99) is None


# Tests modifier


def test_modifier_ok(dao):
    """Nouvelles gares libres et ligne sans trajet : modification acceptée"""
    # GIVEN
    dao.modifier.return_value = True
    ligne = Ligne(gare_matabiau, gare_rennes, id_ligne=1)

    # WHEN
    res = LigneService().modifier(ligne)

    # THEN
    dao.modifier.assert_called_once_with(ligne)
    assert res is True


def test_modifier_memes_gares_meme_ligne(dao):
    """Retrouver sa propre ligne n'est pas un doublon"""
    # GIVEN
    dao.modifier.return_value = True
    dao.rechercher.return_value = ligne_toulouse_paris

    # WHEN / THEN
    assert LigneService().modifier(Ligne(gare_matabiau, gare_montparnasse, id_ligne=1)) is True


def test_modifier_inexistante(dao):
    """La ligne 99 n'existe pas : le DAO renvoie False"""
    dao.modifier.return_value = False

    assert LigneService().modifier(Ligne(gare_matabiau, gare_rennes, id_ligne=99)) is False


def test_modifier_gares_identiques(dao):
    """Départ = arrivée : ValueError"""
    with pytest.raises(ValueError, match="différentes"):
        LigneService().modifier(Ligne(gare_matabiau, gare_matabiau, id_ligne=1))
    dao.modifier.assert_not_called()


def test_modifier_doublon(dao):
    """Une autre ligne relie déjà ces gares : ValueError"""
    # GIVEN
    dao.rechercher.return_value = ligne_paris_rennes  # id_ligne 2, différent de 1

    # WHEN / THEN
    with pytest.raises(ValueError, match="existe déjà"):
        LigneService().modifier(Ligne(gare_montparnasse, gare_rennes, id_ligne=1))
    dao.modifier.assert_not_called()


def test_modifier_ligne_avec_trajets(dao):
    """La ligne a des trajets : ValueError"""
    # GIVEN
    dao.a_des_trajets.return_value = True

    # WHEN / THEN
    with pytest.raises(ValueError, match="a des trajets"):
        LigneService().modifier(Ligne(gare_matabiau, gare_rennes, id_ligne=1))
    dao.modifier.assert_not_called()


# Tests supprimer


def test_supprimer_ok(dao):
    """La ligne 1 existe : True"""
    dao.supprimer.return_value = True

    assert LigneService().supprimer(1) is True
    dao.supprimer.assert_called_once_with(1)


def test_supprimer_inexistante(dao):
    """La ligne 99 n'existe pas : False"""
    dao.supprimer.return_value = False

    assert LigneService().supprimer(99) is False


def test_supprimer_ligne_avec_trajets(dao):
    """La BDD refuse (clé étrangère) : ValueError"""
    dao.supprimer.side_effect = ForeignKeyViolation

    with pytest.raises(ValueError, match="a des trajets"):
        LigneService().supprimer(1)
