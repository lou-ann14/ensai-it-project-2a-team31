from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests
from psycopg2.errors import ForeignKeyViolation
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train
from src.Classes.classes_objets.trajet import Trajet
from src.Classes.classes_service.trajet_service import TrajetService, train_depuis_id

# Données communes aux tests

ligne_test = Ligne(
    gare_depart=Gare("Rennes", "Rennes", "stop_area:SNCF:87471003", id_gare=1),
    gare_arrivee=Gare("Nantes", "Nantes", "stop_area:SNCF:87481002", id_gare=2),
    id_ligne=1,
)

train_test = Train(
    type_train="TGV",
    places_premieres=100,
    places_secondes=200,
    num_train=8541,
    id_train=1,
)

heure_depart = datetime(2026, 1, 15, 10, 0)
heure_arrivee = datetime(2026, 1, 15, 11, 0)
tarif_base = 30.0

trajet_test = Trajet(
    id_trajet=10,
    ligne=ligne_test,
    train=train_test,
    heure_depart=heure_depart,
    heure_arrivee=heure_arrivee,
    tarif_base=tarif_base,
)

# tests _verifier_donnees


def test_verifier_donnees_ok():
    """Données valides : ne lève rien"""
    # WHEN
    res = TrajetService()._verifier_donnees(
        ligne_test.id_ligne,
        train_test.id_train,
        heure_depart,
        tarif_base
        )

    # THEN
    assert res is None


def test_verifier_donnees_ligne_manquante():
    """id_ligne est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(
            None,
            train_test.id_train,
            heure_depart,
            tarif_base
            )


def test_verifier_donnees_train_manquant():
    """id_train est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(
            ligne_test.id_ligne,
            None,
            heure_depart,
            tarif_base
            )


def test_verifier_donnees_heures_pas_datetime():
    """L'heure de départ n'est pas un datetime : TypeError"""
    with pytest.raises(TypeError):
        TrajetService()._verifier_donnees(
            ligne_test.id_ligne,
            train_test.id_train,
            "10h",
            tarif_base
            )


def test_verifier_donnees_tarif_negatif():
    """Le tarif est négatif : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(
            ligne_test.id_ligne,
            train_test.id_train,
            heure_depart,
            -5.0
            )


def test_verifier_donnees_tarif_manquant():
    """Le tarif est None : ValueError"""
    with pytest.raises(ValueError):
        TrajetService()._verifier_donnees(
            ligne_test.id_ligne,
            train_test.id_train,
            heure_depart,
            None
            )

# tests _verifier_ligne


@patch("src.Classes.classes_service.trajet_service.LigneDAO")
def test_verifier_ligne_ok(mock_ligne_dao):
    """La ligne 1 existe : elle est renvoyée"""
    # GIVEN
    mock_ligne_dao().trouver_par_id.return_value = ligne_test

    # WHEN
    res = TrajetService()._verifier_ligne(1)

    # THEN
    assert res is ligne_test
    mock_ligne_dao().trouver_par_id.assert_called_with(1)


@patch("src.Classes.classes_service.trajet_service.LigneDAO")
def test_verifier_ligne_inexistante(mock_ligne_dao):
    """La ligne 99 n'existe pas : ValueError"""
    mock_ligne_dao().trouver_par_id.return_value = None

    with pytest.raises(ValueError, match="ligne #99"):
        TrajetService()._verifier_ligne(99)


# tests _trajet_similaire_existe


def test_trajet_similaire_existe_meme_heure():
    """Un trajet part déjà à la même heure sur cette ligne : True"""
    # GIVEN
    service = TrajetService()
    service.trajet_dao.rechercher = MagicMock(return_value=[trajet_test])

    # WHEN / THEN
    assert service._trajet_similaire_existe(ligne_test, heure_depart) is True


def test_trajet_similaire_existe_autre_heure():
    """Le seul trajet du jour part à une autre heure : False"""
    service = TrajetService()
    service.trajet_dao.rechercher = MagicMock(return_value=[trajet_test])

    assert service._trajet_similaire_existe(ligne_test, datetime(2026, 1, 15, 18, 0)) is False


def test_trajet_similaire_existe_aucun_trajet():
    """Aucun trajet ce jour-là : False"""
    service = TrajetService()
    service.trajet_dao.rechercher = MagicMock(return_value=[])

    assert service._trajet_similaire_existe(ligne_test, heure_depart) is False


def test_trajet_similaire_existe_ignore_le_trajet_modifie():
    """En modification, le trajet lui-même (id 10) n'est pas un doublon : False"""
    service = TrajetService()
    service.trajet_dao.rechercher = MagicMock(return_value=[trajet_test])

    assert service._trajet_similaire_existe(ligne_test, heure_depart, id_trajet_ignore=10) is False

# tests creer


