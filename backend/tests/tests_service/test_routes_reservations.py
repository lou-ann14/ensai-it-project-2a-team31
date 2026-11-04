from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from src.Classes.classes_objets.utilisateurs.utilisateur import Utilisateur
from src.Classes.controller import utilisateur_controller as controller

# La base est simulée : aucun appel réel n'est fait.

UTILISATEUR_DAO = "src.Classes.controller.utilisateur_controller.UtilisateurDAO"
CLIENT_BDD = Utilisateur("x", "client", "CLIENT", id=1)
COLLABORATEUR_BDD = Utilisateur("x", "collab", "COLLABORATEUR", id=2)


@pytest.fixture
def dao():
    with patch(UTILISATEUR_DAO) as utilisateur_dao:
        utilisateur_dao.return_value.trouver_par_id.return_value = CLIENT_BDD
        yield utilisateur_dao.return_value


def test_historique_ok(dao):
    service = MagicMock()
    service.voir_historique_reservations.return_value = ["une réservation"]

    assert controller.voir_historique_reservations(1, service) == ["une réservation"]
    assert service.voir_historique_reservations.call_args.args[0].id == 1


def test_historique_client_inconnu(dao):
    dao.trouver_par_id.return_value = None
    service = MagicMock()

    with pytest.raises(HTTPException) as erreur:
        controller.voir_historique_reservations(99, service)

    assert erreur.value.status_code == 404
    service.voir_historique_reservations.assert_not_called()


def test_historique_compte_non_client(dao):
    dao.trouver_par_id.return_value = COLLABORATEUR_BDD

    with pytest.raises(HTTPException) as erreur:
        controller.voir_historique_reservations(2, MagicMock())

    assert erreur.value.status_code == 400


def test_annuler_ok(dao):
    service = MagicMock()
    service.annuler_reservation.return_value = True

    assert controller.annuler_reservation(7, 1, service) == {"message": "Annulation de la réservation réussie"}
    client, id_reservation = service.annuler_reservation.call_args.args
    assert client.id == 1
    assert id_reservation == 7


def test_annuler_reservation_inexistante(dao):
    service = MagicMock()
    service.annuler_reservation.return_value = False

    with pytest.raises(HTTPException) as erreur:
        controller.annuler_reservation(99, 1, service)

    assert erreur.value.status_code == 404


def test_annuler_refusee(dao):
    service = MagicMock()
    service.annuler_reservation.side_effect = ValueError("Cette réservation appartient à un autre client.")

    with pytest.raises(HTTPException) as erreur:
        controller.annuler_reservation(7, 1, service)

    assert erreur.value.status_code == 400
    assert "autre client" in erreur.value.detail
