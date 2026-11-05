from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi import HTTPException
from psycopg2.errors import ForeignKeyViolation
from src.Classes.classes_DAO.ligne_DAO import LigneDAO
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_service.ligne_service import LigneService
from src.Classes.classes_service.utilisateurs_service.collaborateur_service import CollaborateurService
from src.Classes.controller import collaborateur_controller as controller
from src.schema.collaborateur_schema import TrajetModificationModel

# La base et l'API SNCF sont simulées : aucun appel réel n'est fait.

DEPART = datetime(2027, 6, 1, 8, 0)
RENNES = Gare("Rennes", "Rennes", "a", id_gare=1)
NANTES = Gare("Nantes", "Nantes", "b", id_gare=2)
SERVICE = "src.Classes.classes_service.utilisateurs_service.collaborateur_service"
COLLAB = MagicMock(grade="COLLABORATEUR")  # remplace l'utilisateur fourni par verif_token
CLIENT = MagicMock(grade="CLIENT")
TRAJET = TrajetModificationModel(id_ligne=1, id_train=1, heure_depart=DEPART, tarif_base=40)


def service_gares():
    """Simule GareService.rechercher : les routes de lignes reçoivent des noms de gares."""
    service = MagicMock()
    service.rechercher.side_effect = lambda nom, ville: {"Rennes": [RENNES], "Nantes": [NANTES]}.get(nom, [])
    return service


# ------------------------------------------------------------------ LigneDAO


@pytest.fixture
def curseur():
    curseur = MagicMock()
    with patch("src.Classes.classes_DAO.ligne_DAO.DBConnexion") as mock_db:
        connexion = mock_db.return_value.connexion.__enter__.return_value
        connexion.cursor.return_value.__enter__.return_value = curseur
        yield curseur


def test_dao_modifier(curseur):
    curseur.rowcount = 1
    assert LigneDAO().modifier(Ligne(RENNES, NANTES, id_ligne=7)) is True
    requete, parametres = curseur.execute.call_args.args
    assert "UPDATE lignes" in requete
    assert parametres == {"id_gare_depart": 1, "id_gare_arrivee": 2, "id_ligne": 7}


def test_dao_supprimer(curseur):
    curseur.rowcount = 0
    assert LigneDAO().supprimer(99) is False
    assert "DELETE FROM lignes" in curseur.execute.call_args.args[0]


def test_dao_a_des_trajets(curseur):
    curseur.fetchone.return_value = {"existe": True}
    assert LigneDAO().a_des_trajets(1) is True


# -------------------------------------------------------------- LigneService


@pytest.fixture
def ligne_dao():
    with patch("src.Classes.classes_service.ligne_service.LigneDAO") as dao:
        dao.return_value.rechercher.return_value = None
        dao.return_value.a_des_trajets.return_value = False
        dao.return_value.modifier.return_value = True
        yield dao.return_value


def test_modifier_ok(ligne_dao):
    assert LigneService().modifier(Ligne(RENNES, NANTES, id_ligne=1)) is True


def test_modifier_memes_gares_sur_la_meme_ligne_accepte(ligne_dao):
    """Retrouver sa propre ligne n'est pas un doublon"""
    ligne_dao.rechercher.return_value = Ligne(RENNES, NANTES, id_ligne=1)
    assert LigneService().modifier(Ligne(RENNES, NANTES, id_ligne=1)) is True


def test_modifier_doublon(ligne_dao):
    ligne_dao.rechercher.return_value = Ligne(RENNES, NANTES, id_ligne=2)
    with pytest.raises(ValueError, match="existe déjà"):
        LigneService().modifier(Ligne(RENNES, NANTES, id_ligne=1))
    ligne_dao.modifier.assert_not_called()


def test_modifier_gares_identiques(ligne_dao):
    with pytest.raises(ValueError, match="différentes"):
        LigneService().modifier(Ligne(RENNES, RENNES, id_ligne=1))


def test_modifier_ligne_avec_trajets(ligne_dao):
    ligne_dao.a_des_trajets.return_value = True
    with pytest.raises(ValueError, match="a des trajets"):
        LigneService().modifier(Ligne(RENNES, NANTES, id_ligne=1))
    ligne_dao.modifier.assert_not_called()


def test_supprimer_ligne_avec_trajets(ligne_dao):
    ligne_dao.supprimer.side_effect = ForeignKeyViolation()
    with pytest.raises(ValueError, match="a des trajets"):
        LigneService().supprimer(1)


# ------------------------------------------------------ CollaborateurService