@patch("src.Classes.classes_service.trajet_service.SncfClient")
def test_creer_ok(sncf):
    """Crée un trajet avec succès"""
    # GIVEN
    sncf.return_value.duree_trajet.return_value = 3600
    service = TrajetService()
    service._verifier_donnees = MagicMock()
    service._verifier_ligne = MagicMock(return_value=ligne_test)
    service._trajet_similaire_existe = MagicMock(return_value=False)
    service.trajet_dao.creer = MagicMock(return_value=trajet_test)

    # WHEN
    trajet = service.creer(
        ligne_test.id_ligne,
        train_test.id_train,
        heure_depart,
        tarif_base
        )

    # THEN
    assert trajet is trajet_test
    trajet_envoye = service.trajet_dao.creer.call_args.args[0]
    assert trajet_envoye.ligne is ligne_test
    assert trajet_envoye.train.id_train == train_test.id_train
    assert trajet_envoye.heure_arrivee == heure_arrivee


@patch("src.Classes.classes_service.trajet_service.SncfClient")
def test_creer_fail(sncf):
    """Ne parvient pas à créer de trajet car TrajetDAO().creer retourne None"""
    # GIVEN
    sncf.return_value.duree_trajet.return_value = 3600
    service = TrajetService()
    service._verifier_donnees = MagicMock()
    service._verifier_ligne = MagicMock(return_value=ligne_test)
    service._trajet_similaire_existe = MagicMock(return_value=False)
    service.trajet_dao.creer = MagicMock(return_value=None)

    # WHEN
    trajet = service.creer(
        ligne_test.id_ligne,
        train_test.id_train,
        heure_depart,
        tarif_base
        )

    # THEN
    assert trajet is None


def test_creer_donnees_invalides():
    """Les données sont invalides : l'erreur est propagée"""
    # GIVEN
    service = TrajetService()
    service._verifier_donnees = MagicMock(side_effect=ValueError)

    # WHEN / THEN
    with pytest.raises(ValueError):
        service.creer(
            ligne_test.id_ligne,
            train_test.id_train,
            heure_depart,
            tarif_base
            )

# tests creer : ligne inexistante et train inexistant
# (le cas « trajet déjà existant » est testé plus bas : test_creer_doublon_sans_appeler_api)


def test_creer_ligne_inexistante():
    """La ligne n'existe pas : ValueError et rien n'est créé"""
    # GIVEN
    service = TrajetService()
    service._verifier_ligne = MagicMock(side_effect=ValueError("La ligne #99 n'existe pas"))
    service.trajet_dao.creer = MagicMock()

    # WHEN / THEN
    with pytest.raises(ValueError, match="ligne #99"):
        service.creer(99, train_test.id_train, heure_depart, tarif_base)
    service.trajet_dao.creer.assert_not_called()


def test_creer_train_inexistant():
    """La BDD refuse le train (clé étrangère) : ValueError"""
    # GIVEN
    service = TrajetService()
    service._verifier_ligne = MagicMock(return_value=ligne_test)
    service._trajet_similaire_existe = MagicMock(return_value=False)
    service._calculer_duree = MagicMock(return_value=3600)
    service.trajet_dao.creer = MagicMock(side_effect=ForeignKeyViolation)

    # WHEN / THEN
    with pytest.raises(ValueError, match="train #99"):
        service.creer(ligne_test.id_ligne, 99, heure_depart, tarif_base)


# tests du calcul du temps de trajet avec l'API SNCF (anciennement test_trajet_temps.py)
# L'API SNCF et la base sont simulées : aucun appel réel n'est fait.

DEPART = datetime(2027, 6, 1, 8, 0)
ID_RENNES = "stop_area:SNCF:87471003"
ID_NANTES = "stop_area:SNCF:87481002"


def faire_ligne(id_sncf_depart=ID_RENNES, id_sncf_arrivee=ID_NANTES):
    return Ligne(
        Gare("Rennes", "Rennes", id_sncf_depart, id_gare=1),
        Gare("Nantes", "Nantes", id_sncf_arrivee, id_gare=2),
        id_ligne=1,
    )


@pytest.fixture
def mocks():
    """Remplace la base et l'API SNCF, pour une ligne valide et sans trajet existant"""
    with (
        patch("src.Classes.classes_service.trajet_service.TrajetDAO") as trajet_dao,
        patch("src.Classes.classes_service.trajet_service.LigneDAO") as ligne_dao,
        patch("src.Classes.classes_service.trajet_service.SncfClient") as sncf,
    ):
        ligne_dao.return_value.trouver_par_id.return_value = faire_ligne()
        trajet_dao.return_value.rechercher.return_value = []
        trajet_dao.return_value.creer.side_effect = lambda trajet: trajet
        yield MagicMock(dao=trajet_dao.return_value, ligne=ligne_dao.return_value, api=sncf.return_value)


