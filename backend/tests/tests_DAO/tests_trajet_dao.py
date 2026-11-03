from datetime import datetime

from src.Classes.classes_DAO.ligne_DAO import LigneDAO
from src.Classes.classes_DAO.train_DAO import TrainDAO
from src.Classes.classes_DAO.trajet_DAO import TrajetDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.trajet import Trajet

paris = Gare(2, "Paris Montparnasse", "Paris")
rennes = Gare(3, "Rennes", "Rennes")


def _nouveau_trajet() -> Trajet:
    """Construit un trajet (non enregistré) sur la ligne et le train de test_bdd.sql"""
    return Trajet(
        id_trajet=None,
        heure_depart=datetime(2026, 12, 2, 8, 0),
        heure_arrivee=datetime(2026, 12, 2, 10, 0),
        ligne=LigneDAO().trouver_par_id(1),
        train=TrainDAO().trouver_par_id(1),
        tarif_base=39.0,
    )


# tests trouver_par_id


def test_trouver_par_id_ok():
    """Retrouve le trajet de test_bdd.sql avec ses objets Ligne et Train"""
    # WHEN
    trajet = TrajetDAO().trouver_par_id(1)

    # THEN
    assert trajet is not None
    assert trajet.tarif_base == 45.0
    assert trajet.heure_depart == datetime(2026, 12, 1, 10, 0)
    assert trajet.ligne.gare_depart.nom == "Paris Montparnasse"
    assert trajet.train.type_train == "TGV"


def test_trouver_par_id_inexistant():
    """Un id inconnu renvoie None"""
    assert TrajetDAO().trouver_par_id(999) is None


# tests creer


def test_creer_ok():
    """Crée un trajet : son id est renseigné et on peut le relire"""
    # WHEN
    cree = TrajetDAO().creer(_nouveau_trajet())

    # THEN
    assert cree.id_trajet is not None
    relu = TrajetDAO().trouver_par_id(cree.id_trajet)
    assert relu.tarif_base == 39.0
    assert relu.ligne.id_ligne == 1
    assert relu.train.id_train == 1


# tests modifier


def test_modifier_ok():
    """Modifie le tarif d'un trajet existant"""
    # GIVEN
    trajet = TrajetDAO().trouver_par_id(1)
    trajet.tarif_base = 60.0

    # WHEN
    res = TrajetDAO().modifier(trajet)

    # THEN
    assert res is True
    assert TrajetDAO().trouver_par_id(1).tarif_base == 60.0


def test_modifier_inexistant():
    """Modifier un trajet qui n'existe pas renvoie False"""
    # GIVEN
    trajet = _nouveau_trajet()
    trajet.id_trajet = 999

    # WHEN / THEN
    assert TrajetDAO().modifier(trajet) is False


# tests supprimer


def test_supprimer_ok():
    """Supprime un trajet existant"""
    # WHEN
    res = TrajetDAO().supprimer(1)

    # THEN
    assert res is True
    assert TrajetDAO().trouver_par_id(1) is None


def test_supprimer_inexistant():
    """Supprimer un trajet qui n'existe pas renvoie False"""
    assert TrajetDAO().supprimer(999) is False


# tests rechercher


def test_rechercher_ok():
    """Trouve le trajet Paris -> Rennes du 01/12/2026"""
    # WHEN
    trajets = TrajetDAO().rechercher(paris, rennes, datetime(2026, 12, 1))

    # THEN
    assert len(trajets) == 1
    assert trajets[0].id_trajet == 1
    assert trajets[0].train.type_train == "TGV"
    assert trajets[0].ligne.gare_arrivee.nom == "Rennes"


def test_rechercher_autre_date():
    """Aucun trajet ce jour-là : liste vide"""
    assert TrajetDAO().rechercher(paris, rennes, datetime(2026, 12, 5)) == []


def test_rechercher_sens_inverse():
    """Aucun trajet Rennes -> Paris : liste vide"""
    assert TrajetDAO().rechercher(rennes, paris, datetime(2026, 12, 1)) == []