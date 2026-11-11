from datetime import datetime

from pydantic import BaseModel, ConfigDict
from src.schema.administrateur_schema import UtilisateurReponseModel


class TrajetReponseModel(BaseModel):
    """Trajet renvoyé par l'API."""

    # Permet de construire le modèle directement depuis un objet Trajet
    model_config = ConfigDict(from_attributes=True)

    id_trajet: int
    heure_depart: datetime
    heure_arrivee: datetime
    temps_trajet: int | None = None  # en minutes
    tarif_base: float
    nom_gare_depart: str | None = None
    nom_gare_arrivee: str | None = None
    num_train: int | None = None


class CompteCreationModel(BaseModel):
    """Données envoyées par une personne pour créer son propre compte.
    Pas de rôle : un compte créé par l'utilisateur est toujours un compte CLIENT.
    Pas d'id : il est généré par la base (SERIAL)."""

    nom_utilisateur: str
    mdp: str


class ReservationCreationModel(BaseModel):
    """Données envoyées par un client pour réserver une place sur un trajet."""

    id_client: int
    id_trajet: int
    place: str
    classe: int  # 1 = première classe, 2 = seconde classe


class ReservationReponseModel(BaseModel):
    """Réservation renvoyée par l'API."""

    # Permet de construire le modèle directement depuis un objet Reservation
    model_config = ConfigDict(from_attributes=True)

    id_reservation: int
    client: UtilisateurReponseModel
    trajet: TrajetReponseModel
    place: str
    classe: int
    prix: float