def test_creer_calcule_arrivee_et_temps(mocks):
    """1 h 21 d'après l'API : l'arrivée et le temps de trajet sont renseignés"""
    mocks.api.duree_trajet.return_value = 4860

    trajet = TrajetService().creer(1, 1, DEPART, 40.0)

    assert trajet.heure_arrivee == datetime(2027, 6, 1, 9, 21)
    assert trajet.temps_trajet == 81
    mocks.api.duree_trajet.assert_called_once_with(ID_RENNES, ID_NANTES, DEPART)
    mocks.dao.creer.assert_called_once()


def test_creer_date_trop_lointaine_utilise_les_horaires_actuels(mocks):
    """L'API ne connaît pas la date demandée : on redemande la durée sans date"""
    mocks.api.duree_trajet.side_effect = [None, 4620]

    trajet = TrajetService().creer(1, 1, DEPART, 40.0)

    assert trajet.temps_trajet == 77
    assert mocks.api.duree_trajet.call_args_list[1].args == (ID_RENNES, ID_NANTES)


def test_creer_aucun_itineraire(mocks):
    """L'API ne trouve rien, même sans date : le trajet n'est pas créé"""
    mocks.api.duree_trajet.return_value = None

    with pytest.raises(ValueError, match="aucun itinéraire"):
        TrajetService().creer(1, 1, DEPART, 40.0)

    mocks.dao.creer.assert_not_called()


def test_creer_gare_sans_id_sncf(mocks):
    """Une gare qui ne vient pas de l'API : on ne peut pas calculer le temps de trajet"""
    mocks.ligne.trouver_par_id.return_value = faire_ligne(id_sncf_depart=None)

    with pytest.raises(ValueError, match="API SNCF"):
        TrajetService().creer(1, 1, DEPART, 40.0)

    mocks.api.duree_trajet.assert_not_called()
    mocks.dao.creer.assert_not_called()


def test_creer_api_indisponible(mocks):
    """Une panne de l'API remonte, et le trajet n'est pas créé"""
    mocks.api.duree_trajet.side_effect = requests.ConnectionError()

    with pytest.raises(requests.RequestException):
        TrajetService().creer(1, 1, DEPART, 40.0)

    mocks.dao.creer.assert_not_called()


def test_creer_donnee_invalide_sans_appeler_api(mocks):
    """Un tarif négatif est refusé sans consommer de requête API"""
    with pytest.raises(ValueError, match="tarif"):
        TrajetService().creer(1, 1, DEPART, -1)

    mocks.api.duree_trajet.assert_not_called()


def test_creer_doublon_sans_appeler_api(mocks):
    """Un trajet déjà existant à cette heure est refusé sans consommer de requête API"""
    mocks.dao.rechercher.return_value = [MagicMock(heure_depart=DEPART, id_trajet=5)]

    with pytest.raises(ValueError, match="existe déjà"):
        TrajetService().creer(1, 1, DEPART, 40.0)

    mocks.api.duree_trajet.assert_not_called()


def test_modifier_recalcule_arrivee_et_temps(mocks):
    """Modifier l'heure de départ met à jour l'arrivée et le temps de trajet"""
    mocks.dao.trouver_par_id.return_value = MagicMock()
    mocks.dao.modifier.return_value = True
    mocks.api.duree_trajet.return_value = 3600
    trajet = Trajet(DEPART, DEPART, faire_ligne(), Train("TGV", 100, 300, 8541, id_train=1), 40.0)

    assert TrajetService().modifier(1, trajet) is True

    assert trajet.heure_arrivee == datetime(2027, 6, 1, 9, 0)
    assert trajet.temps_trajet == 60
    assert trajet.id_trajet == 1


# tests train_depuis_id et creer (anciennement test_gare_et_train_trajet.py)

SERVICE_TRAJET = "src.Classes.classes_service.trajet_service"
DEPART_RENNES_NANTES = datetime(2026, 11, 18, 8, 35)
LIGNE_RENNES_NANTES = Ligne(
    Gare("Rennes", "Rennes", "stop_area:SNCF:87471003", 1),
    Gare("Nantes", "Nantes", "stop_area:SNCF:87481002", 5),
    id_ligne=1,
)


@pytest.fixture
def service_trajet():
    with patch(f"{SERVICE_TRAJET}.TrajetDAO") as trajet_dao, patch(f"{SERVICE_TRAJET}.LigneDAO") as ligne_dao, patch(
        f"{SERVICE_TRAJET}.SncfClient"
    ) as sncf:
        ligne_dao.return_value.trouver_par_id.return_value = LIGNE_RENNES_NANTES
        trajet_dao.return_value.rechercher.return_value = []
        trajet_dao.return_value.creer.side_effect = lambda trajet: trajet
        sncf.return_value.duree_trajet.return_value = 4620
        yield TrajetService()


