from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from src.Classes.controller import collaborateur_controller, utilisateur_controller
from src.Classes.controller.utilisateur_controller import trouver_gare
from src.utils.securite import verif_token

# Les services sont simulés : ni la base ni l'API SNCF ne sont appelées.


def gare(nom, id_gare, ville="Ville"):
    # "nom" est affecté à part : MagicMock(name=...) a un sens spécial, autant rester explicite
    objet = MagicMock(id_gare=id_gare, ville=ville)
    objet.nom = nom
    return objet


RENNES = gare("Rennes", 1)
BEAULIEU = gare("Rennes Beaulieu Chimie", 2)
NANTES = gare("Nantes", 5)
COLLAB = MagicMock(grade="COLLABORATEUR", id=2)  # collaborateur connecté (token)


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
    """Le nom exact l'emporte (casse et espaces ignorés) : Rennes et pas Rennes Beaulieu"""
    assert trouver_gare(nom, service_gares()) is RENNES


def test_debut_de_nom_unique():
    """Un début de nom qui ne correspond qu'à une gare suffit"""
    assert trouver_gare("Nan", service_gares()) is NANTES


def test_plusieurs_gares_correspondent():
    """Début de nom ambigu : 400, avec la liste des gares possibles"""
    with pytest.raises(HTTPException) as erreur:
        trouver_gare("Ren", service_gares())
    assert erreur.value.status_code == 400
    assert "Rennes (Ville)" in erreur.value.detail
    assert "Rennes Beaulieu Chimie" in erreur.value.detail


def test_meme_nom_exact_dans_deux_villes():
    """Même nom dans deux villes : 400, la ville est indiquée pour choisir"""
    service = MagicMock()
    service.rechercher.return_value = [gare("Centre", 1, "Lyon"), gare("Centre", 2, "Metz")]
    with pytest.raises(HTTPException) as erreur:
        trouver_gare("Centre", service)
    assert erreur.value.status_code == 400
    assert "Centre (Lyon)" in erreur.value.detail


def test_gare_inconnue():
    """Aucune gare ne correspond : 404"""
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
    """La recherche de trajets accepte des noms de gares"""
    trajets = MagicMock()
    jour = date(2026, 11, 18)

    utilisateur_controller.rechercher_trajets("Rennes", "Nantes", jour, trajets, service_gares(), MagicMock())

    trajets.rechercher.assert_called_once_with(RENNES, NANTES, jour)


def test_rechercher_trajets_sans_date():
    """La date est facultative dans l'URL : la route transmet None au service"""
    trajets = MagicMock()
    trajets.rechercher.return_value = []
    app = FastAPI()
    app.include_router(utilisateur_controller.router)
    app.dependency_overrides[utilisateur_controller.get_trajet_service] = lambda: trajets
    app.dependency_overrides[utilisateur_controller.get_gare_service] = service_gares
    app.dependency_overrides[verif_token] = lambda: MagicMock()

    reponse = TestClient(app).get("/trajets", params={"gare_depart": "Rennes", "gare_arrivee": "Nantes"})

    assert reponse.status_code == 200
    trajets.rechercher.assert_called_once_with(RENNES, NANTES, None)


def test_rechercher_trajets_gare_inconnue():
    """Gare inconnue : 404, sans lancer la recherche"""
    trajets = MagicMock()
    with pytest.raises(HTTPException) as erreur:
        utilisateur_controller.rechercher_trajets(
            "Zzz", "Nantes", date(2026, 11, 18), trajets, service_gares(), MagicMock()
        )
    assert erreur.value.status_code == 404
    trajets.rechercher.assert_not_called()


def test_creer_ligne_par_nom():
    """La ligne est créée à partir des noms des gares"""
    service = MagicMock()
    service.creer_ligne.return_value.id_ligne = 7

    reponse = collaborateur_controller.creer_ligne("Rennes", "Nantes", service, service_gares(), COLLAB)

    service.creer_ligne.assert_called_once_with(1, 5, 2)
    assert reponse["id_ligne"] == 7


def test_creer_ligne_rattachee_au_collaborateur_du_token():
    """L'id du collaborateur vient du token, jamais d'un paramètre de la requête"""
    service = MagicMock()
    service.creer_ligne.return_value.id_ligne = 7

    collaborateur_controller.creer_ligne(
        "Rennes", "Nantes", service, service_gares(), MagicMock(grade="COLLABORATEUR", id=42)
    )

    assert service.creer_ligne.call_args.args[2] == 42


def test_modifier_ligne_par_nom():
    """La ligne est modifiée à partir des noms des gares"""
    service = MagicMock()

    collaborateur_controller.modifier_ligne(9, "Nantes", "Rennes", service, service_gares(), COLLAB)

    service.modifier_ligne.assert_called_once_with(9, 5, 1)


def test_creer_ligne_gare_ambigue():
    """Gare ambiguë : 400, et la ligne n'est pas créée"""
    service = MagicMock()
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.creer_ligne("Ren", "Nantes", service, service_gares(), COLLAB)
    assert erreur.value.status_code == 400
    service.creer_ligne.assert_not_called()


def test_creer_ligne_sans_le_grade_collaborateur():
    """Compte client : 403, avant même de chercher les gares"""
    service = MagicMock()
    gares = service_gares()
    with pytest.raises(HTTPException) as erreur:
        collaborateur_controller.creer_ligne("Rennes", "Nantes", service, gares, MagicMock(grade="CLIENT"))
    assert erreur.value.status_code == 403
    gares.rechercher.assert_not_called()
    service.creer_ligne.assert_not_called()



def test_creer_ligne_par_un_administrateur():
    """Hiérarchie des grades : un administrateur peut faire tout ce que fait un collaborateur"""
    service = MagicMock()
    service.creer_ligne.return_value.id_ligne = 7

    reponse = collaborateur_controller.creer_ligne(
        "Rennes", "Nantes", service, service_gares(), MagicMock(grade="ADMIN", id=1)
    )

    assert reponse["id_ligne"] == 7
    assert service.creer_ligne.call_args.args[2] == 1  # la ligne est rattachée à l'administrateur
