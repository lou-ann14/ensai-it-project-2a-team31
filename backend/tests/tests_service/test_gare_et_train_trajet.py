from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_service.trajet_service import TrajetService, train_depuis_id
from src.Classes.classes_service.utilisateurs_service.collaborateur_service import CollaborateurService

# La base et l'API SNCF sont simulées : aucun appel réel n'est fait.

SERVICE = "src.Classes.classes_service.trajet_service"
COLLAB = "src.Classes.classes_service.utilisateurs_service.collaborateur_service"
DEPART = datetime(2026, 11, 18, 8, 35)
LIGNE = Ligne(
    Gare("Rennes", "Rennes", "stop_area:SNCF:87471003", 1),
    Gare("Nantes", "Nantes", "stop_area:SNCF:87481002", 5),
    id_ligne=1,
)

# ------------------------------------------------------------------- Gare


def test_gare_importee_depuis_l_api_sans_id():
    """Cas de GareService.importer : l'id SNCF est du texte et la gare n'a pas encore d'id."""
    gare = Gare("Rennes", "Rennes", "stop_area:SNCF:87471003", None)
    assert gare.id_sncf == "stop_area:SNCF:87471003"
    assert gare.id_gare is None


def test_gare_lue_en_base():
    gare = Gare(id_gare=1, nom="Rennes", ville="Rennes", id_sncf="stop_area:SNCF:87471003")
    assert gare.id_gare == 1


def test_gare_sans_id_sncf():
    assert Gare("Rennes", "Rennes").id_sncf is None


@pytest.mark.parametrize(
    "parametres, message",
    [
        ({"nom": None}, "Le nom doit être une chaîne de caractères."),
        ({"ville": 42}, "La ville doit être une chaîne de caractères."),
        ({"id_sncf": 87471003}, "L'identifiant SNCF doit être une chaîne de caractères."),
        ({"id_gare": "1"}, "L'identifiant de la gare doit être un entier."),
    ],
)
def test_gare_donnee_invalide(parametres, message):
    donnees = {"nom": "Rennes", "ville": "Rennes", "id_sncf": "a", "id_gare": 1, **parametres}
    with pytest.raises(TypeError, match=message):
        Gare(**donnees)


# ----------------------------------------------------------------- Trajets


@pytest.fixture
def service():
    with patch(f"{SERVICE}.TrajetDAO") as trajet_dao, patch(f"{SERVICE}.LigneDAO") as ligne_dao, patch(
        f"{SERVICE}.SncfClient"
    ) as sncf:
        ligne_dao.return_value.trouver_par_id.return_value = LIGNE
        trajet_dao.return_value.rechercher.return_value = []
        trajet_dao.return_value.creer.side_effect = lambda trajet: trajet
        sncf.return_value.duree_trajet.return_value = 4620
        yield TrajetService()


def test_train_depuis_id():
    assert train_depuis_id(3).id_train == 3


@pytest.mark.parametrize("tarif", [40, 40.0])
def test_creer_trajet_garde_l_id_du_train(service, tarif):
    """Un tarif entier est accepté : Trajet exige un float."""
    trajet = service.creer(1, 3, DEPART, tarif)

    assert trajet.train.id_train == 3
    assert trajet.tarif_base == 40.0
    assert trajet.temps_trajet == 77


def test_modifier_trajet_garde_l_id_du_train():
    with patch(f"{COLLAB}.TrajetService") as trajet_service, patch(f"{COLLAB}.LigneService") as ligne_service:
        trajet_service.return_value.modifier.return_value = True
        ligne_service.return_value.trouver_par_id.return_value = LIGNE

        trajet = CollaborateurService().modifier_trajet(9, 1, 3, DEPART, 55.0)

    assert trajet.train.id_train == 3
    assert trajet.id_trajet == 9
    assert trajet_service.return_value.modifier.call_args.args[0] == 9