def test_train_depuis_id():
    assert train_depuis_id(3).id_train == 3


@pytest.mark.parametrize("tarif", [40, 40.0])
def test_creer_trajet_garde_l_id_du_train(service_trajet, tarif):
    """Un tarif entier est accepté : Trajet exige un float."""
    trajet = service_trajet.creer(1, 3, DEPART_RENNES_NANTES, tarif)

    assert trajet.train.id_train == 3
    assert trajet.tarif_base == 40.0
    assert trajet.temps_trajet == 77


# tests modifier : cas d'erreur


def test_modifier_trajet_manquant():
    """Pas de trajet : ValueError"""
    with pytest.raises(ValueError, match="obligatoire"):
        TrajetService().modifier(10, None)


def test_modifier_trajet_inexistant():
    """Le trajet 99 n'existe pas : ValueError et rien n'est modifié"""
    # GIVEN
    service = TrajetService()
    service.trajet_dao.trouver_par_id = MagicMock(return_value=None)
    service.trajet_dao.modifier = MagicMock()

    # WHEN / THEN
    with pytest.raises(ValueError, match="#99 n'existe pas"):
        service.modifier(99, trajet_test)
    service.trajet_dao.modifier.assert_not_called()


def test_modifier_doublon():
    """Un autre trajet part déjà à cette heure sur la ligne : ValueError"""
    # GIVEN
    service = TrajetService()
    service.trajet_dao.trouver_par_id = MagicMock(return_value=trajet_test)
    service._verifier_ligne = MagicMock(return_value=ligne_test)
    service._trajet_similaire_existe = MagicMock(return_value=True)
    service.trajet_dao.modifier = MagicMock()

    # WHEN / THEN
    with pytest.raises(ValueError, match="existe déjà"):
        service.modifier(10, trajet_test)
    service.trajet_dao.modifier.assert_not_called()


# tests supprimer


def test_supprimer_ok():
    """Le trajet 10 existe : True"""
    # GIVEN
    service = TrajetService()
    service.trajet_dao.supprimer = MagicMock(return_value=True)

    # WHEN / THEN
    assert service.supprimer(10) is True
    service.trajet_dao.supprimer.assert_called_once_with(10)


def test_supprimer_inexistant():
    """Le trajet 99 n'existe pas : False"""
    service = TrajetService()
    service.trajet_dao.supprimer = MagicMock(return_value=False)

    assert service.supprimer(99) is False


def test_supprimer_trajet_avec_reservations():
    """La BDD refuse (clé étrangère) : ValueError"""
    service = TrajetService()
    service.trajet_dao.supprimer = MagicMock(side_effect=ForeignKeyViolation)

    with pytest.raises(ValueError, match="a des réservations"):
        service.supprimer(10)


# tests rechercher

gare_rennes = ligne_test.gare_depart
gare_nantes = ligne_test.gare_arrivee


def test_rechercher_ok():
    """Le service renvoie les trajets trouvés par le DAO"""
    # GIVEN
    service = TrajetService()
    service.trajet_dao.rechercher = MagicMock(return_value=[trajet_test])

    # WHEN
    res = service.rechercher(gare_rennes, gare_nantes, heure_depart)

    # THEN
    service.trajet_dao.rechercher.assert_called_once_with(gare_depart=gare_rennes, gare_arrivee=gare_nantes, date=heure_depart)
    assert res == [trajet_test]


@pytest.mark.parametrize(
    "gare_depart, gare_arrivee",
    [
        (None, gare_nantes),
        (gare_rennes, None),
    ]
)
def test_rechercher_gare_manquante(gare_depart, gare_arrivee):
    """Une gare manque : ValueError"""
    with pytest.raises(ValueError, match="obligatoires"):
        TrajetService().rechercher(gare_depart, gare_arrivee, heure_depart)


def test_rechercher_gares_identiques():
    """Départ = arrivée : ValueError"""
    with pytest.raises(ValueError, match="différentes"):
        TrajetService().rechercher(gare_rennes, gare_rennes, heure_depart)


def test_rechercher_date_manquante():
    """Pas de date : ValueError"""
    with pytest.raises(ValueError, match="date"):
        TrajetService().rechercher(gare_rennes, gare_nantes, None)


# tests trouver_par_id


def test_trouver_par_id_ok():
    """Le trajet 10 existe : il est renvoyé"""
    service = TrajetService()
    service.trajet_dao.trouver_par_id = MagicMock(return_value=trajet_test)

    assert service.trouver_par_id(10) is trajet_test
    service.trajet_dao.trouver_par_id.assert_called_once_with(10)


def test_trouver_par_id_introuvable():
    """Le trajet 99 n'existe pas : None"""
    service = TrajetService()
    service.trajet_dao.trouver_par_id = MagicMock(return_value=None)

    assert service.trouver_par_id(99) is None
