from unittest.mock import MagicMock, patch

import pytest
from src.Classes.classes_DAO.reservation_DAO import ReservationDAO
from src.Classes.classes_objets.reservation import Reservation

# données préenregistrées (équivalent d'une bdd)

# identifiants des clients et des trajets utilisés dans les réservations
id_client_fan2train = 1
id_client_groupeprojetinfo = 2
id_client_sans_reservation = 3

id_trajet_toulouse_paris = 10
id_trajet_paris_rennes = 11
id_trajet_paris_lyon = 12

# réservations : dicts, car c'est ce que renvoie le curseur
reservation_fan2train_toulouse_paris = {
    "id_reservation": 1,
    "id_client": 1,
    "id_trajet": 10,
    "place": "12A",
    "classe": 2,
    "prix": 45.0,
}
reservation_fan2train_paris_rennes = {
    "id_reservation": 2,
    "id_client": 1,
    "id_trajet": 11,
    "place": "3B",
    "classe": 1,
    "prix": 80.0,
}
reservation_groupeprojetinfo_toulouse_paris = {
    "id_reservation": 3,
    "id_client": 2,
    "id_trajet": 10,
    "place": "12B",
    "classe": 2,
    "prix": 45.0,
}
reservation_groupeprojetinfo_paris_lyon = {
    "id_reservation": 4,
    "id_client": 2,
    "id_trajet": 12,
    "place": "7C",
    "classe": 2,
    "prix": 30.5,
}

reservations_bdd = [
    reservation_fan2train_toulouse_paris,
    reservation_fan2train_paris_rennes,
    reservation_groupeprojetinfo_toulouse_paris,
    reservation_groupeprojetinfo_paris_lyon,
]

# réservations d'un client donné (ce que renverrait trouver_par_client)
reservations_fan2train = [reservation_fan2train_toulouse_paris, reservation_fan2train_paris_rennes]
reservations_groupeprojetinfo = [
    reservation_groupeprojetinfo_toulouse_paris,
    reservation_groupeprojetinfo_paris_lyon
    ]

# nouvelle réservation à insérer avec creer (pas encore d'id_reservation)
# MagicMock fait en sorte que le DAO lit reservation.id_client / reservation.id_trajet,
# attributs que la classe Reservation n'a pas pour l'instant
nouvelle_reservation = MagicMock(
    id_reservation=None,
    id_client=3,
    id_trajet=12,
    place="1A",
    classe=1,
    prix=60.0,
)
