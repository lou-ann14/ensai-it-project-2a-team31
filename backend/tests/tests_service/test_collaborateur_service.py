from datetime import datetime
from unittest.mock import patch

import pytest
from src.Classes.classes_objets.gare import Gare
from src.Classes.classes_objets.ligne import Ligne
from src.Classes.classes_objets.train import Train
from src.Classes.classes_service.utilisateurs_service.collaborateur_service import CollaborateurService

# Les services appelés par CollaborateurService sont simulés : aucun appel réel n'est fait.

DEPART = datetime(2027, 6, 1, 8, 0)
RENNES = Gare("Rennes", "Rennes", 87471003, id_gare=1)
NANTES = Gare("Nantes", "Nantes", 87481002, id_gare=2)
SERVICE = "src.Classes.classes_service.utilisateurs_service.collaborateur_service"


# ------------------------------------------------------------- lignes et trajets


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


# --------------------------------------------------------------- gares et trains


def test_service_importer_gares():
    with patch(f"{SERVICE}.GareService") as gare_service:
        gare_service.return_value.importer.return_value = ["Rennes"]
        assert CollaborateurService().importer_gares("Rennes") == ["Rennes"]
    gare_service.return_value.importer.assert_called_once_with("Rennes")


def test_service_creer_train():
    with patch(f"{SERVICE}.TrainService") as train_service:
        CollaborateurService().creer_train("TGV", 100, 300, 8541)
    train_service.return_value.creer.assert_called_once_with("TGV", 100, 300, 8541)


def test_service_modifier_capacite_renvoie_le_train_modifie():
    with patch(f"{SERVICE}.TrainService") as train_service:
        train_service.return_value.trouver_train_par_num.return_value = Train("TGV", 100, 300, 8541, id_train=1)
        train_service.return_value.modifier_capacite.return_value = True

        train = CollaborateurService().modifier_capacite(8541, 120, 280)

    train_service.return_value.modifier_capacite.assert_called_once_with(8541, 120, 280)
    assert (train.places_premieres, train.places_secondes, train.id_train) == (120, 280, 1)


def test_service_modifier_capacite_non_executee():
    with patch(f"{SERVICE}.TrainService") as train_service:
        train_service.return_value.modifier_capacite.return_value = False
        assert CollaborateurService().modifier_capacite(8541, 120, 280) is None