def test_service_modifier_ligne_inexistante():
    with patch(f"{SERVICE}.LigneService") as ligne_service, patch(f"{SERVICE}.GareDAO") as gare_dao:
        ligne_service.return_value.trouver_par_id.return_value = None
        assert CollaborateurService().modifier_ligne(99, 1, 2) is None
        gare_dao.return_value.trouver_par_id.assert_not_called()


def test_service_modifier_ligne_gare_inconnue():
    with patch(f"{SERVICE}.LigneService"), patch(f"{SERVICE}.GareDAO") as gare_dao:
        gare_dao.return_value.trouver_par_id.return_value = None
        with pytest.raises(ValueError, match="n'existe pas"):
            CollaborateurService().modifier_ligne(1, 98, 99)


def test_service_modifier_trajet_inexistant():
    with patch(f"{SERVICE}.TrajetService") as trajet_service:
        trajet_service.return_value.trouver_par_id.return_value = None
        assert CollaborateurService().modifier_trajet(99, 1, 1, DEPART, 40.0) is None
        trajet_service.return_value.modifier.assert_not_called()


def test_service_modifier_trajet_ligne_inconnue():
    with patch(f"{SERVICE}.TrajetService"), patch(f"{SERVICE}.LigneService") as ligne_service:
        ligne_service.return_value.trouver_par_id.return_value = None
        with pytest.raises(ValueError, match="ligne #99"):
            CollaborateurService().modifier_trajet(1, 99, 1, DEPART, 40.0)


def test_service_modifier_trajet_transmet_les_objets():
    with patch(f"{SERVICE}.TrajetService") as trajet_service, patch(f"{SERVICE}.LigneService") as ligne_service:
        ligne = Ligne(RENNES, NANTES, id_ligne=3)
        ligne_service.return_value.trouver_par_id.return_value = ligne
        trajet_service.return_value.modifier.return_value = True

        trajet = CollaborateurService().modifier_trajet(1, 3, 5, DEPART, 40.0)

        assert trajet.ligne is ligne
        assert trajet.train.id_train == 5
        assert trajet.id_trajet == 1
        trajet_service.return_value.modifier.assert_called_once_with(1, trajet)


# ---------------------------------------------------------------- Controller


@pytest.mark.parametrize(
    "appel, methode, resultat",
    [
        (lambda s: controller.modifier_ligne(9, "Rennes", "Nantes", s, service_gares(), COLLAB), "modifier_ligne", None),
        (lambda s: controller.supprimer_ligne(9, s, COLLAB), "supprimer_ligne", False),
        (lambda s: controller.modifier_trajet(9, TRAJET, s, COLLAB), "modifier_trajet", None),
        (lambda s: controller.supprimer_trajet(9, s, COLLAB), "supprimer_trajet", False),
    ],
)
def test_route_introuvable_renvoie_404(appel, methode, resultat):
    service = MagicMock()
    getattr(service, methode).return_value = resultat
    with pytest.raises(HTTPException) as erreur:
        appel(service)
    assert erreur.value.status_code == 404


def test_route_supprimer_refus_renvoie_400():
    service = MagicMock()
    service.supprimer_trajet.side_effect = ValueError("Impossible de supprimer un trajet qui a des réservations.")
    with pytest.raises(HTTPException) as erreur:
        controller.supprimer_trajet(1, service, COLLAB)
    assert erreur.value.status_code == 400


def test_route_modifier_trajet_api_indisponible_renvoie_502():
    service = MagicMock()
    service.modifier_trajet.side_effect = requests.ConnectionError()
    with pytest.raises(HTTPException) as erreur:
        controller.modifier_trajet(1, TRAJET, service, COLLAB)
    assert erreur.value.status_code == 502


def test_route_modifier_ligne_transmet_les_id_des_gares():
    service = MagicMock()

    controller.modifier_ligne(9, "Rennes", "Nantes", service, service_gares(), COLLAB)

    service.modifier_ligne.assert_called_once_with(9, 1, 2)


@pytest.mark.parametrize(
    "appel",
    [
        lambda s: controller.modifier_ligne(9, "Rennes", "Nantes", s, service_gares(), CLIENT),
        lambda s: controller.supprimer_ligne(9, s, CLIENT),
        lambda s: controller.modifier_trajet(9, TRAJET, s, CLIENT),
        lambda s: controller.supprimer_trajet(9, s, CLIENT),
    ],
)
def test_route_refusee_sans_le_grade_collaborateur(appel):
    service = MagicMock()
    with pytest.raises(HTTPException) as erreur:
        appel(service)
    assert erreur.value.status_code == 401
    assert service.mock_calls == []
