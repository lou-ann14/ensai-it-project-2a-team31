from src.Classes.classes_DAO.ligne_DAO import LigneDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne

# Gares de test_bdd.sql : 2 = Paris Montparnasse, 3 = Rennes
paris = Gare(2, "Paris Montparnasse", "Paris")
rennes = Gare(3, "Rennes", "Rennes")


def test_trouver_par_id_ok():
    """Retrouve la ligne de test_bdd.sql avec ses deux objets Gare"""
    # WHEN
    ligne = LigneDAO().trouver_par_id(1)

    # THEN
    assert ligne is not None
    assert ligne.gare_depart.nom == "Paris Montparnasse"
    assert ligne.gare_arrivee.nom == "Rennes"


def test_trouver_par_id_inexistant():
    """Un id inconnu renvoie None"""
    assert LigneDAO().trouver_par_id(999) is None


def test_rechercher_ok():
    """Retrouve la ligne Paris -> Rennes"""
    # WHEN
    ligne = LigneDAO().rechercher(paris, rennes)

    # THEN
    assert ligne is not None
    assert ligne.id_ligne == 1


def test_rechercher_sens_inverse():
    """Rennes -> Paris n'existe pas : l'ordre départ/arrivée compte"""
    assert LigneDAO().rechercher(rennes, paris) is None


def test_creer_ok():
    """Crée la ligne Rennes -> Paris : son id est renseigné et on peut la relire"""
    # WHEN
    cree = LigneDAO().creer(Ligne(None, rennes, paris))

    # THEN
    assert cree.id_ligne is not None
    relue = LigneDAO().trouver_par_id(cree.id_ligne)
    assert relue.gare_depart.id_gare == 3
    assert relue.gare_arrivee.id_gare == 2