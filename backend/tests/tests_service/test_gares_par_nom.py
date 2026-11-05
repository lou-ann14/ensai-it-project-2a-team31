from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from src.Classes.controller import collaborateur_controller, utilisateur_controller
from src.Classes.controller.utilisateur_controller import trouver_gare

# Les services sont simulés : ni la base ni l'API SNCF ne sont appelées.


def gare(nom, id_gare, ville="Ville"):
    # "nom" est affecté à part : MagicMock(name=...) a un sens spécial, autant rester explicite
    objet = MagicMock(id_gare=id_gare, ville=ville)
    objet.nom = nom
    return objet


RENNES = gare("Rennes", 1)
BEAULIEU = gare("Rennes Beaulieu Chimie", 2)
NANTES = gare("Nantes", 5)
COLLAB = MagicMock(grade="COLLABORATEUR")


def service_gares():
    """Simule la recherche par début de nom, comme GareService.rechercher."""
    gares = [NANTES, RENNES, BEAULIEU]
    service = MagicMock()
    service.rechercher.side_effect = lambda nom, ville: [
        g for g in gares if g.nom.casefold().startswith(nom.casefold())
    ]
    return service


# ------------------------------------------------------------- trouver_gare


@pytest.mark.parametrize("nom", ["Rennes", "rennes", "  RENNES  "])
def test_nom_exact_prioritaire(nom):
    assert trouver_gare(nom, service_gares()) is RENNES


def test_debut_de_nom_unique():
    assert trouver_gare("Nan", service_gares()) is NANTES


def test_plusieurs_gares_correspondent():
    with pytest.raises(HTTPException) as erreur:
        trouver_gare("Ren", service_gares())
    assert erreur.value.status_code == 400
    assert "Rennes (Ville)" in erreur.value.detail
    assert "Rennes Beaulieu Chimie" in erreur.value.detail


def test_meme_nom_exact_dans_deux_villes():
    service = MagicMock()
    service.rechercher.return_value = [gare("Centre", 1, "Lyon"), gare("Centre", 2, "Metz")]
    with pytest.raises(HTTPException) as erreur:
        trouver_gare("Centre", service)
    assert erreur.value.status_code == 400
    assert "Centre (Lyon)" in erreur.value.detail


def test_gare_inconnue():
    with pytest.raises(HTTPException) as erreur:
        trouver_gare("Zzz", service_gares())
    assert erreur.value.status_code == 404


@pytest.mark.parametrize("nom", ["", "   "])
def test_nom_vide_ne_lance_pas_la_recherche(nom):
    """Sans critère, GareService.rechercher renverrait toutes les gares."""
    service = service_gares()
    with pytest.raises(HTTPException) as erreur:
        trouver_gare(nom, service)
    assert erreur.value.status_code == 400
    service.rechercher.assert_not_called()


# ------------------------------------------------------------------- routes


def test_rechercher_trajets_par_nom():
    trajets = MagicMock()
    jour = date(2026, 11, 18)

    utilisateur_controller.rechercher_trajets("Rennes", "Nantes", jour, trajets, service_gares(), MagicMock())

    trajets.rechercher.assert_called_once_with(RENNES, NANTES, jour)


def test_rechercher_trajets_gare_inconnue():
    trajets = MagicMock()
    with pytest.raises(HTTPException) as erreur:
        utilisateur_controller.rechercher_trajets(
            "Zzz", "Nantes", date(2026, 11, 18), trajets, service_gares(), MagicMock()
        )
    assert erreur.value.status_code == 404
    trajets.rechercher.assert_not_called()


def test_creer_ligne_par_nom():
    service = MagicMock()
    service.creer_ligne.return_value.id_ligne = 7

    reponse = collaborateur_controller.creer_ligne("Rennes", "Nantes", 2, service, service_gares(), COLLAB)

    service.creer_ligne.assert_called_once_with(1, 5, 2)
    assert reponse["id_ligne"] == 7


def test_modifier_ligne_par_nom():
    service = MagicMock()

    collaborateur_controller.modifier_ligne(9, "Nantes", "Rennes", service, service_gares(), COLLAB)

    service.modifier_ligne.assert_called_once_with(9, 5, 1)


def test_creer_ligne_gare_ambigue():
    service = MagicMock()
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.creer_ligne("Ren", "Nantes", 2, service, service_gares(), COLLAB)
    assert erreur.value.status_code == 400
    service.creer_ligne.assert_not_called()


def test_creer_ligne_sans_le_grade_collaborateur():
    service = MagicMock()
    gares = service_gares()
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.creer_ligne("Rennes", "Nantes", 2, service, gares, MagicMock(grade="CLIENT"))
    assert erreur.value.status_code == 401
    gares.rechercher.assert_not_called()
    service.creer_ligne.assert_not_called()
