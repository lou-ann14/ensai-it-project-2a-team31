from datetime import datetime

from pydantic import BaseModel, ConfigDict
from src.schema.administrateur_schema import UtilisateurReponseModel


class DetailPrixModel(BaseModel):
    """Tarification transparente (F5) : décomposition du prix d'une place, en euros.
    prix_total = cout_exploitation + peage_reseau + marge + tva."""

    prix_total: float
    cout_exploitation: float
    peage_reseau: float
    marge: float
    tva: float


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
    # F5 : places restantes par classe (None si non calculées ou si le trajet n'a pas de train)
    places_restantes_premiere: int | None = None
    places_restantes_seconde: int | None = None
    # F5 : tarification transparente (renseignée dans les résultats de recherche)
    detail_prix_premiere: DetailPrixModel | None = None
    detail_prix_seconde: DetailPrixModel | None = None


class PlacesLibresModel(BaseModel):
    """Places encore libres sur un trajet, classe par classe (numéros de 1 à la capacité)."""

    id_trajet: int
    capacite_premiere: int
    capacite_seconde: int
    libres_premiere: list[int]
    libres_seconde: list[int]


class CompteCreationModel(BaseModel):
    """Données envoyées par une personne pour créer son propre compte.
    Pas de rôle : un compte créé par l'utilisateur est toujours un compte CLIENT.
    Pas d'id : il est généré par la base (SERIAL)."""

    nom_utilisateur: str
    mdp: str


class MotDePasseModificationModel(BaseModel):
    """Données envoyées par un utilisateur connecté pour changer son mot de passe.
    Pas d'id : l'utilisateur est celui du token d'authentification."""

    ancien_mdp: str
    nouveau_mdp: str


class ReservationCreationModel(BaseModel):
    """Données envoyées par un client pour réserver une place sur un trajet.
    Pas d'id_client : le client est celui du token d'authentification.
    place est optionnelle : si elle est absente ou vide, la première place libre
    de la classe est attribuée automatiquement."""

    id_trajet: int
    place: str | None = None
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
